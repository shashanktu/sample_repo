import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_app.models import Base
from main import app, get_db
from db import SQLALCHEMY_DATABASE_URL

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test_data.db"

# Override the engine and session for testing
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Recreate tables
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# === University Endpoints ===

def test_get_universities_sync():
    with patch("universities.get_all_universities_for_country", return_value={"turkey": []}) as mock_sync:
        response = client.get("/universities/")
        assert response.status_code == 200
        data = response.json()
        assert "turkey" in data
        assert "india" in data
        assert "australia" in data
        assert mock_sync.call_count == 3


@pytest.mark.asyncio
async def test_get_universities_async():
    mock_univ = MagicMock()
    mock_univ.name = "Test University"
    mock_univ.country = "turkey"
    mock_univ.web_pages = ["http://test.edu"]

    with patch("universities.get_all_universities_for_country_async", new_callable=AsyncMock) as mock_async:
        response = client.get("/universities/async")
        assert response.status_code == 200
        data = response.json()
        assert "turkey" in data
        assert mock_async.call_count == 3


# === Item Endpoints ===

def test_create_item():
    item_data = {
        "name": "Laptop",
        "price": 999.99,
        "description": "High-end gaming laptop",
        "store_id": 1
    }
    response = client.post("/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99
    assert "id" in data


def test_create_duplicate_item():
    item_data = {"name": "Phone", "price": 499.99, "description": "Smartphone", "store_id": 1}
    client.post("/items", json=item_data)  # First creation
    response = client.post("/items", json=item_data)  # Duplicate
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_all_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_item_by_id():
    # Create an item first
    create_resp = client.post("/items", json={"name": "Tablet", "price": 299.99, "store_id": 1})
    item_id = create_resp.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Tablet"


def test_get_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_item():
    # Create item
    create_resp = client.post("/items", json={"name": "Mouse", "price": 25.0, "store_id": 1})
    item_id = create_resp.json()["id"]

    update_data = {
        "name": "Wireless Mouse",
        "price": 35.0,
        "description": "Bluetooth mouse",
        "store_id": 1
    }
    response = client.put(f"/items/{item_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Wireless Mouse"
    assert response.json()["price"] == 35.0


def test_delete_item():
    # Create item
    create_resp = client.post("/items", json={"name": "Keyboard", "price": 75.0, "store_id": 1})
    item_id = create_resp.json()["id"]

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == "Item deleted successfully!"

    # Verify it's gone
    get_resp = client.get(f"/items/{item_id}")
    assert get_resp.status_code == 404


# === Store Endpoints ===

def test_create_store():
    store_data = {"name": "Electronics Hub"}
    response = client.post("/stores", json=store_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Electronics Hub"


def test_create_duplicate_store():
    client.post("/stores", json={"name": "Bookstore"})
    response = client.post("/stores", json={"name": "Bookstore"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_all_stores():
    response = client.get("/stores")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_store_by_id():
    create_resp = client.post("/stores", json={"name": "Grocery Store"})
    store_id = create_resp.json()["id"]

    response = client.get(f"/stores/{store_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Grocery Store"


def test_delete_store():
    create_resp = client.post("/stores", json={"name": "Fashion Outlet"})
    store_id = create_resp.json()["id"]

    response = client.delete(f"/stores/{store_id}")
    assert response.status_code == 200
    assert response.json() == "Store deleted successfully!"


# === Middleware Test ===

def test_process_time_header():
    response = client.get("/items")
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"][:-4]) >= 0  # Remove ' sec'


# === Exception Handler ===

def test_exception_handler():
    with patch("sql_app.repositories.ItemRepo.fetch_all", side_effect=Exception("DB error")):
        response = client.get("/items")
        assert response.status_code == 400
        assert "Failed to execute" in response.json()["message"]
        assert "DB error" in response.json()["message"]