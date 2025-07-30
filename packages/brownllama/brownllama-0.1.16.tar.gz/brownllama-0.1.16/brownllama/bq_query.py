"""
Module provides a class for executing BigQuery queries and returning results in JSON format.

Classes:
    BigqueryQuery: A class to execute BigQuery queries and return results in JSON format.
"""

import json

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

    def execute_query(self, query: str) -> str:
        """
        Execute a BigQuery SQL query and returns the results as a JSON string.

        Args:
            query (str): The SQL query string to execute.

        Returns:
            str: A JSON string representing the query results.
                 Returns an empty JSON array string if no results or an error occurs.

        """
        try:
            logger.debug(f"{'=' * 10}\nExecuting query:\n{query}\n{'=' * 10}")
            query_job = self.client.query(query)
            results = query_job.result()

            # Convert results to a list of dictionaries
            rows_dict = [dict(row) for row in results]

            # Convert the list of dictionaries to a JSON string
            json_results = json.dumps(rows_dict, indent=2)

            logger.debug(
                "{'=' * 10} Query executed successfully. Results converted to JSON. {'=' * 10}"
            )
            return json_results

        except Exception as e:
            logger.error(
                f"{'=' * 10} An error occurred during query execution: {e} {'=' * 10}"
            )
            return json.dumps({"error": str(e)})
