"""
schema_profiler_duckdb.py
=========================

Compute DataAssetFieldProfiles directly with DuckDB/Arrow.
No pandas dependency, no copies; works on DuckDB relations
or Arrow tables that you already produce in schema_detection.py.
"""

from __future__ import annotations

import duckdb
import pyarrow as pa
from typing import Dict, Any, Mapping, List

from gable.openapi import (
    DataAssetFieldProfile,
    DataAssetFieldProfileBoolean,
    DataAssetFieldProfileList,
    DataAssetFieldProfileNumber,
    DataAssetFieldProfileOther,
    DataAssetFieldProfileString,
    DataAssetFieldProfileTemporal,
    DataAssetFieldProfileUnion,
    DataAssetFieldProfileUUID,
    DataAssetFieldsToProfilesMapping,
    S3SamplingParameters,
)
from gable.cli.helpers.data_asset_s3.path_pattern_manager import (
    UUID_REGEX_V1,
    UUID_REGEX_V3,
    UUID_REGEX_V4,
    UUID_REGEX_V5,
)
from loguru import logger


# ────────────────────────────────────────────────────────────────────────────
#  PUBLIC ENTRY
# ────────────────────────────────────────────────────────────────────────────
def get_data_asset_field_profiles_for_data_asset(
    recap_schema: dict,
    file_to_obj: Mapping[str, "duckdb.DuckDBPyRelation | pa.Table"],
    event_name: str,
    sampling_params: S3SamplingParameters,
) -> DataAssetFieldsToProfilesMapping | None:
    """
    Build { column_name -> DataAssetFieldProfile } using DuckDB aggregates,
    no pandas required.
    """
    logger.debug(f"[Profiler] computing profiles for {event_name}")

    if not file_to_obj:
        logger.warning(f"[Profiler] No sample data for {event_name}")
        return None

    # ------------------------------------------------------------------ #
    # 1 · Register every sample once (Arrow table) in a fresh connection
    # ------------------------------------------------------------------ #
    con        = duckdb.connect()
    view_names: list[str] = []

    for idx, (_, obj) in enumerate(file_to_obj.items()):
        view = f"sample_view_{idx}"
        if isinstance(obj, duckdb.DuckDBPyRelation):
            tbl = obj.fetch_arrow_table()               # zero-copy arrow
            con.register(view, tbl)
        elif isinstance(obj, pa.Table):
            con.register(view, obj)
        else:
            raise TypeError("Expected DuckDB relation or Arrow table")
        view_names.append(view)                         # ← append once

    union_sql  = " UNION ALL ".join(f"SELECT * FROM {v}" for v in view_names)
    merged_rel = con.query(union_sql)

    # ------------------------------------------------------------------ #
    # 2 · Map fully-qualified column names → schema fragments
    # ------------------------------------------------------------------ #
    column_schema: Dict[str, dict] = {}
    _populate_column_schemas(recap_schema, column_schema)

    # ------------------------------------------------------------------ #
    # 3 · Profile column-by-column
    # ------------------------------------------------------------------ #
    profiles: Dict[str, DataAssetFieldProfile] = {}

    for col, schema in column_schema.items():
        if col not in merged_rel.columns:
            logger.warning(f"[Profiler] Column {col} missing in sample; skipping")
            continue
        try:
            profiles[col] = _profile_column(
                con, merged_rel, col, schema, sampling_params
            )
        except Exception as e:
            logger.error(f"[Profiler] Error profiling {col}: {e}")

    return DataAssetFieldsToProfilesMapping(__root__=profiles)

# ────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ────────────────────────────────────────────────────────────────────────────
def _populate_column_schemas(schema: dict, out: dict, prefix: str = ""):
    for field in schema["fields"]:
        name = prefix + field["name"]
        if field["type"] == "struct":
            _populate_column_schemas(field, out, name + ".")
        else:
            out[name] = field





def _profile_column(
    con: duckdb.DuckDBPyConnection,        # kept for regex BOOL_AND call
    rel: duckdb.DuckDBPyRelation,
    col: str,
    schema: dict,
    params: S3SamplingParameters,
) -> DataAssetFieldProfile:
    col_q = f'"{col}"'                      # always quote identifiers

    total_rows_row = rel.aggregate("COUNT(*)").fetchone()
    total_rows = total_rows_row[0] if total_rows_row is not None else 0
    null_cnt_row = rel.aggregate(f"COUNT(*) - COUNT({col_q})").fetchone()
    null_cnt = null_cnt_row[0] if null_cnt_row is not None else 0

    # ─────────────────────────────  BOOLEAN  ──────────────────────────────
    if schema["type"] == "bool":
        true_cnt_row = rel.aggregate(f"SUM(LOWER({col_q}) = 'true')").fetchone()
        true_cnt = true_cnt_row[0] if true_cnt_row is not None else 0
        false_cnt_row = rel.aggregate(f"SUM(LOWER({col_q}) = 'false')").fetchone()
        false_cnt = false_cnt_row[0] if false_cnt_row is not None else 0
        profile = DataAssetFieldProfileBoolean(
            profileType="boolean",
            sampledRecordsCount=total_rows,
            nullable=null_cnt > 0,
            nullCount=null_cnt,
            trueCount=true_cnt or 0,
            falseCount=false_cnt or 0,
            sampledFiles=list(params.dict().values()),
            samplingParameters=params,
        )

    # ─────────────────────────────  NUMERIC / TEMPORAL  ───────────────────
    elif schema["type"] in ("int", "float"):
        min_v_row = rel.aggregate(f"MIN({col_q})").fetchone()
        min_v = min_v_row[0] if min_v_row is not None else None
        max_v_row = rel.aggregate(f"MAX({col_q})").fetchone()
        max_v = max_v_row[0] if max_v_row is not None else None
        uniq_row = rel.aggregate(f"COUNT(DISTINCT {col_q})").fetchone()
        uniq = uniq_row[0] if uniq_row is not None else 0


        if _schema_is_date(schema):
            profile = DataAssetFieldProfileTemporal(
                profileType="temporal",
                sampledRecordsCount=total_rows,
                nullable=null_cnt > 0,
                nullCount=null_cnt,
                min=min_v, # type: ignore
                max=max_v, # type: ignore
                format="",
                sampledFiles=list(params.dict().values()),
                samplingParameters=params,
            )
        else:
            uniq_row = rel.aggregate(f"COUNT(DISTINCT {col_q})").fetchone()
            uniq = uniq_row[0] if uniq_row is not None else 0
            profile = DataAssetFieldProfileNumber(
                profileType="number",
                sampledRecordsCount=total_rows,
                nullable=null_cnt > 0,
                nullCount=null_cnt,
                uniqueCount=uniq, # type: ignore
                min=min_v, # type: ignore
                max=max_v, # type: ignore
                sampledFiles=list(params.dict().values()),
                samplingParameters=params,
            )

    # ─────────────────────────────  STRING  ───────────────────────────────
    elif schema["type"] == "string":
        uniq_row = rel.aggregate(f"COUNT(DISTINCT {col_q})").fetchone()
        uniq = uniq_row[0] if uniq_row is not None else 0
        empty_cnt_row = rel.aggregate(f"SUM({col_q} = '')").fetchone()
        empty_cnt = empty_cnt_row[0] if empty_cnt_row is not None else 0
        max_len_row = rel.aggregate(f"MAX(LENGTH({col_q}))").fetchone()
        max_len = max_len_row[0] if max_len_row is not None else None
        min_len_row = rel.aggregate(f"MIN(LENGTH({col_q}))").fetchone()
        min_len = min_len_row[0] if min_len_row is not None else None

        # UUID-v4 check – use relation aggregate instead of SELECT … FROM (rel)
        is_v4_row = rel.aggregate(
            f"BOOL_AND(REGEXP_MATCHES({col_q}, '^{UUID_REGEX_V4}$'))"
        ).fetchone()
        is_v4 = is_v4_row[0] if is_v4_row is not None else False




        if is_v4:
            profile = DataAssetFieldProfileUUID(
                profileType="uuid",
                sampledRecordsCount=total_rows,
                nullable=null_cnt > 0,
                nullCount=null_cnt,
                uuidVersion=4,
                emptyCount=empty_cnt or 0,
                uniqueCount=uniq, # type: ignore
                maxLength=max_len, # type: ignore
                minLength=min_len, # type: ignore
                sampledFiles=list(params.dict().values()),
                samplingParameters=params,
            )
        else:
            profile = DataAssetFieldProfileString(
                profileType="string",
                sampledRecordsCount=total_rows,
                nullable=null_cnt > 0,
                nullCount=null_cnt,
                emptyCount=empty_cnt or 0,
                uniqueCount=uniq, # type: ignore
                maxLength=max_len, # type: ignore
                minLength=min_len, # type: ignore
                sampledFiles=list(params.dict().values()),
                samplingParameters=params,
            )

    # ─────────────────────────────  LIST  ─────────────────────────────────
    elif schema["type"] == "list":
        max_len_row = rel.aggregate(f"MAX(CARDINALITY({col_q}))").fetchone()
        max_len = max_len_row[0] if max_len_row is not None else None
        min_len_row = rel.aggregate(f"MIN(CARDINALITY({col_q}))").fetchone()
        min_len = min_len_row[0] if min_len_row is not None else None

        profile = DataAssetFieldProfileList(
            profileType="list",
            sampledRecordsCount=total_rows,
            nullable=null_cnt > 0,
            nullCount=null_cnt,
            maxLength=max_len, # type: ignore
            minLength=min_len, # type: ignore
            sampledFiles=list(params.dict().values()),
            samplingParameters=params,
        )

    # ─────────────────────────────  UNION / OTHER  ────────────────────────
    elif schema["type"] == "union":
        profile = DataAssetFieldProfileUnion(
            profileType="union",
            sampledRecordsCount=total_rows,
            nullable=null_cnt > 0,
            profiles=[],   # recursion can be added later
            sampledFiles=list(params.dict().values()),
            samplingParameters=params,
        )
    else:
        profile = DataAssetFieldProfileOther(
            profileType="other",
            sampledRecordsCount=total_rows,
            nullable=null_cnt > 0,
            nullCount=null_cnt,
            sampledFiles=list(params.dict().values()),
            samplingParameters=params,
        )

    return DataAssetFieldProfile(__root__=profile)

def _schema_is_date(schema: dict) -> bool:
    return schema["type"] == "int" and schema.get("logical") in ("Timestamp", "Date")
