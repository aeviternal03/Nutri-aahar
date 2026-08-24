"""Regression coverage for the Nutri-Aahar catalogue and enquiry APIs."""
import os
import subprocess
from collections import Counter
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

EXPECTED_COUNTS = {
    "Whole Spices": 13,
    "Makhana": 6,
    "Atta & Flours": 6,
    "Dates & Dry Fruits": 4,
    "Spice Powders": 3,
    "Seeds & Specialty": 3,
}


@pytest.fixture
def api_client():
    with requests.Session() as session:
        session.headers.update({"Content-Type": "application/json"})
        yield session


# --- Module: root + catalogue ---
def test_root_and_products(api_client):
    root = api_client.get(f"{BASE_URL}/api/")
    assert root.status_code == 200
    assert root.json()["message"] == "Nutri-Aahar API"
    response = api_client.get(f"{BASE_URL}/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 35, f"expected 35 products, got {len(products)}"
    assert all({"slug", "name", "category", "description", "uses"} <= set(p) for p in products)
    slugs = [p["slug"] for p in products]
    assert len(set(slugs)) == len(slugs), "duplicate slugs in catalogue"


def test_products_category_distribution(api_client):
    products = api_client.get(f"{BASE_URL}/api/products").json()
    assert dict(Counter(p["category"] for p in products)) == EXPECTED_COUNTS


@pytest.mark.parametrize("category,expected", sorted(EXPECTED_COUNTS.items()))
def test_product_category_filter(api_client, category, expected):
    response = api_client.get(f"{BASE_URL}/api/products", params={"category": category})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == expected
    assert all(product["category"] == category for product in products)


@pytest.mark.parametrize("alias", ["Dates", "Dry Fruits"])
def test_dates_alias_filters(api_client, alias):
    """Frontend exposes Dates / Dry Fruits labels that map to Dates & Dry Fruits."""
    response = api_client.get(f"{BASE_URL}/api/products", params={"category": alias})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 4
    assert all(p["category"] == "Dates & Dry Fruits" for p in products)


def test_unknown_category_returns_empty(api_client):
    response = api_client.get(f"{BASE_URL}/api/products", params={"category": "Nope"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("slug", [
    "wheat-atta", "besan-gram-flour", "ragi-atta", "bajra-atta", "jowar-atta",
    "soyabean-atta", "roasted-cheese-makhana", "star-anise", "raw-makhana",
])
def test_new_product_slugs_present_with_image(api_client, slug):
    products = api_client.get(f"{BASE_URL}/api/products").json()
    match = next((p for p in products if p["slug"] == slug), None)
    assert match is not None, f"{slug} missing from catalogue"
    assert match["image"].startswith("http")
    assert match["name"] and match["description"] and match["uses"]


def test_makhana_detail_fields(api_client):
    products = api_client.get(f"{BASE_URL}/api/products", params={"category": "Makhana"}).json()
    cheese = next(p for p in products if p["slug"] == "roasted-cheese-makhana")
    for field in ("benefits", "nutrition", "shelf_life", "form"):
        assert cheese.get(field), f"missing {field}"


# --- Module: enquiries (with Resend email skip) ---
@pytest.mark.parametrize("enquiry_type", ["quote", "b2b", "export", "contact"])
def test_enquiry_create_and_persisted_get(api_client, enquiry_type):
    payload = {
        "enquiry_type": enquiry_type,
        "name": f"TEST {enquiry_type} Buyer",
        "company": "TEST Co",
        "email": f"test-{enquiry_type}@example.com",
        "phone": "+910000000000",
        "country": "India",
        "product": "Cumin Seeds",
        "quantity": "500 kg",
        "packaging": "25kg bags",
        "destination": "Dubai",
        "subject": "TEST subject",
        "message": f"TEST persistence check {enquiry_type}",
    }
    created = api_client.post(f"{BASE_URL}/api/enquiries", json=payload)
    assert created.status_code == 200, created.text[:400]
    data = created.json()
    assert data["name"] == payload["name"]
    assert data["enquiry_type"] == enquiry_type
    assert isinstance(data["id"], str) and data["id"]
    assert data["created_at"]
    assert "_id" not in data

    enquiries = api_client.get(f"{BASE_URL}/api/enquiries")
    assert enquiries.status_code == 200
    saved = next((i for i in enquiries.json() if i["id"] == data["id"]), None)
    assert saved is not None, "enquiry not persisted"
    assert saved["message"] == payload["message"]
    assert saved["email"] == payload["email"]
    assert "_id" not in saved


def test_email_notification_gracefully_skipped():
    """RESEND_API_KEY is empty: enquiry must succeed and log a skip message."""
    log_dir = Path("/var/log/supervisor")
    logs = list(log_dir.glob("backend*.log")) if log_dir.exists() else []
    if not logs:
        pytest.skip("supervisor backend logs unavailable")
    text = "\n".join(
        subprocess.run(["tail", "-n", "400", str(p)], capture_output=True, text=True).stdout
        for p in logs
    )
    assert "Email notification skipped" in text, "expected graceful email skip log entry"
    assert "Failed to send enquiry email" not in text.split("Email notification skipped")[-1]


def test_enquiry_rejects_missing_required_fields(api_client):
    response = api_client.post(f"{BASE_URL}/api/enquiries", json={"email": "bad@example.com"})
    assert response.status_code == 422
