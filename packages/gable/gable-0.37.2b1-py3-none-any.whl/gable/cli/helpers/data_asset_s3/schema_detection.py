"""
schema_detection.py
===================
Robust S3 schema inference with DuckDB/Arrow.
 • Zero pandas
 • Wrapper/format detection by magic-bytes
 • Decompress only when DuckDB cannot stream the file as-is
"""

from __future__ import annotations
import io, os, tempfile, urllib.parse
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

import boto3, duckdb, fastavro, pyarrow as pa
from loguru import logger

from gable.cli.helpers.data_asset_s3.compression_handler import CompressionHandler
from gable.cli.helpers.data_asset_s3.native_s3_converter  import NativeS3Converter, merge_schemas
from gable.cli.helpers.data_asset_s3.schema_profiler       import (
    get_data_asset_field_profiles_for_data_asset,
)
from gable.openapi import S3SamplingParameters, DataAssetFieldsToProfilesMapping

duckdb.query("INSTALL httpfs; LOAD httpfs;")
# duckdb.query("INSTALL orc;   LOAD orc;")  # load ORC extension only if used

# ───────────────────────── dataclasses ─────────────────────────
@dataclass
class S3DetectionResult:
    schema: dict
    data_asset_fields_to_profiles_map: Optional[DataAssetFieldsToProfilesMapping] = None


# ───────────────────────── helper: sniff 64 KB ─────────────────────────
def _sniff_wrapper_and_format(
    handler: CompressionHandler, key: str, head: bytes
) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (.wrapper, .format) as lowercase extensions *with dot*,
    e.g. ('.gz', '.csv') or (None, '.parquet')
    """
    real_fmt  = handler.get_original_format(key, head)            # '.csv' | '.orc' | …
    wrapper   = handler.detect_compression_by_magic_bytes(head)
    if not wrapper:
        # fall back to filename for wrapper (.gz/.zip/.snappy)
        for part in key.lower().split("."):
            if part in handler.COMPRESSION_EXTENSIONS:
                wrapper = f".{part}"
                break
    return wrapper, real_fmt


# ───────────────────────── helper: read via DuckDB ─────────────────────
def _relation_from_path(path: str, fmt: str, rows: int):
    """
    Return a DuckDB relation that contains *rows* sample rows.
    """
    if fmt in (".csv", ".tsv"):
        delim = "\t" if fmt == ".tsv" else ","
        q = f"SELECT * FROM read_csv_auto('{path}', delim='{delim}', header=True) LIMIT {rows}"
    elif fmt == ".json":
        q = f"SELECT * FROM read_json_auto('{path}') LIMIT {rows}"
    elif fmt == ".parquet":
        q = f"SELECT * FROM '{path}' LIMIT {rows}"
    elif fmt == ".orc":
        q = f"SELECT * FROM read_orc('{path}') LIMIT {rows}"
    elif fmt == ".avro":
        q = f"SELECT * FROM read_avro('{path}') LIMIT {rows}"
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    return duckdb.query(q)


# ─────────────────────────── main routine ──────────────────────────────
def read_s3_files_with_schema_inference(
    *,
    s3_urls: list[str],
    row_sample_count: int,
    event_name: str,
    recent_file_count: int,
    skip_profiling: bool = False,
) -> Optional[S3DetectionResult]:
    s3        = boto3.client("s3")
    handler   = CompressionHandler()
    converter = NativeS3Converter()
    data_map: Dict[str, Tuple[duckdb.DuckDBPyRelation | pa.Table, dict]] = {}

    for url in s3_urls:
        parsed  = urllib.parse.urlparse(url)
        bucket  = parsed.netloc
        key     = parsed.path.lstrip("/")
        ext_raw = os.path.splitext(key)[1].lower()

        # 0️⃣  sniff first 64 KB
        head_bytes = s3.get_object(
            Bucket=bucket, Key=key, Range="bytes=0-65535"
        )["Body"].read()
        wrapper, fmt = _sniff_wrapper_and_format(handler, key, head_bytes)

        # fallback if extension was already good
        if not fmt and ext_raw not in ("", ".gz", ".zip", ".snappy"):
            fmt = ext_raw

        if not fmt:
            logger.error(f"[SchemaDetect] cannot determine format for {url}")
            continue

        # 1️⃣  Avro with *no* wrapper → Arrow + fastavro quickest
        if fmt == ".avro" and not wrapper:
            whole = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            tbl   = pa.Table.from_pylist(
                list(fastavro.reader(io.BytesIO(whole)))[:row_sample_count]
            )
            schema = converter.to_recap(tbl, event_name=event_name)
            data_map[url] = (tbl, schema)
            continue

        # 2️⃣  Decide whether DuckDB can stream directly
        can_stream_direct = (
            not wrapper
            or (wrapper == ".gz"  and fmt in (".csv", ".tsv", ".json", ".parquet"))
            or (wrapper == ".zst" and fmt == ".parquet")
        )

        try:
            if can_stream_direct:
                s3_path = f"s3://{bucket}/{key}"
                rel     = _relation_from_path(s3_path, fmt, row_sample_count)
            else:
                # need local decompression (zip / snappy / mixed wrappers)
                with tempfile.TemporaryDirectory() as tmpd:
                    local_path = handler.decompress_s3_file_to_local(
                        bucket, key
                    )
                    real_fmt   = os.path.splitext(local_path)[1].lower()
                    rel = _relation_from_path(local_path, real_fmt or fmt, row_sample_count)

            # sanity-check the relation; skip if the read failed
            rel.aggregate("COUNT(*)").fetchone()

        except Exception as e:
            logger.error(f"[SchemaDetect] skip {url}: {e}")
            continue

        schema           = converter.to_recap(rel, event_name=event_name)
        data_map[url] = (rel, schema)

    if not data_map:
        return None

    merged_schema = merge_schemas([s for _, s in data_map.values()])

    if skip_profiling:
        return S3DetectionResult(merged_schema)

    profiles = get_data_asset_field_profiles_for_data_asset(
        merged_schema,
        {k: v[0] for k, v in data_map.items()},
        event_name,
        S3SamplingParameters(
            rowSampleCount=row_sample_count,
            recentFileCount=recent_file_count,
        ),
    )
    return S3DetectionResult(merged_schema, profiles)


# ───────────────────────── tiny utilities (unchanged) ─────────────────────────
def strip_s3_bucket_prefix(bucket: str) -> str:
    return bucket[len("s3://") :] if bucket.startswith("s3://") else bucket


def append_s3_url_prefix(bucket: str, key: str) -> str:
    if key.startswith("s3://"):
        return key
    return f"s3://{bucket}/{key.lstrip('/')}"
