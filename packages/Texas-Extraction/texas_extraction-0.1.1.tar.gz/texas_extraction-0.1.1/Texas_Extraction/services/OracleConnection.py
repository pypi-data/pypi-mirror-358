import logging
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, Connection
from Texas_Extraction.services.RetryLogic import retry
# Local modules
from Texas_Extraction.helper.config import Settings

# Configure logging
logger = logging.getLogger(__name__)


class OracleConnection:
    def __init__(self):
        self.engine: Optional[Engine] = create_engine(Settings.DB_URL.value)
        self.connection: Optional[Connection] = None

    def __enter__(self) -> "OracleConnection":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def connect(self) -> None:
        """Establish the database connection."""
        try:
            self.connection = self.engine.raw_connection()
            logger.info("Database connection established.")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}", exc_info=True)
            raise


    def fetch_data(self, query: str):
        """Execute a query and return column names and rows."""
        with self._cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0].upper() for desc in cursor.description]
            return columns, rows

    @retry(max_retries=1, delay=100, retry_on_exceptions=(Exception,))
    def commit_data(self, query: str):
        """Execute a query and commit the transaction."""
        with self._cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    @contextmanager
    def _cursor(self):
        """Context manager to handle cursor lifecycle."""
        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
        finally:
            if cursor:
                cursor.close()

    def close(self) -> None:
        """Safely close the connection."""
        if self.connection and not self._is_connection_closed(self.connection):
            try:
                self.connection.close()
                logger.info("Connection closed.")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
        self.connection = None
        self.engine = None


    def _is_connection_closed(self, conn) -> bool:
        """Check if cx_Oracle connection is closed."""
        try:
            conn.ping()  # Ping the database to test connection status
            return False
        except Exception:
            return True