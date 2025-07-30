import pytest
from jinja2 import Environment, StrictUndefined
from good_clickhouse.query import SQL, sql


@sql
def example_query(table_name: str):
    """
    select * from {{ table_name }};
    """
    pass


def test_query_registration():
    # Check that the query was registered correctly
    assert "example_query" in SQL.instance_registry
    registered_query = SQL.instance_registry["example_query"]
    assert isinstance(registered_query, SQL)
    # Normalize whitespace for comparison
    assert registered_query.template.strip() == "select * from {{ table_name }};"


def test_query_rendering():
    # Test the rendering of the query
    rendered_query = example_query("my_table")
    assert rendered_query == "select * from my_table;"


def test_query_parameters():
    # Test that the query correctly extracts parameters from the signature
    registered_query = SQL.instance_registry["example_query"]
    assert registered_query.parameters == ["table_name"]


def test_env_patching():
    # Test that the environment is correctly patched with the query globals
    env = Environment(undefined=StrictUndefined)
    SQL.patch_env(env)
    assert "example_query" in env.globals
    assert env.globals["example_query"] == SQL.instance_registry["example_query"]


@sql
def complex_query(table_name: str, columns: list[str], filters: dict[str, str]):
    """
    select {{ columns | join(', ') }}
    from {{ table_name }}
    where {% for key, value in filters.items() -%}
            {{ key }} {{ value }}{% if not loop.last %} and {% endif %}
          {%- endfor %};
    """


def test_complex_query_rendering():
    # Test the complex query rendering
    columns = ["id", "name", "age"]
    filters = {"age": "> 20", "name": "like 'John%'"}
    rendered_query = complex_query("users", columns, filters)
    expected_query = (
        "select id, name, age\nfrom users\nwhere age > 20 and name like 'John%';"
    )
    assert rendered_query.strip() == expected_query.strip()


def test_empty_render_function():
    # Test rendering with an empty context
    with pytest.raises(TypeError):
        example_query()  # This should raise a TypeError due to missing argument


def test_missing_template_docstring():
    # Test that an error is raised if a function has no docstring
    with pytest.raises(TypeError):

        @sql
        def invalid_query(table_name: str):
            pass
