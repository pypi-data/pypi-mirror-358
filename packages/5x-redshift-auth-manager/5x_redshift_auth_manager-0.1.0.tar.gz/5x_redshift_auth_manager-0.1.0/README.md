# 5X Redshift Auth Manager

A simple Python library for managing AWS Redshift connections using environment variables. This library provides an easy way to authenticate and connect to AWS Redshift clusters with comprehensive error handling and connection management.

## 🚀 Features

- Streamlined AWS Redshift authentication with **environment variables**
- **Automatic credential validation** and connection testing
- Comprehensive **error handling** for production reliability
- Built-in **connection testing** utilities
- Context manager support for connection management
- **Secure credential handling** with environment variables

## 📦 Installation

```bash
pip install 5x-redshift-auth-manager
```

## 🔧 Configuration

Set the following environment variables:

```bash
export FIVEX_REDSHIFT_HOST="your-redshift-cluster.region.redshift.amazonaws.com"
export FIVEX_REDSHIFT_PORT="5439"  # Optional, defaults to 5439
export FIVEX_REDSHIFT_DATABASE="your_database"
export FIVEX_REDSHIFT_USER="your_username"
export FIVEX_REDSHIFT_PASSWORD="your_password"
```

## 💻 Usage

### Basic Usage

```python
from redshift_auth import RedshiftConnectionManager

# Create connection manager
manager = RedshiftConnectionManager()

# Get connection
connection = manager.get_connection()

# Execute queries
with manager.get_cursor() as cursor:
    cursor.execute("SELECT * FROM your_table LIMIT 10")
    results = cursor.fetchall()
    print(results)

# Close connection when done
manager.close_connection()
```

### Using Context Manager

```python
from redshift_auth import RedshiftConnectionManager

# Use context manager for automatic connection cleanup
with RedshiftConnectionManager() as manager:
    connection = manager.get_connection()
    
    with manager.get_cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"Redshift version: {version[0]}")
```

### Error Handling

```python
from redshift_auth import RedshiftConnectionManager

try:
    manager = RedshiftConnectionManager()
    connection = manager.get_connection()
    print("Successfully connected to Redshift!")
    
except ValueError as e:
    print(f"Configuration error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🔒 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIVEX_REDSHIFT_HOST` | ✅ | - | Redshift cluster endpoint |
| `FIVEX_REDSHIFT_PORT` | ❌ | 5439 | Redshift port number |
| `FIVEX_REDSHIFT_DATABASE` | ✅ | - | Database name |
| `FIVEX_REDSHIFT_USER` | ✅ | - | Database username |
| `FIVEX_REDSHIFT_PASSWORD` | ✅ | - | Database password |

## 🛠️ API Reference

### RedshiftConnectionManager

#### Methods

- `__init__()`: Initialize the connection manager
- `get_connection()`: Get or create a Redshift connection
- `get_cursor()`: Get a database cursor for executing queries
- `close_connection()`: Close the connection
- `__enter__()` / `__exit__()`: Context manager support

#### Error Handling

The library provides specific error handling for:

- **ValueError**: Missing or invalid environment variables
- **ConnectionError**: Network connectivity issues
- **psycopg2.OperationalError**: Database connection issues
- **psycopg2.DatabaseError**: Database-specific errors

## 🔍 Requirements

- Python 3.8 or higher
- psycopg2-binary >= 2.9.0

## 📝 License

This project is licensed under the MIT License.

## 🤝 Support

- 🌐 Website: [www.5x.co](https://www.5x.co)
- 📧 Email: [support@5x.co](mailto:support@5x.co)
- 🐛 Issues: [GitHub Issues](https://github.com/5x-Platform/5x-nextgen-python-libraries/issues)

---

🚀 Developed by [**5X**](https://www.5x.co) | Powering Secure & Scalable Data Platforms