from __future__ import annotations

import duckdb
import pyarrow as pa
from typing import Any, Dict, List


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────
def _duck_type_to_recap(duck_type: str) -> str:
    mapping = {
        "BOOLEAN": "boolean",
        "TINYINT": "int8",
        "SMALLINT": "int16",
        "INTEGER": "int32",
        "BIGINT": "int64",
        "UTINYINT": "uint8",
        "USMALLINT": "uint16",
        "UINTEGER": "uint32",
        "UBIGINT": "uint64",
        "FLOAT": "float32",
        "DOUBLE": "float64",
        "DECIMAL": "decimal",
        "VARCHAR": "string",
        "TIME": "time",
        "TIMESTAMP": "timestamp",
        "DATE": "date",
        "BLOB": "bytes",
        "LIST": "array",
        "MAP": "map",
        "STRUCT": "struct",
    }
    return mapping.get(duck_type.upper(), "string")


def _arrow_type_to_recap(a_type: pa.DataType) -> str:
    if pa.types.is_boolean(a_type):
        return "boolean"
    if pa.types.is_integer(a_type):
        signed = a_type.bit_width < 64 and a_type.bit_width != 0
        return ("u" if not signed else "") + f"int{a_type.bit_width}"
    if pa.types.is_floating(a_type):
        return f"float{a_type.bit_width}"
    if pa.types.is_binary(a_type) or pa.types.is_large_binary(a_type):
        return "bytes"
    if pa.types.is_string(a_type) or pa.types.is_large_string(a_type):
        return "string"
    if pa.types.is_timestamp(a_type):
        return "timestamp"
    if pa.types.is_date(a_type):
        return "date"
    if pa.types.is_list(a_type):
        return "array"
    if pa.types.is_struct(a_type):
        return "struct"
    return "string"


# ────────────────────────────────────────────────────────────────────────────
# Converter
# ────────────────────────────────────────────────────────────────────────────
class NativeS3Converter:
    """
    Convert DuckDB relations **or** Arrow tables to a Gable/Recap schema dict
    with no pandas dependency.
    """

    def to_recap(self, table: Any, *, event_name: str) -> Dict[str, Any]:
        if isinstance(table, duckdb.DuckDBPyRelation):
            return self._from_duck_relation(table, event_name)
        if isinstance(table, pa.Table):
            return self._from_arrow_table(table, event_name)
        raise TypeError(
            "NativeS3Converter.to_recap() accepts duckdb.DuckDBPyRelation or pyarrow.Table"
        )

    # ─────────────────────────────  DuckDB path  ─────────────────────────────
    def _from_duck_relation(
        self, rel: duckdb.DuckDBPyRelation, event_name: str
    ) -> Dict[str, Any]:
        """
        Build Recap schema from a DuckDB relation *without* pulling in pandas.

        • We issue a single COUNT(col) per column to know how many NULLs exist.  
        fetchall() returns plain Python tuples, so no pandas is involved.
        """
        # ----- 1. build COUNT expression for every column -------------------
        cnt_sql = ", ".join(
            f'COUNT("{col}") AS cnt_{i}' for i, col in enumerate(rel.columns)
        )

        # ----- 2. run aggregation & retrieve counts as a tuple --------------
        non_null_counts = rel.aggregate(cnt_sql).fetchall()[0]  # e.g. (100, 95, 100, …)
        # total_rows WITH the correct syntax
        total_rows_result = rel.aggregate("COUNT(*)").fetchone()
        total_rows = total_rows_result[0] if total_rows_result is not None else 0

        # ----- 3. craft Recap fields ----------------------------------------
        fields: List[Dict[str, Any]] = []
        for idx, col_name in enumerate(rel.columns):
            duck_type  = rel.types[idx]            # DuckDBPyType
            recap_type = _duck_type_to_recap(str(duck_type))  # 🔑 cast to str

            non_null_cnt = non_null_counts[idx]

            # If the table is empty, all fields are nullable
            if total_rows == 0:
                nullable = True
            else:
                nullable = (total_rows - non_null_cnt) > 0

            fields.append(
                {
                    "name": col_name,
                    "type": recap_type,
                    "nullable": nullable,
                    "logical": None,
                    "doc": None,
                }
            )

        return {
            "type": "struct",
            "name": event_name,
            "fields": fields,
            "doc": None,
            "logical": None,
        }

    # ─────────────────────────────  Arrow path  ─────────────────────────────
    def _from_arrow_table(self, tbl: pa.Table, event_name: str) -> Dict[str, Any]:
        fields: List[Dict[str, Any]] = []
        for field in tbl.schema:
            recap_type = _arrow_type_to_recap(field.type)
            fields.append(
                {
                    "name": field.name,
                    "type": recap_type,
                    "nullable": field.nullable,
                    "logical": None,
                    "doc": None,
                }
            )
        return {
            "type": "struct",
            "name": event_name,
            "fields": fields,
            "doc": None,
            "logical": None,
        }

def merge_schemas(schemas: list[dict]) -> dict:
    """
    Merge multiple Recap/Gable schemas into one:
    • Flattens field order
    • Recursively merges nested structs
    • Creates unions when same-named fields differ
    """
    result: dict[str, dict] = {}

    for schema in schemas:
        for field in schema.get("fields", []):
            name = field["name"]

            # first time we see the field → keep as-is
            if name not in result:
                result[name] = field
                continue

            # if both sides are structs, recurse
            if (
                field["type"] == "struct"
                and result[name]["type"] == "struct"
            ):
                merged_inner = merge_schemas([result[name], field])
                result[name] = {"type": "struct", "name": name, "fields": merged_inner["fields"]}
                continue

            # otherwise form / extend a union
            left  = result[name]
            right = field

            left_types  = left["types"]  if left ["type"] == "union" else [left]
            right_types = right["types"] if right["type"] == "union" else [right]

            union_types = _get_distinct_dicts(_remove_names(left_types + right_types))

            if len(union_types) == 1:
                result[name] = {"name": name, **union_types[0]}
                continue # ✅ no union needed

            result[name] = {"type": "union", "name": name, "types": union_types}

    return {"type": "struct", "fields": list(result.values())}


def _get_distinct_dicts(items: list[dict]) -> list[dict]:
    """Return list with duplicates removed, preserving first-seen order."""
    seen, out = set(), []
    for d in items:
        frozen = frozenset(d.items())
        if frozen not in seen:
            seen.add(frozen)
            out.append(d)
    return out


def _remove_names(items: list[dict]) -> list[dict]:
    """Strip 'name' keys so identical types compare equal."""
    return [{k: v for k, v in d.items() if k != "name"} for d in items]
