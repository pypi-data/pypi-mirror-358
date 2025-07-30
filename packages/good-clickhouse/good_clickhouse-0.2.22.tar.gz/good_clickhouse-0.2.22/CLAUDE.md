# Good ClickHouse Library

A ClickHouse database client with dependency injection support, Jinja2-based query templating, and comprehensive type mapping.

## Package Overview

good-clickhouse provides both synchronous and asynchronous ClickHouse clients with fast_depends integration for use in FastAPI and other frameworks. It features a powerful query builder using Jinja2 templates and automatic type conversion between Python and ClickHouse.

## Key Components

### Clients (`_client.py`)
- `Clickhouse`: Synchronous client
- `ClickhouseAsync`: Asynchronous client  
- `ClickhouseProvider`/`ClickhouseAsyncProvider`: Dependency injection providers
- Connection management with profiles and pooling

### Query Builder (`query.py`)
- `@query` decorator for creating reusable query components
- Jinja2 templating with custom filters and environment variables
- Composable queries that can call other queries
- Support for parameterized queries with automatic escaping

### Type System (`_types.py`)
- Comprehensive Python to ClickHouse type mapping
- Support for complex types: Arrays, Maps, Tuples, Nested
- DateTime64 with timezone support
- Nullable and LowCardinality types
- Custom type conversions

### Collection Management (`collection.py`)
- Higher-level abstractions for working with ClickHouse tables
- Batch operations and data management

### Local Database (`chdb.py`)
- Optional integration with chdb for local ClickHouse engine
- Useful for testing and development

## Usage Examples

### Basic Client Usage
```python
from good_clickhouse import ClickhouseAsyncProvider
from fast_depends import inject

@inject
async def get_data(
    ch: ClickhouseAsync = ClickhouseAsyncProvider(
        host="localhost",
        database="mydb"
    )
):
    return await ch.execute("SELECT * FROM users")
```

### Query Builder
```python
from good_clickhouse import query

@query
def get_users():
    '''
    SELECT *
    FROM users
    WHERE active = 1
    {% if name %}
        AND name = {{ name }}
    {% endif %}
    '''

# Use the query
result = await ch.execute(get_users(name="John"))
```

### Composable Queries
```python
@query
def base_filter():
    '''WHERE active = 1 AND deleted_at IS NULL'''

@query  
def get_recent_users():
    '''
    SELECT *
    FROM users
    {{ base_filter() }}
    AND created_at > now() - INTERVAL 7 DAY
    '''
```

## Type Mapping

The library automatically converts between Python and ClickHouse types:

- `int` → `Int64`
- `float` → `Float64`
- `str` → `String`
- `datetime` → `DateTime64(3)`
- `list[T]` → `Array(T)`
- `dict[K, V]` → `Map(K, V)`
- `Optional[T]` → `Nullable(T)`
- Custom types via `Annotated`

## Connection Profiles

Define reusable connection configurations:

```python
from good_clickhouse import ConnectionProfile

profile = ConnectionProfile(
    name="production",
    host="clickhouse.example.com",
    port=9000,
    database="analytics",
    username="user",
    password="pass"
)

client = ClickhouseAsyncProvider(profile=profile)
```

## Testing

The library includes comprehensive tests for:
- Client connectivity and operations
- Query builder functionality
- Type conversions
- Collection operations

Run tests with:
```bash
uv run pytest
```

## Environment Variables

The query builder supports environment variables in templates:
```sql
SELECT * FROM {{ env.TABLE_NAME }}
WHERE region = {{ env.AWS_REGION }}
```

## Best Practices

1. Use the query builder for complex queries to leverage templating
2. Prefer async clients for better performance
3. Use connection profiles for different environments
4. Leverage type annotations for automatic conversions
5. Use parameterized queries to prevent SQL injection

## Dependencies

- `clickhouse-connect`: Official ClickHouse Python driver
- `jinja2`: Template engine for queries
- `fast-depends`: Dependency injection
- `good-common`: Shared utilities
- Optional: `chdb` for local database support