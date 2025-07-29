import json

import pytest
from fastapi.testclient import TestClient
from qualpipe_webapp.backend.main import app, load_ob_date_map

client = TestClient(app)


@pytest.mark.verifies_usecase("UC-140-2.1")
def test_load_ob_date_map(tmp_path):
    test_data = {"2024-01-01": {"some": "value"}}
    test_file = tmp_path / "ob_date_map.json"
    test_file.write_text(json.dumps(test_data))
    result = load_ob_date_map(str(test_file))
    assert result == test_data


@pytest.mark.verifies_usecase("UC-140-2.1")
def test_load_ob_date_map_file_not_found(tmp_path):
    test_file = tmp_path / "ob_date_map.json"
    result = load_ob_date_map(str(test_file))
    assert "error" in result


@pytest.mark.verifies_usecase("UC-140-2.1")
def test_get_ob_date_map_endpoint(tmp_path, monkeypatch):
    test_data = {"2024-01-01": {"some": "value"}}
    test_file = tmp_path / "ob_date_map.json"
    test_file.write_text(json.dumps(test_data))

    monkeypatch.setattr(
        "qualpipe_webapp.backend.main.load_ob_date_map",
        lambda file_path=None: test_data,
    )

    response = client.get("/v1/ob_date_map")
    assert response.status_code == 200
    assert response.json() == test_data


@pytest.mark.verifies_usecase("UC-140-2.1")
def test_get_data_file_not_found():
    response = client.get(
        "/v1/data",
        params={
            "site": "North",
            "date": "2024-01-01",
            "ob": 1,
            "telescope_type": "LST",
            "telescope_id": 999,
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.verifies_usecase("UC-140-2.1")
def test_get_data_invalid_telescope_type():
    response = client.get(
        "/v1/data",
        params={
            "site": "North",
            "date": "2024-01-01",
            "ob": 1,
            "telescope_type": "INVALID",
            "telescope_id": 1,
        },
    )
    assert response.status_code == 400
    assert "Invalid telescope type" in response.json()["detail"]


@pytest.mark.verifies_usecase("UC-140-2.1")
def test_load_ob_date_map_invalid_json(tmp_path):
    # Create a file with invalid JSON content
    test_file = tmp_path / "ob_date_map.json"
    test_file.write_text("{invalid_json: true,}")  # malformed JSON
    result = load_ob_date_map(str(test_file))
    assert "error" in result
    assert "Expecting property name enclosed in double quotes" in result["error"]
