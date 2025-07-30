import pytest
from fastapi.testclient import TestClient
from dbt_run_api import app, DbtRunConfig

client = TestClient(app)

# Define test cases

def test_prepare_command():
    config = DbtRunConfig(cmd="dbt run --profiles-dir profiles --target prod")
    assert config.prepare_command() == ["run", "--profiles-dir", "profiles", "--target", "prod"]

def test_callback_endpoint():
    response = client.get("/callback")
    assert response.status_code == 200
    assert response.json() == {"message": "This endpoint works!"}

def test_dbt_endpoint():
    data = {"cmd": "dbt run --profiles-dir profiles --target prod"}
    response = client.post("/dbt", json=data)
    assert response.status_code == 200
    assert "pid" in response.json()