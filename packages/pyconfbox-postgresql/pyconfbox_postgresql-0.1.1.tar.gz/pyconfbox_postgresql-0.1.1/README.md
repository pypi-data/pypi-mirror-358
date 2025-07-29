# PyConfBox PostgreSQL Plugin

**PostgreSQL database storage backend for PyConfBox**

This plugin provides PostgreSQL database storage backend for PyConfBox, enabling persistent configuration storage with advanced PostgreSQL features like JSONB support and full-text search.

> **한국어 문서**: [README_ko.md](README_ko.md) | **English Documentation**: README.md (current)

## 🚀 Installation

```bash
pip install pyconfbox-postgresql
```

## 📋 Requirements

- Python 3.8+
- pyconfbox >= 0.1.0
- psycopg2-binary >= 2.9.0 or asyncpg >= 0.27.0

## 💡 Usage

### Basic Usage

```python
from pyconfbox_postgresql import PostgreSQLStorage
from pyconfbox import Config

# PostgreSQL storage configuration
postgresql_storage = PostgreSQLStorage(
    host='localhost',
    port=5432,
    user='postgres',
    password='password',
    database='config_db'
)

config = Config(default_storage=postgresql_storage)

# Store and retrieve configurations
config.set('app_name', 'MyApp')
config.set('debug', True)
config.set('max_connections', 100)

app_name = config.get('app_name')
debug_mode = config.get('debug')
```

### Connection String Usage

```python
from pyconfbox_postgresql import PostgreSQLStorage

# Using connection string
postgresql_storage = PostgreSQLStorage(
    connection_string='postgresql://user:password@localhost:5432/config_db'
)

config = Config(default_storage=postgresql_storage)
```

### Advanced Configuration with JSONB

```python
from pyconfbox_postgresql import PostgreSQLStorage

postgresql_storage = PostgreSQLStorage(
    host='localhost',
    port=5432,
    user='config_user',
    password='secure_password',
    database='app_config',
    table_name='configurations',  # Custom table name
    use_jsonb=True,  # Enable JSONB for complex data types
    pool_size=10,  # Connection pool size
    pool_timeout=30,  # Pool timeout in seconds
    ssl_mode='require',  # SSL mode
    application_name='PyConfBox'  # Application name for monitoring
)

config = Config(default_storage=postgresql_storage)

# Store complex data structures
config.set('database_config', {
    'host': 'db.example.com',
    'port': 5432,
    'connections': {
        'read': 5,
        'write': 2
    }
})
```

### Async Support

```python
from pyconfbox_postgresql import AsyncPostgreSQLStorage
from pyconfbox import Config
import asyncio

async def main():
    # Async PostgreSQL storage
    async_storage = AsyncPostgreSQLStorage(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='config_db'
    )
    
    config = Config(default_storage=async_storage)
    
    # Async operations
    await config.aset('async_key', 'async_value')
    value = await config.aget('async_key')
    
    await async_storage.close()

asyncio.run(main())
```

## 🎯 Features

- **🔄 Full CRUD Operations**: Create, read, update, delete configurations
- **📊 JSONB Support**: Native JSON storage with indexing and querying
- **🔒 Transaction Support**: ACID-compliant transactions
- **⚡ Connection Pooling**: Efficient connection management
- **🛡️ SSL Support**: Secure connections with various SSL modes
- **🔍 Full-text Search**: Advanced search capabilities
- **⚙️ Async Support**: Asynchronous operations with asyncpg
- **📈 Performance**: Optimized queries and indexing strategies

## 🏗️ Database Schema

The plugin automatically creates the following table structure:

```sql
CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT,
    config_json JSONB,  -- When use_jsonb=True
    data_type VARCHAR(50),
    scope VARCHAR(50),
    is_immutable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_config_key UNIQUE (config_key)
);

-- Indexes for performance
CREATE INDEX idx_config_key ON configurations (config_key);
CREATE INDEX idx_scope ON configurations (scope);
CREATE INDEX idx_config_json ON configurations USING GIN (config_json);  -- For JSONB
```

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | 'localhost' | PostgreSQL server host |
| `port` | int | 5432 | PostgreSQL server port |
| `user` | str | Required | Database username |
| `password` | str | Required | Database password |
| `database` | str | Required | Database name |
| `table_name` | str | 'configurations' | Table name for storing configs |
| `connection_string` | str | None | Complete connection string |
| `use_jsonb` | bool | False | Enable JSONB for complex data |
| `pool_size` | int | 5 | Connection pool size |
| `pool_timeout` | int | 30 | Pool timeout in seconds |
| `ssl_mode` | str | 'prefer' | SSL mode (disable, allow, prefer, require) |
| `application_name` | str | 'PyConfBox' | Application name for monitoring |

## 🔍 Advanced Querying

```python
from pyconfbox_postgresql import PostgreSQLStorage

# Enable JSONB for advanced querying
storage = PostgreSQLStorage(
    host='localhost',
    database='config_db',
    use_jsonb=True
)

config = Config(default_storage=storage)

# Store complex configuration
config.set('api_config', {
    'endpoints': {
        'users': '/api/v1/users',
        'orders': '/api/v1/orders'
    },
    'rate_limits': {
        'requests_per_minute': 1000,
        'burst_size': 100
    }
})

# Query using JSONB operators (PostgreSQL-specific)
# This would be implemented in custom storage methods
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
- **[pyconfbox-mongodb](../pyconfbox-mongodb/)** - MongoDB storage backend

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](../../.github/CONTRIBUTING.md) for details.

## 📄 License

MIT License - See the [LICENSE](LICENSE) file for details.

---

**Leverage PostgreSQL's power for your configurations!** 🚀 