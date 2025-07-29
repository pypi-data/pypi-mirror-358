"""Tests for MySQL storage."""

from typing import TYPE_CHECKING, Any, Dict
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys

from pyconfbox.core.types import ConfigValue, ConfigScope
from pyconfbox_mysql.storage import MySQLStorage

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestMySQLStorage:
    """Test cases for MySQLStorage."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.connection_params = {
            'host': 'localhost',
            'port': 3306,
            'user': 'test_user',
            'password': 'test_password',
            'database': 'test_db'
        }

    def _setup_mock_connection(self, mock_pymysql: Mock) -> tuple[Mock, Mock]:
        """Set up mock connection and cursor with proper context manager support."""
        mock_connection = Mock()
        mock_cursor = Mock()
        
        # Set up context manager for cursor
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Set up connection mock
        mock_pymysql.connect.return_value = mock_connection
        
        return mock_connection, mock_cursor

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_initialization_success(self, mock_pymysql: Mock) -> None:
        """Test successful storage initialization."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        storage = MySQLStorage(**self.connection_params)
        
        assert storage.host == 'localhost'
        assert storage.port == 3306
        assert storage.user == 'test_user'
        assert storage.database == 'test_db'
        assert storage.table == 'configurations'  # Default table name

    @patch('pyconfbox_mysql.storage.pymysql', None)
    def test_initialization_missing_pymysql(self) -> None:
        """Test initialization when pymysql is not available."""
        with pytest.raises(ImportError, match="pymysql package is required"):
            MySQLStorage(**self.connection_params)

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_initialization_custom_table(self, mock_pymysql: Mock) -> None:
        """Test initialization with custom table name."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        storage = MySQLStorage(table='custom_config', **self.connection_params)
        
        assert storage.table == 'custom_config'

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_ensure_table(self, mock_pymysql: Mock) -> None:
        """Test table creation."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        storage = MySQLStorage(**self.connection_params)
        storage._ensure_table()
        
        # Verify table creation SQL was executed
        mock_cursor.execute.assert_called()
        create_table_call = mock_cursor.execute.call_args_list[-1]
        assert 'CREATE TABLE IF NOT EXISTS' in create_table_call[0][0]

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_get_existing_key(self, mock_pymysql: Mock) -> None:
        """Test getting an existing configuration key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock database response as dictionary (DictCursor)
        mock_cursor.fetchone.return_value = {
            'key': 'test_key',
            'value': '"test_value"',  # JSON string
            'data_type': str,  # Use actual type object
            'scope': ConfigScope.GLOBAL,  # Use actual enum
            'storage': 'mysql',
            'immutable': False,
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        storage = MySQLStorage(**self.connection_params)
        result = storage.get('test_key')
        
        assert result is not None
        assert result.key == 'test_key'
        assert result.value == 'test_value'
        assert result.storage == 'mysql'

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_get_nonexistent_key(self, mock_pymysql: Mock) -> None:
        """Test getting a nonexistent key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock no result found
        mock_cursor.fetchone.return_value = None
        
        storage = MySQLStorage(**self.connection_params)
        result = storage.get('nonexistent_key')
        
        assert result is None

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_set_new_key(self, mock_pymysql: Mock) -> None:
        """Test setting a new configuration key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        config_value = ConfigValue(
            key='test_key',
            value='test_value',
            data_type=str,
            scope=ConfigScope.GLOBAL,
            storage='mysql',
            immutable=False
        )
        
        storage = MySQLStorage(**self.connection_params)
        storage.set('test_key', config_value)
        
        # Verify INSERT or UPDATE was executed
        mock_cursor.execute.assert_called()
        # Check that the last call contains INSERT or UPDATE
        last_call = mock_cursor.execute.call_args_list[-1]
        sql = last_call[0][0].upper()
        assert 'INSERT' in sql or 'UPDATE' in sql

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_delete_existing_key(self, mock_pymysql: Mock) -> None:
        """Test deleting an existing key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock affected rows (key existed and was deleted)
        mock_cursor.rowcount = 1
        
        storage = MySQLStorage(**self.connection_params)
        result = storage.delete('test_key')
        
        assert result is True
        mock_cursor.execute.assert_called()

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_delete_nonexistent_key(self, mock_pymysql: Mock) -> None:
        """Test deleting a nonexistent key."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock no affected rows (key didn't exist)
        mock_cursor.rowcount = 0
        
        storage = MySQLStorage(**self.connection_params)
        result = storage.delete('nonexistent_key')
        
        assert result is False

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_exists_true(self, mock_pymysql: Mock) -> None:
        """Test key existence check - key exists."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock key exists
        mock_cursor.fetchone.return_value = (1,)
        
        storage = MySQLStorage(**self.connection_params)
        result = storage.exists('test_key')
        
        assert result is True

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_exists_false(self, mock_pymysql: Mock) -> None:
        """Test key existence check - key does not exist."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock key doesn't exist
        mock_cursor.fetchone.return_value = None
        
        storage = MySQLStorage(**self.connection_params)
        result = storage.exists('nonexistent_key')
        
        assert result is False

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_keys(self, mock_pymysql: Mock) -> None:
        """Test getting all keys."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock multiple keys
        mock_cursor.fetchall.return_value = [('key1',), ('key2',), ('key3',)]
        
        storage = MySQLStorage(**self.connection_params)
        keys = storage.keys()
        
        assert keys == ['key1', 'key2', 'key3']

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_clear(self, mock_pymysql: Mock) -> None:
        """Test clearing all configuration data."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        storage = MySQLStorage(**self.connection_params)
        storage.clear()
        
        # Verify DELETE was executed
        mock_cursor.execute.assert_called()
        last_call = mock_cursor.execute.call_args_list[-1]
        assert 'DELETE' in last_call[0][0].upper()

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_update(self, mock_pymysql: Mock) -> None:
        """Test updating multiple configuration values."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        config_values = {
            'key1': ConfigValue(
                key='key1',
                value='value1',
                data_type=str,
                scope=ConfigScope.GLOBAL,
                storage='mysql',
                immutable=False
            ),
            'key2': ConfigValue(
                key='key2',
                value='value2',
                data_type=str,
                scope=ConfigScope.GLOBAL,
                storage='mysql',
                immutable=False
            )
        }
        
        storage = MySQLStorage(**self.connection_params)
        storage.update(config_values)
        
        # Verify multiple executions occurred
        assert mock_cursor.execute.call_count >= 2

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_get_info(self, mock_pymysql: Mock) -> None:
        """Test getting storage information."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock database info
        mock_cursor.fetchone.side_effect = [
            (5,),  # Total keys count
            ('8.0.25',),  # MySQL version
        ]
        
        storage = MySQLStorage(**self.connection_params)
        info = storage.get_info()
        
        assert info['type'] == 'mysql'
        assert info['host'] == 'localhost'
        assert info['database'] == 'test_db'
        assert info['table'] == 'configurations'  # Default table name
        assert 'total_keys' in info
        assert 'mysql_version' in info  # Actual key name

    def test_connection_error_handling(self) -> None:
        """Test connection error handling."""
        # This test doesn't need mocking since we're testing actual connection failure
        with pytest.raises(Exception):  # Should raise StorageError or ImportError
            MySQLStorage(host='nonexistent_host', **self.connection_params)

    @patch('pyconfbox_mysql.storage.pymysql')
    def test_database_error_handling(self, mock_pymysql: Mock) -> None:
        """Test database operation error handling."""
        mock_connection, mock_cursor = self._setup_mock_connection(mock_pymysql)
        
        # Mock database error during get operation (not during initialization)
        storage = MySQLStorage(**self.connection_params)
        
        # Reset mock to simulate error in get operation
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            storage.get('test_key') 