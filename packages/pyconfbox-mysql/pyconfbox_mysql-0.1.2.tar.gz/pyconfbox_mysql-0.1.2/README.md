# PyConfBox MySQL Plugin

**MySQL database storage backend for PyConfBox**

This plugin provides MySQL database storage backend for PyConfBox, enabling persistent configuration storage with full MySQL feature support.

> **한국어 문서**: [README_ko.md](README_ko.md) | **English Documentation**: README.md (current)

## 🚀 Installation

```bash
pip install pyconfbox-mysql
```

## 📋 Requirements

- Python 3.8+
- pyconfbox >= 0.1.0
- PyMySQL >= 1.0.0 or mysql-connector-python >= 8.0.0

## 💡 Usage

### Basic Usage

```python
from pyconfbox_mysql import MySQLStorage
from pyconfbox import Config

# MySQL storage configuration
mysql_storage = MySQLStorage(
    host='localhost',
    port=3306,
    user='root',
    password='password',
    database='config_db'
)

config = Config(default_storage=mysql_storage)

# Store and retrieve configurations
config.set('app_name', 'MyApp')
config.set('debug', True)
config.set('max_connections', 100)

app_name = config.get('app_name')
debug_mode = config.get('debug')
```

### Connection String Usage

```python
from pyconfbox_mysql import MySQLStorage

# Using connection string
mysql_storage = MySQLStorage(
    connection_string='mysql://user:password@localhost:3306/config_db'
)

config = Config(default_storage=mysql_storage)
```

### Advanced Configuration

```python
from pyconfbox_mysql import MySQLStorage

mysql_storage = MySQLStorage(
    host='localhost',
    port=3306,
    user='config_user',
    password='secure_password',
    database='app_config',
    table_name='configurations',  # Custom table name
    pool_size=10,  # Connection pool size
    pool_timeout=30,  # Pool timeout in seconds
    ssl_config={  # SSL configuration
        'ssl_ca': '/path/to/ca.pem',
        'ssl_cert': '/path/to/client-cert.pem',
        'ssl_key': '/path/to/client-key.pem'
    }
)

config = Config(default_storage=mysql_storage)
```

## 🎯 Features

- **🔄 Full CRUD Operations**: Create, read, update, delete configurations
- **🔒 Transaction Support**: ACID-compliant transactions
- **⚡ Connection Pooling**: Efficient connection management
- **🛡️ SSL Support**: Secure connections with SSL/TLS
- **📊 Metadata Tracking**: Configuration metadata and timestamps
- **🔍 Query Optimization**: Efficient indexing and query performance

## 🏗️ Database Schema

The plugin automatically creates the following table structure:

```sql
CREATE TABLE configurations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT,
    data_type VARCHAR(50),
    scope VARCHAR(50),
    is_immutable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key),
    INDEX idx_scope (scope)
);
```

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | 'localhost' | MySQL server host |
| `port` | int | 3306 | MySQL server port |
| `user` | str | Required | Database username |
| `password` | str | Required | Database password |
| `database` | str | Required | Database name |
| `table_name` | str | 'configurations' | Table name for storing configs |
| `connection_string` | str | None | Complete connection string |
| `pool_size` | int | 5 | Connection pool size |
| `pool_timeout` | int | 30 | Pool timeout in seconds |
| `ssl_config` | dict | None | SSL configuration dictionary |

## 📖 Documentation

- **[Main PyConfBox Documentation](../../docs/README.md)**
- **[Storage Backends Guide](../../docs/en/storage-backends.md)**
- **[API Reference](../../docs/en/api-reference.md)**
- **[한국어 문서](../../docs/ko/README.md)**

## 🔗 Related Packages

- **[pyconfbox](../pyconfbox/)** - Main PyConfBox package
- **[pyconfbox-django](../pyconfbox-django/)** - Django integration
- **[pyconfbox-postgresql](../pyconfbox-postgresql/)** - PostgreSQL storage backend
- **[pyconfbox-mongodb](../pyconfbox-mongodb/)** - MongoDB storage backend

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](../../.github/CONTRIBUTING.md) for details.

## 📄 License

MIT License - See the [LICENSE](LICENSE) file for details.

---

**Power your configurations with MySQL reliability!** 🚀 