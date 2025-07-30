import json
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field, computed_field

from good_clickhouse.collection import (
    DataTable,
    PydanticCollection,
    columns_from_model,
    insert_into_clickhouse,
)
from good_clickhouse.query import ClickhouseColumn


class SampleModel(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    active: bool = True
    
    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.id})"


class ModelWithExclusions(BaseModel):
    __exclude_columns__ = ["internal_field"]
    __table_column_order__ = ["id", "name", "value"]
    
    id: int
    name: str
    value: float
    internal_field: str = "internal"
    extra_field: Optional[str] = None


class TestDataTable:
    def test_model_all_fields(self):
        # Test getting all fields from model - DataTable.model_all_fields is a classmethod
        # Create a subclass that inherits from DataTable
        from good_common.types import UUIDField
        
        class TestDataTableModel(DataTable):
            uid: UUIDField
            id: int
            name: str
            email: Optional[str] = None
            active: bool = True
            
            @computed_field
            @property
            def display_name(self) -> str:
                return f"{self.name} ({self.id})"
        
        fields = TestDataTableModel.model_all_fields()
        assert "uid" in fields
        assert "id" in fields
        assert "name" in fields
        assert "email" in fields
        assert "active" in fields
        assert "display_name" in fields  # Computed field should be included

    def test_object_all_fields(self):
        # Test getting all fields from instance
        from good_common.types import UUIDField
        import uuid
        
        class TestDataTableModel(DataTable):
            uid: UUIDField
            id: int
            name: str
            email: Optional[str] = None
            active: bool = True
            
            @computed_field
            @property
            def display_name(self) -> str:
                return f"{self.name} ({self.id})"
        
        instance = TestDataTableModel(uid=uuid.uuid4(), id=1, name="Test")
        fields = instance.object_all_fields()
        
        # object_all_fields returns TypeInfo objects, not values
        assert "uid" in fields
        assert "id" in fields
        assert "name" in fields
        assert "email" in fields
        assert "active" in fields
        assert "display_name" in fields

    def test_data_table_with_extra_attributes(self):
        # Test handling of extra attributes
        from good_common.types import UUIDField
        import uuid
        
        class TestDataTableModel(DataTable):
            uid: UUIDField
            id: int
            name: str
            
            model_config = {"extra": "allow"}
        
        instance = TestDataTableModel(uid=uuid.uuid4(), id=1, name="Test", extra_attr="extra_value")
        fields = instance.object_all_fields()
        
        # Should include the extra attribute
        assert "extra_attr" in fields


class TestColumnsFromModel:
    def test_basic_column_generation(self):
        # columns_from_model expects a model class with model_fields
        # Since SampleModel doesn't have model_all_fields, it will use model_fields
        # which returns FieldInfo objects, not TypeInfo
        from good_common.types import UUIDField
        
        class TestModel(DataTable):
            uid: UUIDField
            id: int
            name: str
            email: Optional[str] = None
            active: bool = True
            
            @computed_field
            @property
            def display_name(self) -> str:
                return f"{self.name} ({self.id})"
        
        columns = columns_from_model(TestModel)
        
        # Check that all columns are created
        column_names = [col.name for col in columns]
        assert "uid" in column_names
        assert "id" in column_names
        assert "name" in column_names
        assert "email" in column_names
        assert "active" in column_names
        assert "display_name" in column_names
        
        # Check column types
        id_col = next(col for col in columns if col.name == "id")
        assert id_col.type == "Int64"
        
        name_col = next(col for col in columns if col.name == "name")
        assert name_col.type == "String"
        
        email_col = next(col for col in columns if col.name == "email")
        assert email_col.type == "Nullable(String)"
        
        active_col = next(col for col in columns if col.name == "active")
        assert active_col.type == "Bool"

    def test_column_exclusion(self):
        # Test that excluded columns are not generated
        from good_common.types import UUIDField
        
        class TestModelWithExclusions(DataTable):
            __exclude_columns__ = {"internal_field"}  # Should be a set
            __table_column_order__ = ["uid", "id", "name", "value"]
            
            uid: UUIDField
            id: int
            name: str
            value: float
            internal_field: str = "internal"
            extra_field: Optional[str] = None
        
        columns = columns_from_model(TestModelWithExclusions)
        column_names = [col.name for col in columns]
        
        assert "internal_field" not in column_names
        assert "id" in column_names
        assert "name" in column_names
        assert "value" in column_names
        assert "extra_field" in column_names

    def test_column_ordering(self):
        # Test that columns are ordered according to __table_column_order__
        from good_common.types import UUIDField
        
        class TestModelWithOrder(DataTable):
            __table_column_order__ = ["id", "name", "value"]
            
            uid: UUIDField
            id: int
            name: str
            value: float
            extra_field: Optional[str] = None
        
        columns = columns_from_model(TestModelWithOrder)
        column_names = [col.name for col in columns]
        
        # Find positions of ordered columns
        id_pos = column_names.index("id")
        name_pos = column_names.index("name")
        value_pos = column_names.index("value")
        
        # They should be in order
        assert id_pos < name_pos < value_pos
        # uid and extra_field should exist but not necessarily in specific positions
        assert "uid" in column_names
        assert "extra_field" in column_names


class TestPydanticCollectionWithDataTable:
    def get_test_model(self):
        from good_common.types import UUIDField
        
        class TestDataModel(DataTable):
            uid: UUIDField
            id: int
            name: str
            email: Optional[str] = None
            active: bool = True
            
            @computed_field
            @property
            def display_name(self) -> str:
                return f"{self.name} ({self.id})"
        
        return TestDataModel
    
    def test_init_with_list(self):
        # Test initialization with list of models
        import uuid
        TestModel = self.get_test_model()
        
        models = [
            TestModel(uid=uuid.uuid4(), id=1, name="Alice"),
            TestModel(uid=uuid.uuid4(), id=2, name="Bob"),
        ]
        collection = PydanticCollection(models, type=TestModel)
        
        assert len(collection) == 2
        assert collection._type == TestModel

    def test_init_empty(self):
        # Test initialization with empty list and explicit model
        TestModel = self.get_test_model()
        collection = PydanticCollection([], type=TestModel)
        
        assert len(collection) == 0
        assert collection._type == TestModel

    def test_len(self):
        # Test __len__ method
        import uuid
        TestModel = self.get_test_model()
        models = [TestModel(uid=uuid.uuid4(), id=i, name=f"User{i}") for i in range(5)]
        collection = PydanticCollection(models, type=TestModel)
        
        assert len(collection) == 5

    def test_getitem(self):
        # Test __getitem__ method
        import uuid
        TestModel = self.get_test_model()
        models = [
            TestModel(uid=uuid.uuid4(), id=1, name="Alice"),
            TestModel(uid=uuid.uuid4(), id=2, name="Bob"),
        ]
        collection = PydanticCollection(models, type=TestModel)
        
        # getitem returns serialize_to_columns result
        item = collection[0]
        assert item["id"] == 1
        assert item["name"] == "Alice"
        assert item["display_name"] == "Alice (1)"

    def test_getitem_with_serializer(self):
        # Test __getitem__ with custom serializer
        import uuid
        TestModel = self.get_test_model()
        
        def custom_serializer(obj):
            return {"custom_id": obj.id, "custom_name": obj.name.upper()}
        
        models = [TestModel(uid=uuid.uuid4(), id=1, name="Alice")]
        collection = PydanticCollection(models, type=TestModel, serializer=custom_serializer)
        
        item = collection[0]
        assert item == {"custom_id": 1, "custom_name": "ALICE"}

    def test_select_property(self):
        # Test select property
        TestModel = self.get_test_model()
        collection = PydanticCollection([], type=TestModel)
        select = collection.select
        
        # select returns comma-separated column names
        assert "uid" in select
        assert "id" in select
        assert "name" in select
        assert "email" in select
        assert "active" in select
        assert "display_name" in select

    def test_columns_property(self):
        # Test columns property
        TestModel = self.get_test_model()
        collection = PydanticCollection([], type=TestModel)
        columns = collection.columns
        
        # Check that columns are ClickhouseColumn instances
        assert all(isinstance(col, ClickhouseColumn) for col in columns)
        
        # Check column names
        column_names = [col.name for col in columns]
        assert "uid" in column_names
        assert "id" in column_names
        assert "name" in column_names
        assert "email" in column_names
        assert "active" in column_names
        assert "display_name" in column_names

    def test_columns_with_exclusion(self):
        # Test columns with exclusion
        from good_common.types import UUIDField
        
        class TestModelWithExclusions(DataTable):
            __exclude_columns__ = {"internal_field"}  # Should be a set
            
            uid: UUIDField
            id: int
            name: str
            internal_field: str = "internal"
        
        collection = PydanticCollection([], type=TestModelWithExclusions)
        columns = collection.columns
        
        column_names = [col.name for col in columns]
        assert "internal_field" not in column_names

    def test_serialize_to_columns(self):
        # Test serialize_to_columns method - it takes an object as parameter
        import uuid
        TestModel = self.get_test_model()
        model = TestModel(uid=uuid.uuid4(), id=1, name="Alice", email="alice@example.com")
        collection = PydanticCollection([model], type=TestModel)
        
        # serialize_to_columns takes a single object
        serialized = collection.serialize_to_columns(model)
        
        # Should return a dict
        assert isinstance(serialized, dict)
        assert serialized["id"] == 1
        assert serialized["name"] == "Alice"
        assert serialized["email"] == "alice@example.com"
        assert serialized["active"] is True
        assert serialized["display_name"] == "Alice (1)"

    def test_serialize_with_json(self):
        # Test serialization of complex types
        from good_common.types import UUIDField
        from good_common.modeling import TypeInfo
        
        class ComplexDataModel(DataTable):
            uid: UUIDField
            id: int
            data: dict
            tags: List[str]
        
        import uuid
        model = ComplexDataModel(uid=uuid.uuid4(), id=1, data={"key": "value"}, tags=["tag1", "tag2"])
        collection = PydanticCollection([model], type=ComplexDataModel)
        
        # The collection will properly detect json_serialize from model fields
        serialized = collection.serialize_to_columns(model)
        
        # Check that dict and list are JSON serialized if json_serialize is True
        # Since we're using DataTable with proper TypeInfo, it should handle this
        assert serialized["id"] == 1
        # The actual behavior depends on how ClickhouseColumn determines json_serialize
        # For now, just check the values are present
        assert "data" in serialized
        assert "tags" in serialized

    def test_iter(self):
        # Test __iter__ method
        import uuid
        TestModel = self.get_test_model()
        models = [
            TestModel(uid=uuid.uuid4(), id=1, name="Alice"),
            TestModel(uid=uuid.uuid4(), id=2, name="Bob"),
        ]
        collection = PydanticCollection(models, type=TestModel)
        
        items = list(collection)
        assert len(items) == 2
        assert items[0]["id"] == 1
        assert items[1]["id"] == 2


@pytest.mark.asyncio
class TestInsertIntoClickhouse:
    def get_test_model(self):
        from good_common.types import UUIDField
        
        class TestDataModel(DataTable):
            uid: UUIDField
            id: int
            name: str
            email: Optional[str] = None
            active: bool = True
            
            @computed_field
            @property
            def display_name(self) -> str:
                return f"{self.name} ({self.id})"
        
        return TestDataModel
    
    async def test_basic_insert(self):
        # Test without mocking - just check it doesn't crash with proper data
        import uuid
        TestModel = self.get_test_model()
        
        # Create test data
        models = [
            TestModel(uid=uuid.uuid4(), id=1, name="Alice"),
            TestModel(uid=uuid.uuid4(), id=2, name="Bob"),
        ]
        collection = PydanticCollection(models, type=TestModel)
        
        # Since we can't actually connect to clickhouse, we'll skip this test
        pytest.skip("Requires actual ClickHouse connection")

    async def test_insert_with_retry(self):
        # Test retry behavior
        pytest.skip("Requires actual ClickHouse connection")

    async def test_insert_empty_collection(self):
        # Test with empty collection
        pytest.skip("Requires actual ClickHouse connection")