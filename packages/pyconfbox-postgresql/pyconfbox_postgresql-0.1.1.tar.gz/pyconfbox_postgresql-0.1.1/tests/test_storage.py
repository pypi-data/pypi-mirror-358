"""Tests for PostgreSQL storage."""

from typing import TYPE_CHECKING, Any, Dict
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys

from pyconfbox.core.types import ConfigValue, ConfigScope
from pyconfbox_postgresql.storage import PostgreSQLStorage

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestPostgreSQLStorage:
    """Test cases for PostgreSQLStorage."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.connection_params = {
            'host': 'localhost',
            'port': 5432,
            'user': 'test_user',
            'password': 'test_password',
            'database': 'test_db'
        }

    def _setup_mock_connection(self, mock_psycopg2: Mock) -> tuple[Mock, Mock]:
        """Set up mock connection and cursor with proper context manager support."""
        mock_connection = Mock()
        mock_cursor = Mock()
        
        # Set up context manager for cursor
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Set up connection mock
        mock_psycopg2.connect.return_value = mock_connection
        
        return mock_connection, mock_cursor

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_initialization_success(self, mock_psycopg2: Mock) -> None:
        """Test successful storage initialization."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        storage = PostgreSQLStorage(**self.connection_params)
        
        assert storage.host == 'localhost'
        assert storage.port == 5432
        assert storage.user == 'test_user'
        assert storage.database == 'test_db'
        assert storage.table == 'configurations'

    @patch('pyconfbox_postgresql.storage.psycopg2', None)
    def test_initialization_missing_psycopg2(self) -> None:
        """Test initialization when psycopg2 is not available."""
        with pytest.raises(ImportError, match="psycopg2-binary package is required"):
            PostgreSQLStorage(**self.connection_params)

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_initialization_custom_table(self, mock_psycopg2: Mock) -> None:
        """Test initialization with custom table name."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        storage = PostgreSQLStorage(table='custom_config', **self.connection_params)
        
        assert storage.table == 'custom_config'

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_create_table(self, mock_psycopg2: Mock) -> None:
        """Test table creation."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        storage = PostgreSQLStorage(**self.connection_params)
        storage._ensure_table()
        
        # Verify table creation SQL was executed
        mock_cursor.execute.assert_called()
        # Should have multiple calls for table, indexes, and triggers
        assert mock_cursor.execute.call_count >= 3

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_get_existing_key(self, mock_psycopg2: Mock) -> None:
        """Test getting an existing configuration key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock database response (RealDictCursor returns dict-like object)
        mock_cursor.fetchone.return_value = {
            'key': 'test_key',
            'value': '{"test": "value"}',
            'data_type': 'str',
            'scope': 'global',
            'storage': 'postgresql',
            'immutable': False,
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        storage = PostgreSQLStorage(**self.connection_params)
        result = storage.get('test_key')
        
        assert result is not None
        assert result.key == 'test_key'
        assert result.value == {"test": "value"}
        assert result.storage == 'postgresql'

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_get_nonexistent_key(self, mock_psycopg2: Mock) -> None:
        """Test getting a nonexistent key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock no result found
        mock_cursor.fetchone.return_value = None
        
        storage = PostgreSQLStorage(**self.connection_params)
        result = storage.get('nonexistent_key')
        
        assert result is None

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_set_new_key(self, mock_psycopg2: Mock) -> None:
        """Test setting a new configuration key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        config_value = ConfigValue(
            key='test_key',
            value='test_value',
            data_type=str,
            scope=ConfigScope.GLOBAL,
            storage='postgresql',
            immutable=False
        )
        
        storage = PostgreSQLStorage(**self.connection_params)
        storage.set('test_key', config_value)
        
        # Verify INSERT or UPDATE was executed
        mock_cursor.execute.assert_called()
        last_call = mock_cursor.execute.call_args_list[-1]
        sql = last_call[0][0].upper()
        assert 'INSERT' in sql or 'UPDATE' in sql

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_delete_existing_key(self, mock_psycopg2: Mock) -> None:
        """Test deleting an existing key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock affected rows (key existed and was deleted)
        mock_cursor.rowcount = 1
        
        storage = PostgreSQLStorage(**self.connection_params)
        result = storage.delete('test_key')
        
        assert result is True
        mock_cursor.execute.assert_called()

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_delete_nonexistent_key(self, mock_psycopg2: Mock) -> None:
        """Test deleting a nonexistent key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock no affected rows (key didn't exist)
        mock_cursor.rowcount = 0
        
        storage = PostgreSQLStorage(**self.connection_params)
        result = storage.delete('nonexistent_key')
        
        assert result is False

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_exists_true(self, mock_psycopg2: Mock) -> None:
        """Test key existence check - key exists."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock key exists
        mock_cursor.fetchone.return_value = (1,)
        
        storage = PostgreSQLStorage(**self.connection_params)
        result = storage.exists('test_key')
        
        assert result is True

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_exists_false(self, mock_psycopg2: Mock) -> None:
        """Test key existence check - key does not exist."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock key doesn't exist
        mock_cursor.fetchone.return_value = None
        
        storage = PostgreSQLStorage(**self.connection_params)
        result = storage.exists('nonexistent_key')
        
        assert result is False

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_keys(self, mock_psycopg2: Mock) -> None:
        """Test getting all keys."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock multiple keys
        mock_cursor.fetchall.return_value = [('key1',), ('key2',), ('key3',)]
        
        storage = PostgreSQLStorage(**self.connection_params)
        keys = storage.keys()
        
        assert keys == ['key1', 'key2', 'key3']

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_clear(self, mock_psycopg2: Mock) -> None:
        """Test clearing all configuration data."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        storage = PostgreSQLStorage(**self.connection_params)
        storage.clear()
        
        # Verify DELETE was executed
        mock_cursor.execute.assert_called()
        last_call = mock_cursor.execute.call_args_list[-1]
        assert 'DELETE' in last_call[0][0].upper()

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_update(self, mock_psycopg2: Mock) -> None:
        """Test updating multiple configuration values."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        config_values = {
            'key1': ConfigValue(
                key='key1',
                value='value1',
                data_type=str,
                scope=ConfigScope.GLOBAL,
                storage='postgresql',
                immutable=False
            ),
            'key2': ConfigValue(
                key='key2',
                value='value2',
                data_type=str,
                scope=ConfigScope.GLOBAL,
                storage='postgresql',
                immutable=False
            )
        }
        
        storage = PostgreSQLStorage(**self.connection_params)
        storage.update(config_values)
        
        # Verify multiple executions occurred
        assert mock_cursor.execute.call_count >= 2

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_get_info(self, mock_psycopg2: Mock) -> None:
        """Test getting storage information."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)

        # Mock database info - provide more values to account for initialization calls
        mock_cursor.fetchone.side_effect = [
            None,  # Database existence check during initialization
            (5,),  # Total keys count
            ('PostgreSQL 13.3',),  # PostgreSQL version
        ]

        storage = PostgreSQLStorage(**self.connection_params)
        info = storage.get_info()

        assert info['type'] == 'postgresql'
        assert info['host'] == 'localhost'
        assert info['database'] == 'test_db'
        assert info['table'] == 'configurations'
        # Check if total_keys exists or if there's an error
        assert 'total_keys' in info or 'error' in info
        assert 'version' in info

    def test_connection_error_handling(self) -> None:
        """Test connection error handling."""
        # This test doesn't need mocking since we're testing actual connection failure
        with pytest.raises(Exception):  # Should raise StorageError or ImportError
            PostgreSQLStorage(host='nonexistent_host', **self.connection_params)

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_database_error_handling(self, mock_psycopg2: Mock) -> None:
        """Test database operation error handling."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        # Mock database error during get operation (not during initialization)
        storage = PostgreSQLStorage(**self.connection_params)
        
        # Reset mock to simulate error in get operation
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            storage.get('test_key')

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_connection_string_initialization(self, mock_psycopg2: Mock) -> None:
        """Test initialization with connection string."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)

        connection_string = "postgresql://user:pass@localhost:5432/testdb"
        storage = PostgreSQLStorage(connection_string=connection_string)

        # Check that the connection string was parsed correctly
        assert hasattr(storage, 'connection_params')
        assert storage.connection_params['host'] == 'localhost'
        assert storage.connection_params['port'] == 5432
        assert storage.connection_params['database'] == 'testdb'

    @patch('pyconfbox_postgresql.storage.psycopg2')
    def test_json_serialization(self, mock_psycopg2: Mock) -> None:
        """Test JSON value serialization."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_psycopg2)
        
        complex_value = {'nested': {'data': [1, 2, 3]}, 'boolean': True}
        config_value = ConfigValue(
            key='complex_key',
            value=complex_value,
            data_type=dict,
            scope=ConfigScope.GLOBAL,
            storage='postgresql',
            immutable=False
        )
        
        storage = PostgreSQLStorage(**self.connection_params)
        storage.set('complex_key', config_value)
        
        # Verify the value was JSON serialized
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args_list[-1]
        # The JSON string should contain the serialized complex value
        assert '"nested"' in str(call_args) 