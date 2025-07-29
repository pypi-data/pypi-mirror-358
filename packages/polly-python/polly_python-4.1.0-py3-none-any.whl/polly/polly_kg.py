from polly.auth import Polly
from polly.errors import (
    ResourceNotFoundError,
    BadRequestError,
    UnauthorizedException,
    InvalidParameterException,
    QueryFailedException,
)
from polly import helpers
from polly import constants as const
from polly.tracking import Track

import requests
import json
import os
from requests import Response
import time


def get_error_message(response: Response):
    """Helper function to extract error message from response"""
    if "errors" in response.json():
        errors = response.json()["errors"]
        if isinstance(errors, list) and errors:
            return errors[0].get("detail", "Unknown error")
        return errors or "Unknown error"
    return "Unknown error"


def handle_success_and_error_response(response: Response):
    error_message = "Unknown error"

    if response.status_code in [200, 201]:
        return response.json()

    if response.status_code == 204:
        return None

    if response.status_code == 401:
        raise UnauthorizedException()

    error_message = get_error_message(response)

    if response.status_code == 400:
        raise BadRequestError(detail=error_message)
    elif response.status_code == 404:
        raise ResourceNotFoundError(detail=error_message)
    elif response.status_code == 409:
        raise Exception(f"Conflict: {error_message}")

    if int(response.status_code) >= 500:
        raise Exception(f"Server error: {error_message}")

    response.raise_for_status()


def _get_latest_version_kg(session, polly_kg_neo4j_endpoint, kg_id):
    """Get the latest version of the knowledge graph with the specified kg_id.

    Args:
        session: The authenticated session to make requests.
        polly_kg_neo4j_endpoint: The endpoint for the Polly Knowledge Graph API.
        kg_id (str): The ID of the knowledge graph.

    Returns:
        tuple: A tuple containing the kg_id and version_id of the latest version.

    Raises:
        ResourceNotFoundError: If no knowledge graph with the specified kg_id is found.
    """
    response = session.get(f"{polly_kg_neo4j_endpoint}/kg/{kg_id}")
    handle_success_and_error_response(response)
    data = response.json().get("data", {})
    if not data:
        raise ResourceNotFoundError(
            detail=f"No knowledge graph with ID '{kg_id}' found."
        )
    latest_version = data.get("attributes", {})
    return (
        kg_id,
        latest_version.get("version_id"),
    )


def _get_default_kg(session, polly_kg_neo4j_endpoint):
    kg_url = f"{polly_kg_neo4j_endpoint}/kg"
    response = session.get(kg_url)
    handle_success_and_error_response(response)
    data = response.json().get("data", [])
    if not data:
        raise ResourceNotFoundError(detail="No knowledge graphs found.")
    if len(data) > 1:
        raise BadRequestError(
            detail="Multiple knowledge graphs found for the given org. Please specify a kg_id and version_id."
        )
    default_kg = data[0]
    latest_kg_response = session.get(
        f"{polly_kg_neo4j_endpoint}/kg/{default_kg.get('kg_id')}"
    )
    handle_success_and_error_response(latest_kg_response)
    latest_kg = latest_kg_response.json().get("data", {}).get("attributes", {})

    return (
        latest_kg.get("kg_id"),
        latest_kg.get("version_id"),
    )


def _validate_kg_version_exists(session, polly_kg_neo4j_endpoint, kg_id, version_id):
    """Validate if the specified kg_id and version_id exist in the Polly Knowledge Graph.

    Args:
        session: The authenticated session to make requests.
        polly_kg_neo4j_endpoint: The endpoint for the Polly Knowledge Graph API.
        kg_id (str): The ID of the knowledge graph.
        version_id (str): The version ID of the knowledge graph.

    Returns:
        tuple: A tuple containing the kg_id and version_id if they exist.

    Raises:
        ResourceNotFoundError: If the specified kg_id or version_id does not exist.
    """
    response = session.get(
        f"{polly_kg_neo4j_endpoint}/kg/{kg_id}/versions/{version_id}"
    )
    handle_success_and_error_response(response)
    data = response.json().get("data", [])
    if not data:
        raise ResourceNotFoundError(
            detail=f"No knowledge graphs with ID '{kg_id}' and version '{version_id}' found."
        )
    return kg_id, version_id


class PollyKG:
    """The PollyKG class provides an interface to interact with the Polly Knowledge Graph (KG) API.\
     It enables users to execute and manage Cypher queries, retrieve node and relationship data,\
     and analyze graph structures efficiently. This class simplifies access to the KG engine, allowing seamless\
     querying and data exploration. It is designed for users who need to extract insights from complex graph-based datasets.

    Args:
        token (str): Authentication token from polly

    Usage:
        from polly.polly_kg import PollyKG

        kg = PollyKG(token)
    """

    def __init__(
        self,
        token=None,
        env="",
        default_env="polly",
        kg_id=None,
        version_id=None,
    ) -> None:
        # Initialize a PollyKG instance.

        # Args:
        #     token (str, optional): Authentication token. Defaults to None.
        #     env (str, optional): Environment override. Defaults to "".
        #     default_env (str, optional): Default environment if not specified. Defaults to "polly".

        env = helpers.get_platform_value_from_env(
            const.COMPUTE_ENV_VARIABLE, default_env, env
        )
        self.session = Polly.get_session(token, env=env)
        self.polly_kg_endpoint = (
            f"https://sarovar.{self.session.env}.elucidata.io/polly_kg"
        )
        self.polly_kg_neo4j_endpoint = (
            f"https://apis.{self.session.env}.elucidata.io/polly-kg"
        )

        if kg_id is None and version_id is not None:
            raise InvalidParameterException("kg_id")

        if kg_id is None and version_id is None:
            self.kg_id, self.version_id = _get_default_kg(
                self.session, self.polly_kg_neo4j_endpoint
            )
        if kg_id is not None and version_id is not None:
            self.kg_id, self.version_id = _validate_kg_version_exists(
                self.session, self.polly_kg_neo4j_endpoint, kg_id, version_id
            )

        if kg_id is not None and version_id is None:
            self.kg_id, self.version_id = _get_latest_version_kg(
                self.session, self.polly_kg_neo4j_endpoint, kg_id
            )

    def __repr__(self):
        return f"PollyKG(kg_id={self.kg_id}, version_id={self.version_id})"

    @Track.track_decorator
    def run_query(self, query: str, query_type: str = "CYPHER") -> dict:
        """
        Execute a graph query on the specified KG version.

        This function submits the query to Polly KG, tracks its status, and waits
        until it completes. Once complete, it returns the result.

        Args:
            query (str): The query string to be executed.
            query_type (str): The query language type. Accepts "CYPHER".

        Returns:
            dict: Query result in parsed JSON format.

        Raises:
            InvalidParameterException: If query is empty.
            QueryFailedException: If query execution fails.
        """
        if not query or query == "":
            raise InvalidParameterException("query")
        query_url = f"{self.polly_kg_neo4j_endpoint}/kg/{self.kg_id}/versions/{self.version_id}/queries/"
        payload = {
            "data": {
                "type": "kg_query",
                "attributes": {
                    "query_string": query,
                    "query_type": query_type,
                },
            }
        }
        try:
            query_response = self.session.post(query_url, data=json.dumps(payload))

            handle_success_and_error_response(query_response)

            data = query_response.json().get("data")
            query_id = data.get("attributes", {}).get("query_id")
            print(f"Query submitted successfully. Query ID: {query_id}. ")

            download_url = f"{query_url}{query_id}/results?download=true"

            status_response = self.session.get(download_url)

            status = (
                status_response.json()
                .get("data", {})
                .get("attributes", {})
                .get("status")
            )

            while status in ("IN_PROGRESS", "QUEUED"):
                time.sleep(5)  # Wait for 5 seconds before checking the status again
                status_response = self.session.get(download_url)
                status = (
                    status_response.json()
                    .get("data", {})
                    .get("attributes", {})
                    .get("status")
                )

            if status == "COMPLETED":
                result_s3_signed_url = (
                    status_response.json()
                    .get("data", {})
                    .get("attributes", {})
                    .get("metadata", {})
                    .get("results", {})
                    .get("url")
                )
                result_json = requests.get(result_s3_signed_url)
                return result_json.json()
            elif status == "FAILED":
                raise QueryFailedException(
                    status_response.json()
                    .get("data", {})
                    .get("attributes", {})
                    .get("metadata", {})
                    .get("error")
                )
        except Exception as e:
            print(e)
            raise e

    @Track.track_decorator
    def get_query_status(self, query_id: str) -> dict:
        """
        Fetch the status of a  submitted query.

        Args:
            query_id (str): Unique ID of the submitted query.

        Returns:
            dict: A dictionary containing current status of the query (e.g., "IN_PROGRESS", "COMPLETED").

        Raises:
            InvalidParameterException: If query_id is not provided.
        """
        if not query_id or query_id == "":
            raise InvalidParameterException("query_id")
        query_url = f"{self.polly_kg_neo4j_endpoint}/kg/{self.kg_id}/versions/{self.version_id}/queries/{query_id}"
        try:
            response = self.session.get(query_url)
            handle_success_and_error_response(response)
            data = response.json().get("data", {})
            print({"status": data.get("attributes", {}).get("status")})
        except Exception as e:
            print(e)
            raise e

    @Track.track_decorator
    def download_query_results(self, query_id: str) -> None:
        """Download the results of a query by its ID.
            The results will be saved in a ./results directory/query_id.json with the filename as query_id.json.

        Args:
            query_id (str): The ID of the query whose results you want to download.

        Raises:
            InvalidParameterException: If the query_id is empty or None.
            QueryFailedException: If query execution failed.
            RequestFailureException: If the request fails due to an unexpected error.

        """
        if not query_id or query_id == "":
            raise InvalidParameterException("query_id")
        base_url = f"{self.polly_kg_neo4j_endpoint}/kg/{self.kg_id}/versions/{self.version_id}/queries"
        query_url = f"{base_url}/{query_id}/results?download=true"
        try:
            response = self.session.get(query_url)
            handle_success_and_error_response(response)
            data = response.json().get("data", {})

            status = data.get("attributes", {}).get("status")
            if status == "FAILED":
                raise QueryFailedException(
                    data.get("attributes", {})
                    .get("metadata", {})
                    .get("error", "Query failed without a specific error message.")
                )
            result_s3_signed_url = (
                data.get("attributes", {})
                .get("metadata", {})
                .get("results", {})
                .get("url")
            )
            if not result_s3_signed_url:
                raise ResourceNotFoundError("Query results not found.")

            result_json = requests.get(result_s3_signed_url)
            results_dir = "./results"
            os.makedirs(results_dir, exist_ok=True)
            with open(os.path.join(results_dir, f"{query_id}.json"), "w") as f:
                json.dump(result_json.json(), f, indent=4)
            print(f"Results downloaded successfully to {results_dir}/{query_id}.json")
        except Exception as e:
            print(e)
            raise

    def get_summary(self) -> dict:
        """Retrieve a summary of the Polly Knowledge Graph.

        Returns:
            dict: A dictionary containing summary information about the graph,
                 such as node counts, edge counts, and other metadata.

        Raises:
            ResourceNotFoundError: Raised when the specified graph summary does not exist.
            AccessDeniedError: Raised when the user does not have permission to access the graph summary.
            RequestFailureException: Raised when the request fails due to an unexpected error.
        """
        try:
            response = self.session.get(
                f"{self.polly_kg_neo4j_endpoint}/kg/{self.kg_id}/versions/{self.version_id}/summary"
            )
            return handle_success_and_error_response(response)
        except Exception as e:
            print(e)

    def get_schema(self) -> dict:
        """Retrieve the schema of the Polly Knowledge Graph.

        Returns:
            dict: A dictionary containing schema information about the graph,
                 such as node types, relationship types, and other metadata.

        Raises:
            ResourceNotFoundError: Raised when the specified graph schema does not exist.
            AccessDeniedError: Raised when the user does not have permission to access the graph schema.
            RequestFailureException: Raised when the request fails due to an unexpected error.
        """
        try:
            response = self.session.get(
                f"{self.polly_kg_neo4j_endpoint}/kg/{self.kg_id}/versions/{self.version_id}/schema"
            )
            return handle_success_and_error_response(response)
        except Exception as e:
            print(e)
