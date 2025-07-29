"""MongoDB storage backend for PyConfBox."""

from typing import Any, Dict, List, Optional

try:
    import pymongo
    from bson import ObjectId
    from pymongo import MongoClient
except ImportError:
    pymongo = None
    MongoClient = None
    ObjectId = None

try:
    from pyconfbox.core.exceptions import StorageError
    from pyconfbox.core.types import ConfigValue
    from pyconfbox.storage.base import BaseStorage
except ImportError:
    raise ImportError("pyconfbox is required for pyconfbox-mongodb plugin")


class MongoDBStorage(BaseStorage):
    """MongoDB database storage backend for PyConfBox.

    This storage backend uses MongoDB database to persist configuration values.
    Requires pymongo package to be installed.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        database: str = "pyconfbox",
        collection: str = "configurations",
        username: Optional[str] = None,
        password: Optional[str] = None,
        uri: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize MongoDB storage.

        Args:
            host: MongoDB server host.
            port: MongoDB server port.
            database: Database name.
            collection: Collection name for storing configurations.
            username: MongoDB username (optional).
            password: MongoDB password (optional).
            uri: MongoDB connection URI (alternative to individual params).
            **kwargs: Additional connection parameters.
        """
        super().__init__()

        if pymongo is None:
            raise ImportError(
                "pymongo package is required for MongoDB storage. "
                "Install it with: pip install pymongo"
            )

        self.host = host
        self.port = port
        self.database_name = database
        self.collection_name = collection
        self.username = username
        self.password = password
        self.uri = uri
        self.connection_params = kwargs

        self._client = None
        self._database = None
        self._collection = None
        self._ensure_connection()
        self._ensure_indexes()

    def _ensure_connection(self) -> None:
        """Ensure MongoDB connection is established."""
        try:
            # Use URI if provided, otherwise build connection URI
            if self.uri:
                connection_uri = self.uri
            elif self.username and self.password:
                connection_uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
            else:
                connection_uri = f"mongodb://{self.host}:{self.port}/"

            self._client = MongoClient(connection_uri, **self.connection_params)
            self._database = self._client[self.database_name]
            self._collection = self._database[self.collection_name]

            # Test connection
            self._client.admin.command('ping')

        except Exception as e:
            raise StorageError(f"Failed to connect to MongoDB: {e}")

    def _ensure_indexes(self) -> None:
        """Ensure proper indexes exist on the collection."""
        try:
            # Create indexes for better performance
            self._collection.create_index("key", unique=True)
            self._collection.create_index("scope")
            self._collection.create_index("storage")
            self._collection.create_index("created_at")

        except Exception:
            # Indexes might already exist, continue silently
            pass

    def _to_mongo_doc(self, key: str, value: ConfigValue) -> Dict[str, Any]:
        """Convert ConfigValue to MongoDB document.

        Args:
            key: Configuration key.
            value: Configuration value.

        Returns:
            MongoDB document.
        """
        return {
            "key": key,
            "value": value.value,
            "data_type": value.data_type,
            "scope": value.scope,
            "storage": value.storage,
            "immutable": value.immutable,
            "created_at": value.created_at,
            "updated_at": value.updated_at
        }

    def _from_mongo_doc(self, doc: Dict[str, Any]) -> ConfigValue:
        """Convert MongoDB document to ConfigValue.

        Args:
            doc: MongoDB document.

        Returns:
            ConfigValue instance.
        """
        return ConfigValue(
            key=doc["key"],
            value=doc["value"],
            data_type=doc["data_type"],
            scope=doc["scope"],
            storage=doc["storage"],
            immutable=doc["immutable"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )

    def get(self, key: str) -> Optional[ConfigValue]:
        """Get a configuration value from MongoDB.

        Args:
            key: Configuration key.

        Returns:
            Configuration value if found, None otherwise.
        """
        try:
            doc = self._collection.find_one({"key": key})

            if doc:
                return self._from_mongo_doc(doc)

            return None

        except Exception as e:
            raise StorageError(f"Failed to get value from MongoDB: {e}")

    def set(self, key: str, value: ConfigValue) -> None:
        """Set a configuration value in MongoDB.

        Args:
            key: Configuration key.
            value: Configuration value to store.
        """
        try:
            doc = self._to_mongo_doc(key, value)

            # Use upsert to insert or update
            self._collection.replace_one(
                {"key": key},
                doc,
                upsert=True
            )

        except Exception as e:
            raise StorageError(f"Failed to set value in MongoDB: {e}")

    def delete(self, key: str) -> bool:
        """Delete a configuration value from MongoDB.

        Args:
            key: Configuration key.

        Returns:
            True if deleted, False if not found.
        """
        try:
            result = self._collection.delete_one({"key": key})
            return result.deleted_count > 0

        except Exception as e:
            raise StorageError(f"Failed to delete value from MongoDB: {e}")

    def exists(self, key: str) -> bool:
        """Check if a configuration key exists in MongoDB.

        Args:
            key: Configuration key.

        Returns:
            True if exists, False otherwise.
        """
        try:
            return self._collection.count_documents({"key": key}, limit=1) > 0

        except Exception as e:
            raise StorageError(f"Failed to check existence in MongoDB: {e}")

    def keys(self) -> List[str]:
        """Get all configuration keys from MongoDB.

        Returns:
            List of configuration keys.
        """
        try:
            cursor = self._collection.find({}, {"key": 1, "_id": 0})
            return [doc["key"] for doc in cursor]

        except Exception as e:
            raise StorageError(f"Failed to get keys from MongoDB: {e}")

    def clear(self) -> None:
        """Clear all configuration values from MongoDB."""
        try:
            self._collection.delete_many({})

        except Exception as e:
            raise StorageError(f"Failed to clear MongoDB storage: {e}")

    def update(self, data: Dict[str, ConfigValue]) -> None:
        """Update multiple configuration values in MongoDB.

        Args:
            data: Dictionary of configuration values.
        """
        if not data:
            return

        try:
            # Use bulk operations for better performance
            operations = []

            for key, value in data.items():
                doc = self._to_mongo_doc(key, value)
                operations.append(
                    pymongo.ReplaceOne(
                        {"key": key},
                        doc,
                        upsert=True
                    )
                )

            if operations:
                self._collection.bulk_write(operations)

        except Exception as e:
            raise StorageError(f"Failed to update values in MongoDB: {e}")

    def get_by_scope(self, scope: str) -> Dict[str, ConfigValue]:
        """Get all configuration values for a specific scope.

        Args:
            scope: Configuration scope.

        Returns:
            Dictionary of configuration values.
        """
        try:
            cursor = self._collection.find({"scope": scope})
            return {doc["key"]: self._from_mongo_doc(doc) for doc in cursor}

        except Exception as e:
            raise StorageError(f"Failed to get values by scope from MongoDB: {e}")

    def get_info(self) -> Dict[str, Any]:
        """Get information about the MongoDB storage.

        Returns:
            Storage information dictionary.
        """
        try:
            # Get collection stats
            stats = self._database.command("collStats", self.collection_name)

            # Get server info
            server_info = self._client.server_info()

            return {
                'type': 'mongodb',
                'host': self.host,
                'port': self.port,
                'database': self.database_name,
                'collection': self.collection_name,
                'mongodb_version': server_info.get('version', 'unknown'),
                'total_keys': stats.get('count', 0),
                'collection_size': stats.get('size', 0),
                'storage_size': stats.get('storageSize', 0),
                'indexes': len(stats.get('indexSizes', {}))
            }

        except Exception as e:
            return {
                'type': 'mongodb',
                'host': self.host,
                'port': self.port,
                'database': self.database_name,
                'collection': self.collection_name,
                'error': str(e)
            }

    def close(self) -> None:
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self._collection = None

    def __del__(self) -> None:
        """Cleanup when storage is destroyed."""
        self.close()
