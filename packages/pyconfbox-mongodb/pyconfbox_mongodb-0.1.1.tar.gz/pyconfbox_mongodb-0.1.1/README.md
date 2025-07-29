# PyConfBox MongoDB Plugin

**MongoDB document database storage backend for PyConfBox**

This plugin provides MongoDB document database storage backend for PyConfBox, enabling flexible schema-less configuration storage with powerful querying capabilities and horizontal scaling support.

> **한국어 문서**: [README_ko.md](README_ko.md) | **English Documentation**: README.md (current)

## 🚀 Installation

```bash
pip install pyconfbox-mongodb
```

## 📋 Requirements

- Python 3.8+
- pyconfbox >= 0.1.0
- pymongo >= 4.0.0

## 💡 Usage

### Basic Usage

```python
from pyconfbox_mongodb import MongoDBStorage
from pyconfbox import Config

# MongoDB storage configuration
mongodb_storage = MongoDBStorage(
    host='localhost',
    port=27017,
    database='config_db',
    collection='configurations'
)

config = Config(default_storage=mongodb_storage)

# Store and retrieve configurations
config.set('app_name', 'MyApp')
config.set('debug', True)
config.set('max_connections', 100)

app_name = config.get('app_name')
debug_mode = config.get('debug')
```

### Connection URI Usage

```python
from pyconfbox_mongodb import MongoDBStorage

# Using MongoDB connection URI
mongodb_storage = MongoDBStorage(
    uri='mongodb://username:password@localhost:27017/config_db'
)

config = Config(default_storage=mongodb_storage)
```

### Advanced Configuration

```python
from pyconfbox_mongodb import MongoDBStorage

mongodb_storage = MongoDBStorage(
    host='localhost',
    port=27017,
    database='app_config',
    collection='configurations',
    username='config_user',
    password='secure_password',
    auth_source='admin',  # Authentication database
    replica_set='rs0',  # Replica set name
    read_preference='secondaryPreferred',  # Read preference
    write_concern={'w': 'majority'},  # Write concern
    ssl=True,  # Enable SSL
    ssl_cert_reqs='CERT_REQUIRED',  # SSL certificate requirements
    connect_timeout=5000,  # Connection timeout in ms
    server_selection_timeout=3000  # Server selection timeout in ms
)

config = Config(default_storage=mongodb_storage)

# Store complex nested data structures
config.set('api_config', {
    'endpoints': {
        'users': {
            'url': '/api/v1/users',
            'methods': ['GET', 'POST'],
            'rate_limit': 1000
        },
        'orders': {
            'url': '/api/v1/orders',
            'methods': ['GET', 'POST', 'PUT'],
            'rate_limit': 500
        }
    },
    'middleware': ['auth', 'cors', 'rate_limit'],
    'features': {
        'caching': True,
        'logging': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        }
    }
})
```

### Replica Set and Sharding Support

```python
from pyconfbox_mongodb import MongoDBStorage

# Replica set configuration
mongodb_storage = MongoDBStorage(
    uri='mongodb://user:pass@host1:27017,host2:27017,host3:27017/config_db?replicaSet=rs0',
    read_preference='secondaryPreferred',
    write_concern={'w': 'majority', 'j': True}
)

# Sharded cluster configuration
mongodb_storage = MongoDBStorage(
    uri='mongodb://user:pass@mongos1:27017,mongos2:27017/config_db',
    read_preference='nearest'
)

config = Config(default_storage=mongodb_storage)
```

## 🎯 Features

- **📄 Document Storage**: Native document-based configuration storage
- **🔍 Rich Querying**: Powerful MongoDB query capabilities
- **📈 Horizontal Scaling**: Support for replica sets and sharding
- **🔒 Authentication**: Multiple authentication mechanisms
- **🛡️ SSL/TLS Support**: Secure connections with SSL/TLS
- **⚡ Connection Pooling**: Efficient connection management
- **🎯 Flexible Schema**: Schema-less document structure
- **📊 Aggregation**: Advanced data aggregation pipelines
- **🔄 Change Streams**: Real-time configuration change monitoring

## 🏗️ Document Structure

Configurations are stored as MongoDB documents with the following structure:

```json
{
    "_id": ObjectId("..."),
    "config_key": "app_name",
    "config_value": "MyApp",
    "data_type": "str",
    "scope": "global",
    "is_immutable": false,
    "metadata": {
        "created_at": ISODate("2024-01-01T00:00:00Z"),
        "updated_at": ISODate("2024-01-01T00:00:00Z"),
        "version": 1
    }
}
```

### Indexes

The plugin automatically creates the following indexes for optimal performance:

```javascript
// Unique index on config_key
db.configurations.createIndex({ "config_key": 1 }, { unique: true })

// Compound index for scope-based queries
db.configurations.createIndex({ "scope": 1, "config_key": 1 })

// Index for metadata queries
db.configurations.createIndex({ "metadata.updated_at": -1 })
```

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | 'localhost' | MongoDB server host |
| `port` | int | 27017 | MongoDB server port |
| `database` | str | Required | Database name |
| `collection` | str | 'configurations' | Collection name |
| `uri` | str | None | Complete MongoDB URI |
| `username` | str | None | Authentication username |
| `password` | str | None | Authentication password |
| `auth_source` | str | None | Authentication database |
| `replica_set` | str | None | Replica set name |
| `read_preference` | str | 'primary' | Read preference |
| `write_concern` | dict | None | Write concern options |
| `ssl` | bool | False | Enable SSL/TLS |
| `connect_timeout` | int | 20000 | Connection timeout (ms) |
| `server_selection_timeout` | int | 30000 | Server selection timeout (ms) |

## 🔍 Advanced Querying

```python
from pyconfbox_mongodb import MongoDBStorage
from pymongo import ASCENDING, DESCENDING

# Custom storage with advanced querying
class AdvancedMongoDBStorage(MongoDBStorage):
    def find_by_pattern(self, pattern: str):
        """Find configurations matching a pattern."""
        return self.collection.find({
            "config_key": {"$regex": pattern, "$options": "i"}
        })
    
    def find_recent_changes(self, hours: int = 24):
        """Find configurations changed in the last N hours."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.collection.find({
            "metadata.updated_at": {"$gte": cutoff}
        }).sort("metadata.updated_at", DESCENDING)
    
    def aggregate_by_scope(self):
        """Aggregate configurations by scope."""
        pipeline = [
            {"$group": {
                "_id": "$scope",
                "count": {"$sum": 1},
                "keys": {"$push": "$config_key"}
            }}
        ]
        return list(self.collection.aggregate(pipeline))

# Usage
storage = AdvancedMongoDBStorage(
    host='localhost',
    database='config_db'
)

# Find all API-related configurations
api_configs = storage.find_by_pattern("api_.*")

# Find recent changes
recent_changes = storage.find_recent_changes(hours=1)

# Get configuration statistics by scope
scope_stats = storage.aggregate_by_scope()
```

## 📖 Documentation

- **[Main PyConfBox Documentation](../../docs/README.md)**
- **[Storage Backends Guide](../../docs/en/storage-backends.md)**
- **[API Reference](../../docs/en/api-reference.md)**
- **[한국어 문서](../../docs/ko/README.md)**

## 🔗 Related Packages

- **[pyconfbox](../pyconfbox/)** - Main PyConfBox package
- **[pyconfbox-django](../pyconfbox-django/)** - Django integration
- **[pyconfbox-mysql](../pyconfbox-mysql/)** - MySQL storage backend
- **[pyconfbox-postgresql](../pyconfbox-postgresql/)** - PostgreSQL storage backend

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](../../.github/CONTRIBUTING.md) for details.

## 📄 License

MIT License - See the [LICENSE](LICENSE) file for details.

---

**Scale your configurations with MongoDB flexibility!** 🚀 