import os
from unittest.mock import patch, MagicMock

import pytest

from good_clickhouse.chdb import (
    remote_table_secure,
    _inject_env_variable,
    remote_table_secure_ch_cloud,
)


class TestRemoteTableSecure:
    def test_basic_remote_table(self):
        # Test basic remote table SQL generation
        result = remote_table_secure(
            host="clickhouse.example.com",
            database="mydb",
            table="mytable",
            user="myuser",
            password="mypass"
        )
        
        expected = "remoteSecure('clickhouse.example.com', 'mydb', 'mytable', 'myuser', 'mypass')"
        assert str(result).strip() == expected

    def test_remote_table_with_defaults(self):
        # Test with minimal parameters
        result = remote_table_secure(
            host="localhost",
            database="default",
            table="test",
            user="default",
            password="secret"
        )
        
        expected = "remoteSecure('localhost', 'default', 'test', 'default', 'secret')"
        assert str(result).strip() == expected

    def test_remote_table_custom_host(self):
        # Test with custom host
        result = remote_table_secure(
            host="ch.example.com:8443",
            database="analytics",
            table="events",
            user="analyst",
            password="pass123"
        )
        
        expected = "remoteSecure('ch.example.com:8443', 'analytics', 'events', 'analyst', 'pass123')"
        assert str(result).strip() == expected


class TestInjectEnvVariable:
    def test_inject_env_variable(self, monkeypatch):
        # Test environment variable injection
        monkeypatch.setenv("TEST_VAR", "test_value")
        
        # _inject_env_variable returns a function, not the value directly
        inject_func = _inject_env_variable("TEST_VAR")
        result = inject_func()
        assert result == "test_value"

    def test_inject_missing_env_variable(self):
        # Test with missing environment variable
        inject_func = _inject_env_variable("MISSING_VAR")
        with pytest.raises(KeyError):
            inject_func()

    def test_inject_empty_env_variable(self, monkeypatch):
        # Test with empty environment variable
        monkeypatch.setenv("EMPTY_VAR", "")
        
        # Empty string is still a valid value
        inject_func = _inject_env_variable("EMPTY_VAR")
        result = inject_func()
        assert result == ""


class TestRemoteTableSecureChCloud:
    def test_ch_cloud_with_env_vars(self, monkeypatch):
        # Setup environment variables
        monkeypatch.setenv("CLICKHOUSE_CLOUD_HOST", "cloud.clickhouse.com")
        monkeypatch.setenv("CLICKHOUSE_CLOUD_PASSWORD", "cloud_password")
        
        # Call the function - it uses 'default' user hardcoded
        result = remote_table_secure_ch_cloud(
            database="cloud_db",
            table="cloud_table"
        )
        
        expected = "remoteSecure('cloud.clickhouse.com', 'cloud_db', 'cloud_table', 'default', 'cloud_password')"
        assert str(result).strip() == expected

    def test_ch_cloud_missing_host_env(self, monkeypatch):
        # Setup only password env var
        monkeypatch.setenv("CLICKHOUSE_CLOUD_PASSWORD", "cloud_password")
        
        # Should raise error for missing host
        with pytest.raises(KeyError):
            remote_table_secure_ch_cloud(
                database="cloud_db",
                table="cloud_table"
            )

    def test_ch_cloud_missing_password_env(self, monkeypatch):
        # Setup only host env var
        monkeypatch.setenv("CLICKHOUSE_CLOUD_HOST", "cloud.clickhouse.com")
        
        # Should raise error for missing password
        with pytest.raises(KeyError):
            remote_table_secure_ch_cloud(
                database="cloud_db",
                table="cloud_table"
            )

    def test_ch_cloud_with_explicit_params(self):
        # Test that function uses environment variables through Depends
        # The function doesn't actually accept host/password as direct params
        # because they're injected via Depends
        import os
        os.environ["CLICKHOUSE_CLOUD_HOST"] = "explicit.clickhouse.com"
        os.environ["CLICKHOUSE_CLOUD_PASSWORD"] = "explicit_password"
        
        try:
            result = remote_table_secure_ch_cloud(
                database="cloud_db",
                table="cloud_table"
            )
            
            expected = "remoteSecure('explicit.clickhouse.com', 'cloud_db', 'cloud_table', 'default', 'explicit_password')"
            assert str(result).strip() == expected
        finally:
            # Clean up
            os.environ.pop("CLICKHOUSE_CLOUD_HOST", None)
            os.environ.pop("CLICKHOUSE_CLOUD_PASSWORD", None)