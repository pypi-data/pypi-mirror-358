"""
Module provides a class for executing BigQuery queries and returning results in JSON format.

Classes:
    BigqueryQuery: A class to execute BigQuery queries and return results in JSON format.
"""

# Removed date, datetime import as specific handling is no longer needed
from typing import Any  # Import Any for type hinting

from google.cloud import bigquery

from brownllama.logger import get_logger

logger = get_logger(__name__)


class BigqueryQuery:
    """
    A class to execute BigQuery queries and return results in JSON format.

    Attributes:
        client (google.cloud.bigquery.client.Client): The BigQuery client used to execute queries.

    """

    def __init__(self, project_id: str) -> None:
        """
        Initialize the BigqueryQuery client.

        Args:
            project_id (str): Your Google Cloud Project ID.

        """
        self.client = bigquery.Client(project=project_id)
        logger.debug(
            f"{'=' * 10} BigQuery client initialized for project: {project_id} {'=' * 10}"
        )

    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a BigQuery SQL query and returns the results as a list of dictionaries.

        Raises an exception if the query fails or results cannot be serialized.

        Args:
            query (str): The SQL query string to execute.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing the query results.

        Raises:
            Exception: If any error occurs during query execution or data processing.

        """
        logger.debug(f"{'=' * 10}\nExecuting query:\n{query}\n{'=' * 10}")
        query_job = self.client.query(query)
        results = query_job.result()

        # Convert results to a list of dictionaries, converting all values to strings
        rows_dict = []
        for row in results:
            row_dict = {}
            for key, value in row.items():
                row_dict[key] = str(value)
            rows_dict.append(row_dict)

        logger.debug(
            f"{'=' * 10} Query executed successfully. Results converted to list of dictionaries. {'=' * 10}"
        )
        return rows_dict
