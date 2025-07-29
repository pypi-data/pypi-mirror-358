"""Tests for MongoDB storage."""

from typing import TYPE_CHECKING, Any, Dict
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from pyconfbox.core.types import ConfigValue, ConfigScope
from pyconfbox_mongodb.storage import MongoDBStorage
from pyconfbox.core.exceptions import StorageError

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestMongoDBStorage:
    """Test cases for MongoDBStorage."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.connection_params = {
            'host': 'localhost',
            'port': 27017,
            'database': 'test_db'
        }

    def _setup_mock_connection(self, mock_mongo_client: Mock) -> tuple[Mock, Mock, Mock]:
        """Set up mock MongoDB connection hierarchy."""
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_admin = Mock()
        
        # Set up the client mock
        mock_mongo_client.return_value = mock_client
        
        # Configure __getitem__ to work with Mock
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        
        # Mock admin command for connection test
        mock_client.admin = mock_admin
        mock_admin.command = Mock(return_value={'ok': 1})
        
        # Mock collection methods for index creation
        mock_collection.create_index = Mock()
        
        return mock_client, mock_db, mock_collection

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_initialization_success(self, mock_mongo_client: Mock) -> None:
        """Test successful storage initialization."""
        # Create a complete mock hierarchy
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_admin = Mock()
        
        # Set up the client mock
        mock_mongo_client.return_value = mock_client
        
        # Configure __getitem__ to work with Mock
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        
        # Mock admin command for connection test
        mock_client.admin = mock_admin
        mock_admin.command = Mock(return_value={'ok': 1})
        
        # Mock collection methods for index creation
        mock_collection.create_index = Mock()
        
        storage = MongoDBStorage(**self.connection_params)
        
        assert storage.host == 'localhost'
        assert storage.port == 27017
        assert storage.database_name == 'test_db'
        assert storage.collection_name == 'configurations'
        
        # Verify connection was attempted
        mock_mongo_client.assert_called_once()
        mock_admin.command.assert_called_once_with('ping')

    def test_initialization_missing_pymongo(self) -> None:
        """Test initialization when pymongo is not available."""
        # Patch the import at the module level before importing
        with patch.dict('sys.modules', {'pymongo': None, 'pymongo.MongoClient': None}):
            # Also patch the storage module's pymongo reference
            with patch('pyconfbox_mongodb.storage.pymongo', None):
                with pytest.raises(ImportError, match="pymongo package is required"):
                    MongoDBStorage(**self.connection_params)

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_initialization_with_uri(self, mock_mongo_client: Mock) -> None:
        """Test initialization with MongoDB URI."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        uri = "mongodb://localhost:27017/test_db"
        storage = MongoDBStorage(uri=uri, database='test_db')
        
        mock_mongo_client.assert_called_once_with(uri)

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_initialization_custom_collection(self, mock_mongo_client: Mock) -> None:
        """Test initialization with custom collection name."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        storage = MongoDBStorage(collection='custom_config', **self.connection_params)
        
        assert storage.collection_name == 'custom_config'

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_get_existing_key(self, mock_mongo_client: Mock) -> None:
        """Test getting an existing configuration key."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        # Mock MongoDB response
        mock_collection.find_one.return_value = {
            '_id': 'test_key',
            'key': 'test_key',
            'value': 'test_value',
            'data_type': str,
            'scope': 'global',
            'storage': 'mongodb',
            'immutable': False,
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        
        storage = MongoDBStorage(**self.connection_params)
        result = storage.get('test_key')
        
        assert result is not None
        assert result.key == 'test_key'
        assert result.value == 'test_value'
        assert result.data_type is str
        assert result.scope == ConfigScope.GLOBAL
        assert result.storage == 'mongodb'
        assert result.immutable is False

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_get_nonexistent_key(self, mock_mongo_client: Mock) -> None:
        """Test getting a nonexistent key."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        mock_collection.find_one.return_value = None
        
        storage = MongoDBStorage(**self.connection_params)
        result = storage.get('nonexistent_key')
        
        assert result is None

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_set_new_key(self, mock_mongo_client: Mock) -> None:
        """Test setting a new configuration key."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        config_value = ConfigValue(
            key='test_key',
            value='test_value',
            data_type=str,
            scope=ConfigScope.GLOBAL,
            storage='mongodb',
            immutable=False
        )
        
        storage = MongoDBStorage(**self.connection_params)
        storage.set('test_key', config_value)
        
        # Verify upsert operation was called
        mock_collection.replace_one.assert_called_once()
        call_args = mock_collection.replace_one.call_args
        assert call_args[0][0] == {'key': 'test_key'}  # Filter
        assert call_args[1]['upsert'] is True

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_delete_existing_key(self, mock_mongo_client: Mock) -> None:
        """Test deleting an existing key."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        mock_collection.delete_one.return_value.deleted_count = 1
        
        storage = MongoDBStorage(**self.connection_params)
        result = storage.delete('test_key')
        
        assert result is True
        mock_collection.delete_one.assert_called_once_with({'key': 'test_key'})

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_delete_nonexistent_key(self, mock_mongo_client: Mock) -> None:
        """Test deleting a nonexistent key."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        mock_collection.delete_one.return_value.deleted_count = 0
        
        storage = MongoDBStorage(**self.connection_params)
        result = storage.delete('nonexistent_key')
        
        assert result is False

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_exists_true(self, mock_mongo_client: Mock) -> None:
        """Test key existence check - key exists."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        mock_collection.count_documents.return_value = 1
        
        storage = MongoDBStorage(**self.connection_params)
        result = storage.exists('test_key')
        
        assert result is True
        mock_collection.count_documents.assert_called_once_with({'key': 'test_key'}, limit=1)

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_exists_false(self, mock_mongo_client: Mock) -> None:
        """Test key existence check - key does not exist."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        mock_collection.count_documents.return_value = 0
        
        storage = MongoDBStorage(**self.connection_params)
        result = storage.exists('nonexistent_key')
        
        assert result is False

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_keys(self, mock_mongo_client: Mock) -> None:
        """Test getting all keys."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        # Mock cursor with multiple keys
        mock_collection.find.return_value = [
            {'key': 'key1'},
            {'key': 'key2'},
            {'key': 'key3'}
        ]
        
        storage = MongoDBStorage(**self.connection_params)
        keys = storage.keys()
        
        assert keys == ['key1', 'key2', 'key3']

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_clear(self, mock_mongo_client: Mock) -> None:
        """Test clearing all configuration data."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        storage = MongoDBStorage(**self.connection_params)
        storage.clear()
        
        # Verify delete_many was called
        mock_collection.delete_many.assert_called_once_with({})

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_update(self, mock_mongo_client: Mock) -> None:
        """Test updating multiple configuration values."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        config_values = {
            'key1': ConfigValue(
                key='key1',
                value='value1',
                data_type=str,
                scope=ConfigScope.GLOBAL,
                storage='mongodb',
                immutable=False
            ),
            'key2': ConfigValue(
                key='key2',
                value='value2',
                data_type=str,
                scope=ConfigScope.GLOBAL,
                storage='mongodb',
                immutable=False
            )
        }
        
        storage = MongoDBStorage(**self.connection_params)
        storage.update(config_values)
        
        # Verify bulk_write was called instead of individual replace_one calls
        mock_collection.bulk_write.assert_called_once()
        call_args = mock_collection.bulk_write.call_args[0][0]  # operations list
        assert len(call_args) == 2  # Two operations for two keys

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_get_info(self, mock_mongo_client: Mock) -> None:
        """Test getting storage information."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        # Mock database command and server info
        mock_db.command.return_value = {'count': 42, 'size': 1024, 'storageSize': 2048, 'indexSizes': {'_id_': 32, 'key_1': 16}}
        mock_client.server_info.return_value = {'version': '5.0.0'}
        
        storage = MongoDBStorage(**self.connection_params)
        info = storage.get_info()
        
        assert info['type'] == 'mongodb'
        assert info['host'] == 'localhost'
        assert info['port'] == 27017
        assert info['database'] == 'test_db'
        assert info['collection'] == 'configurations'
        assert info['total_keys'] == 42
        assert info['mongodb_version'] == '5.0.0'
        assert info['collection_size'] == 1024
        assert info['storage_size'] == 2048
        assert info['indexes'] == 2

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_connection_error_handling(self, mock_mongo_client: Mock) -> None:
        """Test connection error handling."""
        # Mock connection error
        mock_mongo_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(StorageError, match="Failed to connect to MongoDB"):
            MongoDBStorage(**self.connection_params)

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_database_error_handling(self, mock_mongo_client: Mock) -> None:
        """Test database operation error handling."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        # Mock database error during get operation
        mock_collection.find_one.side_effect = Exception("Database error")
        
        storage = MongoDBStorage(**self.connection_params)
        
        with pytest.raises(StorageError, match="Failed to get value from MongoDB"):
            storage.get('test_key')

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_complex_value_serialization(self, mock_mongo_client: Mock) -> None:
        """Test complex value serialization."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        complex_value = {'nested': {'data': [1, 2, 3]}, 'boolean': True}
        config_value = ConfigValue(
            key='complex_key',
            value=complex_value,
            data_type=dict,
            scope=ConfigScope.GLOBAL,
            storage='mongodb',
            immutable=False
        )
        
        storage = MongoDBStorage(**self.connection_params)
        storage.set('complex_key', config_value)
        
        # Verify the complex value was stored
        mock_collection.replace_one.assert_called_once()
        call_args = mock_collection.replace_one.call_args
        stored_doc = call_args[0][1]  # The document being stored
        assert stored_doc['value'] == complex_value

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_index_creation(self, mock_mongo_client: Mock) -> None:
        """Test index creation on initialization."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        storage = MongoDBStorage(**self.connection_params)
        
        # Verify indexes were created
        assert mock_collection.create_index.call_count >= 4
        index_calls = [call[0][0] for call in mock_collection.create_index.call_args_list]
        assert "key" in index_calls
        assert "scope" in index_calls
        assert "storage" in index_calls
        assert "created_at" in index_calls

    @patch('pyconfbox_mongodb.storage.MongoClient')
    def test_authentication(self, mock_mongo_client: Mock) -> None:
        """Test MongoDB authentication."""
        mock_client, mock_db, mock_collection = self._setup_mock_connection(mock_mongo_client)
        
        storage = MongoDBStorage(
            username='testuser',
            password='testpass',
            **self.connection_params
        )
        
        # Verify connection was attempted with authentication
        mock_mongo_client.assert_called_once()
        call_args = mock_mongo_client.call_args[0][0]  # First positional argument (URI)
        assert 'testuser:testpass' in call_args 