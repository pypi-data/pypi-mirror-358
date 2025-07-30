import json
import pytest
from pydantic import BaseModel
from good_clickhouse._types import JsonDict


class TestJsonDict:
    def test_init_empty(self):
        # Test empty initialization
        jd = JsonDict()
        assert len(jd) == 0
        assert isinstance(jd, dict)

    def test_init_with_dict(self):
        # Test initialization with dictionary
        data = {"key": "value", "number": 42}
        jd = JsonDict(data)
        assert jd["key"] == "value"
        assert jd["number"] == 42

    def test_init_with_kwargs(self):
        # Test initialization with keyword arguments
        jd = JsonDict(name="test", value=123)
        assert jd["name"] == "test"
        assert jd["value"] == 123

    def test_init_with_both(self):
        # Test initialization with both dict and kwargs
        data = {"existing": "data"}
        jd = JsonDict(data, new="value", number=99)
        assert jd["existing"] == "data"
        assert jd["new"] == "value"
        assert jd["number"] == 99

    def test_repr(self):
        # Test string representation
        jd = JsonDict(key="value", number=42)
        repr_str = repr(jd)
        assert repr_str == "JsonDict({'key': 'value', 'number': 42})"

    def test_json_serialization(self):
        # Test JSON serialization
        jd = JsonDict(name="test", value=123, nested={"inner": "data"})
        json_str = json.dumps(jd)
        loaded = json.loads(json_str)
        assert loaded["name"] == "test"
        assert loaded["value"] == 123
        assert loaded["nested"]["inner"] == "data"

    def test_pydantic_integration(self):
        # Test integration with Pydantic models
        class MyModel(BaseModel):
            data: JsonDict

        model = MyModel(data=JsonDict(key="value"))
        assert model.data["key"] == "value"
        
        # Test model serialization
        model_dict = model.model_dump()
        assert model_dict["data"]["key"] == "value"
        
        # Test JSON serialization through Pydantic
        json_str = model.model_dump_json()
        loaded = json.loads(json_str)
        assert loaded["data"]["key"] == "value"

    def test_dict_methods(self):
        # Test that dict methods work properly
        jd = JsonDict(a=1, b=2, c=3)
        
        assert list(jd.keys()) == ["a", "b", "c"]
        assert list(jd.values()) == [1, 2, 3]
        assert list(jd.items()) == [("a", 1), ("b", 2), ("c", 3)]
        
        jd["d"] = 4
        assert jd["d"] == 4
        
        del jd["a"]
        assert "a" not in jd
        
        jd.update({"e": 5, "f": 6})
        assert jd["e"] == 5
        assert jd["f"] == 6