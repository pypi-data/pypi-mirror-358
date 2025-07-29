# from polly import polly_kg
from polly.polly_kg import PollyKG
import pytest

import os
from polly.errors import (
    InvalidParameterException,
    QueryFailedException,
)

key = "POLLY_API_KEY"
token = os.getenv(key)

test_key = "TEST_POLLY_API_KEY"
testpolly_token = os.getenv(test_key)


def test_obj_initialised_with_kg_and_version(mocker):
    mocker.patch(
        "polly.polly_kg._validate_kg_version_exists", return_value=("kg-xyz", "v9")
    )
    obj = PollyKG(token, kg_id="kg-xyz", version_id="v9")
    assert obj.kg_id == "kg-xyz"
    assert obj.version_id == "v9"


def test_run_query_success(mocker):
    mocker.patch(
        "polly.polly_kg._validate_kg_version_exists", return_value=("kg-xyz", "v9")
    )
    obj = PollyKG(token=token, kg_id="kg-xyz", version_id="v9")
    mock_post = mocker.patch.object(obj.session, "post")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "data": {"attributes": {"query_id": "test-query-id"}}
    }

    mock_status = mocker.patch.object(obj.session, "get")
    mock_status.return_value.status_code = 200
    mock_status.return_value.json.return_value = {
        "data": {
            "attributes": {
                "status": "COMPLETED",
                "metadata": {"results": {"url": "https://s3-bucket/test.json"}},
            }
        }
    }

    mock_requests_get = mocker.patch("polly.polly_kg.requests.get")
    mock_requests_get.return_value.json.return_value = {"result": "success"}

    result = obj.run_query("MATCH (n) RETURN count(n);")
    assert result["result"] == "success"


def test_run_query_invalid_input(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))
    obj = PollyKG(token=token)
    with pytest.raises(InvalidParameterException):
        obj.run_query("")


def test_run_query_failed_execution(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))

    obj = PollyKG(token=token)

    mocker.patch.object(
        obj.session,
        "post",
        return_value=mocker.Mock(
            status_code=200,
            json=lambda: {"data": {"attributes": {"query_id": "q1"}}},
        ),
    )

    mocker.patch.object(
        obj.session,
        "get",
        return_value=mocker.Mock(
            status_code=200,
            json=lambda: {
                "data": {
                    "attributes": {
                        "status": "FAILED",
                        "metadata": {"error": "Query timed out"},
                    }
                }
            },
        ),
    )

    with pytest.raises(QueryFailedException, match="Query timed out"):
        obj.run_query("MATCH (n) RETURN count(n);")


def test_get_query_status_completed(mocker, capsys):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))

    obj = PollyKG(token=token)

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"attributes": {"status": "COMPLETED"}}}

    mocker.patch.object(obj.session, "get", return_value=mock_response)
    obj.get_query_status("test-id")

    captured = capsys.readouterr()
    assert "COMPLETED" in captured.out


def test_get_query_status_invalid_input(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))

    mocker.patch(
        "polly.polly_kg._validate_kg_version_exists", return_value=("kg1", "v1")
    )
    obj = PollyKG(token=token)
    with pytest.raises(InvalidParameterException):
        obj.get_query_status("")


def test_download_query_results_success(mocker, tmp_path):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))
    obj = PollyKG(token=token)
    query_id = "query-download-id"

    mock_status_response = {
        "data": {
            "attributes": {
                "status": "COMPLETED",
                "metadata": {"results": {"url": "https://mock-bucket.com/output.json"}},
            }
        }
    }

    mocker.patch.object(
        obj.session,
        "get",
        return_value=mocker.Mock(
            status_code=200,
            json=lambda: mock_status_response,
        ),
    )

    mocker.patch("polly.polly_kg.requests.get").return_value.json.return_value = {
        "data": "mocked"
    }

    mocker.patch("polly.polly_kg.os.makedirs")
    mock_open = mocker.patch("polly.polly_kg.open", create=True)
    mock_file = mock_open.return_value.__enter__.return_value

    obj.download_query_results(query_id)

    mock_file.write.assert_called()


def test_download_query_results_invalid_input(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))
    obj = PollyKG(token=token)
    with pytest.raises(InvalidParameterException):
        obj.download_query_results("")


def test_download_query_results_failed_status(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))

    obj = PollyKG(token=token)
    query_id = "failed-query"

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "data": {
            "attributes": {
                "status": "FAILED",
                "metadata": {"error": "Execution error"},
            }
        }
    }

    mocker.patch.object(obj.session, "get", return_value=mock_response)

    with pytest.raises(QueryFailedException, match="Execution error"):
        obj.download_query_results(query_id)


def test_get_summary_success(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))

    obj = PollyKG(token=token)
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"summary": {"nodes": 10}}

    mocker.patch.object(obj.session, "get", return_value=mock_response)
    result = obj.get_summary()

    assert result["summary"]["nodes"] == 10


def test_get_schema_success(mocker):
    mocker.patch("polly.polly_kg._get_default_kg", return_value=("kg1", "v1"))

    obj = PollyKG(token=token)
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"schema": {"labels": ["Disease", "Drug"]}}

    mocker.patch.object(obj.session, "get", return_value=mock_response)
    result = obj.get_schema()

    assert "Disease" in result["schema"]["labels"]
