"""MySQL storage backend for PyConfBox."""

import json
from typing import Any, Dict, List, Optional

try:
    import pymysql
except ImportError:
    pymysql = None

try:
    from pyconfbox.core.exceptions import StorageError
    from pyconfbox.core.types import ConfigValue
    from pyconfbox.storage.base import BaseStorage
except ImportError:
    raise ImportError("pyconfbox is required for pyconfbox-mysql plugin")


class MySQLStorage(BaseStorage):
    """MySQL database storage backend for PyConfBox.

    This storage backend uses MySQL database to persist configuration values.
    Requires pymysql package to be installed.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "pyconfbox",
        table: str = "configurations",
        **kwargs: Any
    ) -> None:
        """Initialize MySQL storage.

        Args:
            host: MySQL server host.
            port: MySQL server port.
            user: MySQL username.
            password: MySQL password.
            database: Database name.
            table: Table name for storing configurations.
            **kwargs: Additional connection parameters.
        """
        super().__init__()

        if pymysql is None:
            raise ImportError(
                "pymysql package is required for MySQL storage. "
                "Install it with: pip install pymysql"
            )

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.connection_params = kwargs

        self._connection = None
        self._ensure_database()
        self._ensure_table()

    def _get_connection(self):
        """Get MySQL database connection."""
        if self._connection is None or not self._connection.open:
            try:
                self._connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset='utf8mb4',
                    autocommit=True,
                    **self.connection_params
                )
            except Exception as e:
                raise StorageError(f"Failed to connect to MySQL: {e}")

        return self._connection

    def _ensure_database(self) -> None:
        """Ensure the database exists."""
        try:
            # Connect without database to create it if needed
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                **self.connection_params
            )

            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

            connection.close()
        except Exception as e:
            raise StorageError(f"Failed to ensure database exists: {e}")

    def _ensure_table(self) -> None:
        """Ensure the configurations table exists."""
        connection = self._get_connection()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.table}` (
            `key` VARCHAR(255) PRIMARY KEY,
            `value` LONGTEXT,
            `data_type` VARCHAR(50),
            `scope` VARCHAR(50),
            `storage` VARCHAR(50),
            `immutable` BOOLEAN DEFAULT FALSE,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_scope (`scope`),
            INDEX idx_storage (`storage`)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(create_table_sql)
        except Exception as e:
            raise StorageError(f"Failed to create table: {e}")

    def get(self, key: str) -> Optional[ConfigValue]:
        """Get a configuration value from MySQL.

        Args:
            key: Configuration key.

        Returns:
            Configuration value if found, None otherwise.
        """
        connection = self._get_connection()

        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    f"SELECT * FROM `{self.table}` WHERE `key` = %s",
                    (key,)
                )
                row = cursor.fetchone()

                if row:
                    # Parse JSON value
                    try:
                        value = json.loads(row['value'])
                    except (json.JSONDecodeError, TypeError):
                        value = row['value']

                    return ConfigValue(
                        key=row['key'],
                        value=value,
                        data_type=row['data_type'],
                        scope=row['scope'],
                        storage=row['storage'],
                        immutable=bool(row['immutable']),
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )

                return None

        except Exception as e:
            raise StorageError(f"Failed to get value from MySQL: {e}")

    def set(self, key: str, value: ConfigValue) -> None:
        """Set a configuration value in MySQL.

        Args:
            key: Configuration key.
            value: Configuration value to store.
        """
        connection = self._get_connection()

        # Serialize value to JSON
        try:
            serialized_value = json.dumps(value.value, ensure_ascii=False)
        except (TypeError, ValueError):
            serialized_value = str(value.value)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO `{self.table}`
                    (`key`, `value`, `data_type`, `scope`, `storage`, `immutable`, `created_at`, `updated_at`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    `value` = VALUES(`value`),
                    `data_type` = VALUES(`data_type`),
                    `scope` = VALUES(`scope`),
                    `storage` = VALUES(`storage`),
                    `immutable` = VALUES(`immutable`),
                    `updated_at` = VALUES(`updated_at`)
                """, (
                    key,
                    serialized_value,
                    value.data_type,
                    value.scope,
                    value.storage,
                    value.immutable,
                    value.created_at,
                    value.updated_at
                ))

        except Exception as e:
            raise StorageError(f"Failed to set value in MySQL: {e}")

    def delete(self, key: str) -> bool:
        """Delete a configuration value from MySQL.

        Args:
            key: Configuration key.

        Returns:
            True if deleted, False if not found.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM `{self.table}` WHERE `key` = %s",
                    (key,)
                )
                return cursor.rowcount > 0

        except Exception as e:
            raise StorageError(f"Failed to delete value from MySQL: {e}")

    def exists(self, key: str) -> bool:
        """Check if a configuration key exists in MySQL.

        Args:
            key: Configuration key.

        Returns:
            True if exists, False otherwise.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT 1 FROM `{self.table}` WHERE `key` = %s LIMIT 1",
                    (key,)
                )
                return cursor.fetchone() is not None

        except Exception as e:
            raise StorageError(f"Failed to check existence in MySQL: {e}")

    def keys(self) -> List[str]:
        """Get all configuration keys from MySQL.

        Returns:
            List of configuration keys.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT `key` FROM `{self.table}`")
                return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            raise StorageError(f"Failed to get keys from MySQL: {e}")

    def clear(self) -> None:
        """Clear all configuration values from MySQL."""
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM `{self.table}`")

        except Exception as e:
            raise StorageError(f"Failed to clear MySQL storage: {e}")

    def update(self, data: Dict[str, ConfigValue]) -> None:
        """Update multiple configuration values in MySQL.

        Args:
            data: Dictionary of configuration values.
        """
        for key, value in data.items():
            self.set(key, value)

    def get_info(self) -> Dict[str, Any]:
        """Get information about the MySQL storage.

        Returns:
            Storage information dictionary.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                # Get table info
                cursor.execute(f"SELECT COUNT(*) FROM `{self.table}`")
                total_keys = cursor.fetchone()[0]

                # Get MySQL version
                cursor.execute("SELECT VERSION()")
                mysql_version = cursor.fetchone()[0]

                return {
                    'type': 'mysql',
                    'host': self.host,
                    'port': self.port,
                    'database': self.database,
                    'table': self.table,
                    'mysql_version': mysql_version,
                    'total_keys': total_keys
                }

        except Exception as e:
            return {
                'type': 'mysql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'table': self.table,
                'error': str(e)
            }

    def close(self) -> None:
        """Close the MySQL connection."""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None

    def __del__(self) -> None:
        """Cleanup when storage is destroyed."""
        self.close()
