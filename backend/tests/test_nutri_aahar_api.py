"""Regression coverage for the Nutri-Aahar catalogue and enquiry APIs."""
import os
from pathlib import Path

import pytest
import requests


def _backend_url():
    value = os.environ.get("REACT_APP_BACKEND_URL")
    if not value:
        env_file = Path(__file__).parents[2] / "frontend" / ".env"
        for line in env_file.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                value = line.split("=", 1)[1].strip()
                break
    if not value:
        pytest.fail("REACT_APP_BACKEND_URL is not configured")
    return value.rstrip("/")


BASE_URL = _backend_url()


@pytest.fixture
def api_client():
    with requests.Session() as session:
        session.headers.update({"Content-Type": "application/json"})
        yield session


def test_root_and_products(api_client):
    root = api_client.get(f"{BASE_URL}/api/")
    assert root.status_code == 200
    assert root.json()["message"] == "Nutri-Aahar API"
    response = api_client.get(f"{BASE_URL}/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 29
    assert all({"slug", "name", "category", "description", "uses"} <= set(p) for p in products)


@pytest.mark.parametrize("category,expected", [("Whole Spices", 13), ("Makhana", 6), ("Spice Powders", 3), ("Seeds & Specialty", 3)])
def test_product_category_filter(api_client, category, expected):
    response = api_client.get(f"{BASE_URL}/api/products", params={"category": category})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == expected
    assert all(product["category"] == category for product in products)


def test_enquiry_create_and_persisted_get(api_client):
    payload = {
        "enquiry_type": "TEST_quote",
        "name": "TEST API Buyer",
        "email": "test-api-buyer@example.com",
        "product": "Cumin Seeds",
        "message": "TEST persistence check",
    }
    created = api_client.post(f"{BASE_URL}/api/enquiries", json=payload)
    assert created.status_code == 200
    data = created.json()
    assert data["name"] == payload["name"]
    assert isinstance(data["id"], str) and data["id"]
    enquiries = api_client.get(f"{BASE_URL}/api/enquiries")
    assert enquiries.status_code == 200
    assert any(item["id"] == data["id"] and item["message"] == payload["message"] for item in enquiries.json())


def test_enquiry_rejects_missing_required_fields(api_client):
    response = api_client.post(f"{BASE_URL}/api/enquiries", json={"email": "bad@example.com"})
    assert response.status_code == 422