import datetime
import decimal
import uuid
from enum import Enum
from typing import Optional, List, Dict, Tuple

import pytest
from pydantic import BaseModel
from good_common.modeling import TypeInfo

from good_clickhouse.query import (
    get_clickhouse_type,
    set_clickhouse_default_json_type,
    get_clickhouse_default_json_type,
    get_env_var,
    filter_quote,
    ClickhouseColumn,
)
from good_clickhouse._types import JsonDict


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class SampleModel(BaseModel):
    name: str
    value: int


class TestClickhouseTypeMapping:
    def test_basic_types(self):
        # Test basic type conversions
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(str)) == "String"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(int)) == "Int64"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(int), int64=False) == "Int32"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(float)) == "Float64"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(bool)) == "Bool"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(datetime.date)) == "Date"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(datetime.datetime)) == "DateTime64(3)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(datetime.datetime), datetime64=False) == "DateTime"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(uuid.UUID)) == "UUID"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(decimal.Decimal)) == "Decimal64(4)"

    def test_low_cardinality_strings(self):
        # Test LowCardinality option for strings
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(str), low_cardinality_strings=True) == "LowCardinality(String)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Color), low_cardinality_strings=True) == "LowCardinality(String)"

    def test_enum_types(self):
        # Test enum type conversion
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Color)) == "String"

    def test_optional_types(self):
        # Test nullable type handling
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[str])) == "Nullable(String)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[int])) == "Nullable(Int64)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[float])) == "Nullable(Float64)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[bool])) == "Nullable(Bool)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[datetime.date])) == "Nullable(Date)"

    def test_array_types(self):
        # Test array/list type conversion
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(List[str])) == "Array(String)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(List[int])) == "Array(Int64)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(List[Optional[str]])) == "Array(Nullable(String))"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(List[List[int]])) == "Array(Array(Int64))"

    def test_tuple_types(self):
        # Test tuple type conversion
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Tuple[str, int])) == "Tuple(String, Int64)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Tuple[str, int, float])) == "Tuple(String, Int64, Float64)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Tuple[Optional[str], int])) == "Tuple(Nullable(String), Int64)"

    def test_map_types(self):
        # Test map/dict type conversion
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Dict[str, str])) == "Map(String, String)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Dict[int, str])) == "Map(Int64, String)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Dict[str, Optional[int]])) == "Map(String, Nullable(Int64))"
        
        # Test unsupported key types fallback to String
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Dict[float, str])) == "String"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Dict[datetime.date, str])) == "String"

    def test_json_dict_type(self):
        # Test JsonDict type conversion
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(JsonDict)) == "String"
        
        # Test changing default JSON type
        set_clickhouse_default_json_type("JSON")
        assert get_clickhouse_default_json_type() == "JSON"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(JsonDict)) == "JSON"
        
        # Reset to default
        set_clickhouse_default_json_type("String")

    def test_pydantic_model_types(self):
        # Test Pydantic model conversion
        typeinfo = TypeInfo.annotation_extract_primary_type(SampleModel)
        assert get_clickhouse_type(typeinfo) == "String"
        
        # Test with custom JSON type
        set_clickhouse_default_json_type("JSON")
        assert get_clickhouse_type(typeinfo) == "JSON"
        set_clickhouse_default_json_type("String")

    def test_custom_db_type(self):
        # Test custom db_type override
        typeinfo = TypeInfo.annotation_extract_primary_type(str)
        typeinfo.db_type = "FixedString(10)"
        assert get_clickhouse_type(typeinfo) == "FixedString(10)"

    def test_complex_nested_types(self):
        # Test complex nested type combinations
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(List[Dict[str, int]])) == "Array(Map(String, Int64))"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Dict[str, List[int]])) == "Map(String, Array(Int64))"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[List[Dict[str, str]]])) == "Nullable(Array(Map(String, String)))"

    def test_nullable_restrictions(self):
        # Test that certain types don't get wrapped in Nullable
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[Dict[str, str]])) == "Map(String, String)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(Optional[List[Optional[str]]])) == "Array(Nullable(String))"

    def test_no_typeinfo_error(self):
        # Test error when typeinfo is None
        with pytest.raises(ValueError, match="typeinfo is required"):
            get_clickhouse_type(None)

    def test_datetime_precision(self):
        # Test different datetime precisions
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(datetime.datetime), datetime_precision=0) == "DateTime64(0)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(datetime.datetime), datetime_precision=6) == "DateTime64(6)"
        assert get_clickhouse_type(TypeInfo.annotation_extract_primary_type(datetime.datetime), datetime_precision=9) == "DateTime64(9)"


class TestClickhouseColumn:
    def test_column_creation(self):
        # Test basic column creation
        typeinfo = TypeInfo.annotation_extract_primary_type(str)
        col = ClickhouseColumn("name", typeinfo)
        assert col.name == "name"
        assert col.type == "String"
        assert col.json_serialize is False

    def test_column_with_pydantic_model(self):
        # Test column with Pydantic model sets json_serialize
        typeinfo = TypeInfo.annotation_extract_primary_type(SampleModel)
        col = ClickhouseColumn("data", typeinfo)
        assert col.name == "data"
        assert col.type == "String"
        assert col.json_serialize is True

    def test_column_repr(self):
        # Test string representation
        typeinfo = TypeInfo.annotation_extract_primary_type(int)
        col = ClickhouseColumn("count", typeinfo)
        assert repr(col) == "count Int64"

    def test_column_with_options(self):
        # Test column creation with options
        typeinfo = TypeInfo.annotation_extract_primary_type(str)
        col = ClickhouseColumn("name", typeinfo, low_cardinality_strings=True)
        assert col.type == "LowCardinality(String)"


class TestHelperFunctions:
    def test_get_env_var_default(self):
        # Test getting env var with default
        assert get_env_var("NONEXISTENT_VAR", "default") == "default"
        
    def test_get_env_var_exists(self, monkeypatch):
        # Test getting existing env var
        monkeypatch.setenv("TEST_VAR", "test_value")
        assert get_env_var("TEST_VAR") == "test_value"
        
    def test_get_env_var_fail_if_missing(self):
        # Test failing when env var is missing
        with pytest.raises(KeyError):
            get_env_var("NONEXISTENT_VAR", fail_if_missing=True)

    def test_filter_quote(self):
        # Test SQL value quoting
        assert filter_quote("test") == "'test'"
        assert filter_quote("test's") == "'test's'"
        assert filter_quote("") == "''"