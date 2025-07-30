"""
compression_handler.py
———————————————
Detect wrapper compression, infer true format, and decompress in memory.
"""

from __future__ import annotations

import gzip
import io
import os
import tempfile
import zipfile
from typing import Tuple

import boto3
import snappy
from gable.cli.helpers.data_asset_s3.logger import log_debug


class CompressionHandler:
    SUPPORTED_FILE_TYPES       = {"json", "csv", "tsv", "parquet", "orc", "avro"}
    COMPRESSION_EXTENSIONS     = {"gz", "snappy", "zip", "zst"}  # extend as needed
    _ZSTD_MAGIC                = b"\x28\xb5\x2f\xfd"

    # ───────────────────────────── basic helpers ─────────────────────────────
    @staticmethod
    def is_compressed(file_key: str) -> bool:
        exts = set(file_key.lower().split("."))

        # If there is only one extension it's just a filename without a compression extension
        if len(exts) == 1:
            return False

        return any(ext in CompressionHandler.COMPRESSION_EXTENSIONS for ext in exts)

    @staticmethod
    def split_format_and_wrapper(file_key: str) -> tuple[str | None, str | None]:
        """
        Return True iff *any* dot-separated token is a compression ext **and**
        the key actually contains at least one dot.  Bare words like 'gz'
        or 'snappy' are treated as *not* compressed.
        """
        tokens = file_key.lower().split(".")
        if len(tokens) < 2:                          #    ← no dot at all
            return False
        # ignore the first token (file name), inspect the rest
        return any(tok in CompressionHandler.COMPRESSION_EXTENSIONS
                   for tok in tokens[1:])
    
    @staticmethod
    def is_internal_snappy(
        format_ext: str | None,
        wrapper_ext: str | None,
    ) -> bool:
        """
        True when the *wrapper* token is '.snappy' **and** the *format* is a
        columnar file that normally stores Snappy *inside* (ORC/Parquet/Avro).
        """
        return (
            wrapper_ext == ".snappy"
            and format_ext in {".orc", ".parquet", ".avro"}
        )


    @staticmethod
    def split_format_and_wrapper(
        file_key: str,
    ) -> tuple[str | None, str | None]:
        tokens = file_key.lower().split(".")

        fmt  = next((f".{t}" for t in tokens if t in CompressionHandler.SUPPORTED_FILE_TYPES), None)
        wrap = next((f".{t}" for t in tokens if t in CompressionHandler.COMPRESSION_EXTENSIONS), None)

        # Use the new helper – drop '.snappy' if it's only an internal codec
        if CompressionHandler.is_internal_snappy(fmt, wrap):
            wrap = None

        return fmt, wrap
    
    @staticmethod
    def detect_compression_by_magic_bytes(data: bytes) -> str:
        if data.startswith(b"\x1f\x8b"):
            return "gz"
        if data.startswith(b"PK\x03\x04"):
            return "zip"
        if data.startswith(b"\xff\x06\x00\x00sNaPpY"):
            return "snappy"
        if data.startswith(CompressionHandler._ZSTD_MAGIC):
            return "zst"
        try:
            snappy.decompress(data);          return "snappy"
        except Exception:
            pass
        return ""

    # magic-byte probe (true format)
    @staticmethod
    def detect_format_by_magic_bytes(data: bytes) -> str:
        if data.startswith(b"PAR1"):                return ".parquet"
        if b"ORC" in data[-16:]:                    return ".orc"
        if data.startswith(b"Obj"):                 return ".avro"
        if data.strip().startswith((b"{", b"[")):   return ".json"
        if b"," in data[:1024]:                     return ".csv"
        if b"\t" in data[:1024]:                    return ".tsv"
        return ""

    @staticmethod
    def get_original_format(file_key: str, file_content: bytes=b"") -> str:
        # try by explicit token first
        for token in file_key.lower().split("."):
            if token in CompressionHandler.SUPPORTED_FILE_TYPES:
                return f".{token}"
        # else probe magic bytes
        return CompressionHandler.detect_format_by_magic_bytes(file_content)

    # ───────────────────────────── in-memory decompress ─────────────────────
    @staticmethod
    def decompress(file_key: str, raw_bytes: bytes) -> Tuple[io.BytesIO, str]:
        """Return (decompressed_bytes, original_format_ext)"""
        ext_hint = CompressionHandler.detect_compression_by_magic_bytes(raw_bytes)
        if not ext_hint:
            for tok in file_key.lower().split("."):
                if tok in CompressionHandler.COMPRESSION_EXTENSIONS:
                    ext_hint = tok; break
        if ext_hint == "gz":
            data = gzip.decompress(raw_bytes)
        elif ext_hint == "snappy":
            data = snappy.decompress(raw_bytes)
        elif ext_hint == "zip":
            with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
                name = zf.namelist()[0]
                data = zf.read(name)
                file_key = name  # more accurate for format detection
        else:
            raise ValueError(f"Unsupported compression wrapper: {file_key}")

        if not isinstance(data, bytes):
            data = data.encode("utf-8")
        return io.BytesIO(data), CompressionHandler.get_original_format(file_key, data)

    # ───────────────────────────── S3 helper used by schema_detection ───────
    def decompress_s3_file_to_local(
        self,
        bucket: str,
        key: str,
        tmpdir: str | None = None,          # ← NEW OPTIONAL ARG
    ) -> str:
        s3  = boto3.client("s3")
        raw = s3.get_object(Bucket=bucket, Key=key)["Body"].read()

        if not self.is_compressed(key):
            suffix = os.path.splitext(key)[1] or ".bin"
            tmp    = tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix, dir=tmpdir   # ← use tmpdir
                     )
            tmp.write(raw); tmp.close()
            return tmp.name

        byte_io, orig_ext = self.decompress(key, raw)
        suffix = orig_ext or ".bin"
        tmp    = tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix, dir=tmpdir       # ← use tmpdir
                 )
        tmp.write(byte_io.read()); tmp.close()
        return tmp.name
