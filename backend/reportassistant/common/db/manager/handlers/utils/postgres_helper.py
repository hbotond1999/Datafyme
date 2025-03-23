import psycopg2
import logging
from typing import Optional, List, Any

from psycopg2.extras import RealDictCursor

logger = logging.getLogger("reportassistant.default")


class PostgresHelper:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: int):
        """
        Initialize the PostgresDatabaseManager with database connection details.

        :param dbname: Name of the database.
        :param user: Database username.
        :param password: Password for the database user.
        :param host: Hostname of the PostgresSQL server.
        :param port: Port of the PostgresSQL server.
        """
        self.dbname: str = dbname
        self.user: str = user
        self.password: str = password
        self.host: str = host
        self.port: int = port
        self.connection: Optional[psycopg2.extensions.connection] = None  # Optional connection object

    def _connect(self) -> None:
        """Establish connection to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info(f"Connected to the database: {self.dbname}")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error connecting to the database {self.dbname}: {error}")
            self.connection = None
            raise error

    def _disconnect(self) -> None:
        """Close the database connection."""
        if self.connection is not None:
            try:
                self.connection.close()
                logger.info(f"Disconnected from the database: {self.dbname}")
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(f"Error during disconnection from {self.dbname}: {error}")
                raise error
            finally:
                self.connection = None

    def execute_query(self, query: str, row_num=None) -> Optional[List[Any]]:
        """
        Execute an SQL query and return results if applicable.

        :param query: SQL query string to be executed.
        :param row_num: How many rows to return. If provided, the query will be limited to this number of rows.
        :return: List of rows (if SELECT query) or None.
        """
        try:
            # Ensure we are connected to the database
            self._connect()
            if self.connection is None:
                raise ConnectionError("Failed to establish database connection.")

            if row_num is not None:
                if query.strip().upper().startswith("SELECT"):
                    cleaned_query = query.strip()
                    if cleaned_query.endswith(';'):
                        cleaned_query = cleaned_query[:-1]

                    query = f"SELECT * FROM ({cleaned_query}) AS subquery LIMIT {row_num};"

            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                self.connection.commit()
                logger.info("Query executed successfully.")

                if cursor.description:
                    results: List[Any] = cursor.fetchall() # fetchmany(10)   cursor.rowcount
                    return results
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error executing query in {self.dbname}: {error} - {query}")
            raise
        finally:
            self._disconnect()

    def check_connection(self) -> bool:
        try:
            self._connect()
            self._disconnect()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            return False