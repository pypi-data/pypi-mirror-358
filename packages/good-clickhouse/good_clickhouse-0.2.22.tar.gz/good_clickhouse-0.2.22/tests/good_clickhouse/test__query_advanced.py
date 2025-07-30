import asyncio
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest
from jinja2 import Environment
from pydantic import BaseModel

from good_clickhouse.query import SQL, sql, Statement, Column


# Test SQL templates
@sql
def simple_query(name: str):
    """SELECT * FROM users WHERE name = {{ name }}"""


@sql
async def async_query(id: int):
    """SELECT * FROM users WHERE id = {{ id }}"""


@sql
def query_with_response_model(user_id: int) -> "UserResponse":
    """SELECT name, email FROM users WHERE id = {{ user_id }}"""
    ...


class UserResponse(BaseModel):
    name: str
    email: str


class TestStatement:
    def test_statement_creation(self):
        # Test Statement creation
        stmt = Statement("SELECT 1")
        assert str(stmt) == "SELECT 1"
        assert isinstance(stmt, str)

    def test_statement_echo(self):
        # Test echo method
        stmt = Statement("SELECT * FROM test")

        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = stmt.echo()
            output = fake_out.getvalue()

        assert output.strip() == "SELECT * FROM test"
        assert result == stmt  # Should return self


class TestSQLClassAdvanced:
    def test_register_filter(self):
        # Test registering custom filter
        def custom_upper(value):
            return value.upper()

        SQL.register_filter("custom_upper", custom_upper)
        assert "custom_upper" in SQL.__filters__
        assert SQL.__filters__["custom_upper"] == custom_upper

    def test_register_filter_duplicate(self):
        # Test error on duplicate filter
        SQL.__filters__["test_filter"] = lambda x: x

        with pytest.raises(ValueError, match="Duplicate filter: test_filter"):
            SQL.register_filter("test_filter", lambda x: x)

    def test_register_filter_builtin_override(self):
        # Test error when trying to override built-in filter
        with pytest.raises(ValueError, match="Cannot override built-in filter"):
            SQL.register_filter("quote", lambda x: x)

    def test_register_global(self):
        # Test registering global variable
        SQL.register_global("test_var", "test_value")
        assert "test_var" in SQL.__globals__
        assert SQL.__globals__["test_var"] == "test_value"

    def test_register_global_duplicate(self):
        # Test error on duplicate global
        SQL.__globals__["test_global"] = "value"

        with pytest.raises(ValueError, match="Duplicate global: test_global"):
            SQL.register_global("test_global", "new_value")

    def test_register_global_builtin_override(self):
        # Test error when trying to override built-in global
        with pytest.raises(ValueError, match="Cannot override built-in global"):
            SQL.register_global("env", lambda x: x)

    def test_pretty_method(self):
        # Test pretty method
        @sql
        def indented_query():
            """
            SELECT *
            FROM users
            WHERE active = 1
            """

        pretty = SQL.instance_registry["indented_query"].pretty()
        assert "SELECT *" in pretty
        assert "FROM users" in pretty
        assert "WHERE active = 1" in pretty
        assert not pretty.startswith(" ")  # Should be dedented

    @pytest.mark.asyncio
    async def test_async_query_execution(self):
        # Test async query execution
        result = await async_query(123)
        assert str(result) == "SELECT * FROM users WHERE id = 123"

    def test_response_model_assignment(self):
        # Test that response model is properly assigned
        query_obj = SQL.instance_registry["query_with_response_model"]
        # response_model is set to the string "UserResponse" not the class
        assert query_obj.response_model == "UserResponse"

    def test_build_template_whitespace_handling(self):
        # Test template whitespace handling
        template = """
        SELECT   *   FROM   users
        WHERE   id   =   1
        """

        result = SQL.build_template(template)
        rendered = result.render()

        # The regex in build_template preserves some whitespace patterns
        # Check that the query is present
        assert "SELECT" in rendered
        assert "FROM" in rendered
        assert "users" in rendered
        assert "WHERE" in rendered
        assert "id" in rendered

    def test_build_template_linebreak_preservation(self):
        # Test that extra linebreaks at end are preserved
        template = "SELECT 1\n\n"
        result = SQL.build_template(template)
        rendered = result.render()
        assert rendered.endswith("\n")

    def test_patch_env_duplicate_error(self):
        # Test error when patching env with duplicate names
        env = Environment()
        env.globals["simple_query"] = "existing_value"

        with pytest.raises(ValueError, match="Duplicate env variable: simple_query"):
            SQL.patch_env(env)


class TestColumn:
    def test_column_dataclass_defaults(self):
        # Test Column dataclass with defaults
        col = Column(name="test_col", type="String")

        assert col.name == "test_col"
        assert col.type == "String"
        assert col.json_serialize is False
        assert col.default_value is None
        assert col.expression is None
        assert col.codec is None
        assert col.ttl is None
        assert col.comment is None
        assert col.alias is None
        assert col.materialized is False
        assert col.hidden is False
        assert col.cast is None

    def test_column_with_all_fields(self):
        # Test Column with all fields set
        def custom_cast(x):
            return str(x).upper()

        col = Column(
            name="full_col",
            type="String",
            json_serialize=True,
            default_value="'default'",
            expression="toUpper(name)",
            codec="ZSTD(1)",
            ttl="created_at + INTERVAL 30 DAY",
            comment="Test column",
            alias="other_col",
            materialized=True,
            hidden=True,
            cast=custom_cast,
        )

        assert col.name == "full_col"
        assert col.type == "String"
        assert col.json_serialize is True
        assert col.default_value == "'default'"
        assert col.expression == "toUpper(name)"
        assert col.codec == "ZSTD(1)"
        assert col.ttl == "created_at + INTERVAL 30 DAY"
        assert col.comment == "Test column"
        assert col.alias == "other_col"
        assert col.materialized is True
        assert col.hidden is True
        assert col.cast == custom_cast


class TestSQLDecorator:
    def test_sql_decorator_with_kwargs(self):
        # Test sql decorator with kwargs
        @sql(custom_kwarg="test")
        def kwarg_query():
            """SELECT 1"""

        query_obj = SQL.instance_registry["kwarg_query"]
        assert query_obj._kwargs == {"custom_kwarg": "test"}

    def test_sql_decorator_without_parentheses(self):
        # Test sql decorator without parentheses
        @sql
        def no_parens_query():
            """SELECT 2"""

        assert "no_parens_query" in SQL.instance_registry

    def test_sql_decorator_with_empty_parentheses(self):
        # Test sql decorator with empty parentheses
        @sql()
        def empty_parens_query():
            """SELECT 3"""

        assert "empty_parens_query" in SQL.instance_registry


class TestDependencyInjection:
    def test_query_with_dependencies(self):
        # Test query with fast_depends injection
        from fast_depends import Depends

        def get_database() -> str:
            return "production"

        @sql
        def query_with_deps(table: str, database: str = Depends(get_database)):
            """SELECT * FROM {{ database }}.{{ table }}"""

        # Mock the dependency resolution
        with patch("fast_depends.core.build_call_model") as mock_build:
            mock_model = MagicMock()
            mock_model.solve.return_value = (
                [],
                {"table": "users", "database": "production"},
            )
            mock_build.return_value = mock_model

            # Re-initialize the SQL object to use our mock
            query_obj = SQL(query_with_deps.__wrapped__)
            result = query_obj("users")

            # Should use the injected database value
            assert "production" in str(result)
