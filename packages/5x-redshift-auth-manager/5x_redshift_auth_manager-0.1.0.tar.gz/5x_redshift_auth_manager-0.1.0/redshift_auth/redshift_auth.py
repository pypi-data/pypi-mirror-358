# 5x_redshift_auth_manager/redshift_auth.py
import os
from typing import Dict
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection

class RedshiftConnectionManager:
    """
    Manages AWS Redshift connections using environment variables.
    Required environment variables:
    - FIVEX_REDSHIFT_HOST: Redshift cluster endpoint
    - FIVEX_REDSHIFT_PORT: Redshift port (defaults to 5439)
    - FIVEX_REDSHIFT_DATABASE: Database name
    - FIVEX_REDSHIFT_USER: Database username
    - FIVEX_REDSHIFT_PASSWORD: Database password
    """
    
    def __init__(self):
        """Initialize the Redshift connection manager using environment variables."""
        self._connection = None
        self._validate_and_set_credentials()
    
    def _validate_and_set_credentials(self) -> None:
        """
        Validate and set Redshift credentials from environment variables.
        
        Raises:
            ValueError: If required environment variables are missing
            ValueError: If credentials are empty or malformed
        """
        # Get credentials from environment
        host = os.getenv('FIVEX_REDSHIFT_HOST')
        port = os.getenv('FIVEX_REDSHIFT_PORT', '5439')
        database = os.getenv('FIVEX_REDSHIFT_DATABASE')
        user = os.getenv('FIVEX_REDSHIFT_USER')
        password = os.getenv('FIVEX_REDSHIFT_PASSWORD')

        # Check for missing credentials
        missing_vars = []
        if not host:
            missing_vars.append('FIVEX_REDSHIFT_HOST')
        if not database:
            missing_vars.append('FIVEX_REDSHIFT_DATABASE')
        if not user:
            missing_vars.append('FIVEX_REDSHIFT_USER')
        if not password:
            missing_vars.append('FIVEX_REDSHIFT_PASSWORD')
            
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Validate credential format
        if not host.strip():
            raise ValueError("Redshift host is invalid or empty")
        if not database.strip():
            raise ValueError("Redshift database name is invalid or empty")
        if not user.strip():
            raise ValueError("Redshift username is invalid or empty")
        if not password.strip():
            raise ValueError("Redshift password is invalid or empty")

        # Validate port
        try:
            port_int = int(port)
            if port_int < 1 or port_int > 65535:
                raise ValueError("Redshift port must be between 1 and 65535")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Redshift port must be a valid integer")
            raise

        self.credentials = {
            'host': host,
            'port': port_int,
            'database': database,
            'user': user,
            'password': password
        }

    def get_connection(self) -> connection:
        """
        Get or create a Redshift connection instance.
        
        Returns:
            psycopg2.connection: Configured Redshift connection
            
        Raises:
            psycopg2.OperationalError: If connection fails due to invalid credentials or network issues
            psycopg2.DatabaseError: If database-specific errors occur
            ConnectionError: If connection to Redshift fails
            Exception: For other unexpected errors
        """
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(**self.credentials)
                # Test the connection immediately
                with self._connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    
            except psycopg2.OperationalError as e:
                error_msg = str(e).lower()
                if "password authentication failed" in error_msg:
                    raise ValueError("Invalid Redshift username or password") from e
                elif "could not connect to server" in error_msg or "timeout" in error_msg:
                    raise ConnectionError("Could not connect to Redshift server. Check host and port.") from e
                elif "database" in error_msg and "does not exist" in error_msg:
                    raise ValueError("Redshift database does not exist") from e
                else:
                    raise ConnectionError(f"Failed to connect to Redshift: {str(e)}") from e
            except psycopg2.DatabaseError as e:
                raise ValueError(f"Redshift database error: {str(e)}") from e
            except Exception as e:
                raise ConnectionError(f"Unexpected error connecting to Redshift: {str(e)}") from e
                
        return self._connection

    def get_cursor(self):
        """
        Get a cursor from the connection.
        
        Returns:
            psycopg2.cursor: Database cursor for executing queries
        """
        connection = self.get_connection()
        return connection.cursor()

    def close_connection(self):
        """Close the connection if it exists."""
        if self._connection and not self._connection.closed:
            self._connection.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close_connection()

# Example usage
if __name__ == "__main__":
    try:
        # Create manager and get connection
        manager = RedshiftConnectionManager()
        connection = manager.get_connection()
        print("Successfully connected to AWS Redshift")
        
        # Test with a simple query
        with manager.get_cursor() as cursor:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            print(f"Redshift version: {result[0]}")
            
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        try:
            manager.close_connection()
        except:
            pass