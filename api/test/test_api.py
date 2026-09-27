import os

import pytest
from fastapi.testclient import TestClient

# Définir les variables d'environnement avant d'importer l'API
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("ADMIN_PASSWORD", "test_admin_password")

from api.api import app, generate_token  # noqa: E402

client = TestClient(app)

PAYLOAD = {
    "experience_level": "se",
    "employment_type": "ft",
    "job_title": "dataengineer",
    "employee_residence": "gb",
    "remote_ratio": "0",
    "company_location": "gb",
    "company_size": "m"
}


@pytest.fixture
def token():
    return generate_token("admin")


def test_login():
    response = client.post("/token", data={"username": "admin", "password": os.environ["ADMIN_PASSWORD"]})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_login():
    response = client.post("/token", data={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401


def test_predict(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/predict", json=PAYLOAD, headers=headers)
    assert response.status_code == 200
    assert "prediction" in response.json()


def test_predict_normalizes_input(token):
    headers = {"Authorization": f"Bearer {token}"}
    raw_payload = {
        "experience_level": "SE",
        "employment_type": "FT",
        "job_title": "Data Engineer",
        "employee_residence": "GB",
        "remote_ratio": "0",
        "company_location": "GB",
        "company_size": "M"
    }
    clean = client.post("/predict", json=PAYLOAD, headers=headers).json()["prediction"]
    raw = client.post("/predict", json=raw_payload, headers=headers).json()["prediction"]
    assert raw == pytest.approx(clean)


def test_predict_without_token():
    response = client.post("/predict", json=PAYLOAD)
    assert response.status_code == 401


def test_predict_with_invalid_token():
    headers = {"Authorization": "Bearer invalid"}
    response = client.post("/predict", json=PAYLOAD, headers=headers)
    assert response.status_code == 401
