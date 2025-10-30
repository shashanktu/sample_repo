import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_get_universities(monkeypatch):
    mock_data = {"turkey": ["u1"], "india": ["u2"], "australia": ["u3"]}
    monkeypatch.setattr("universities.get_all_universities_for_country", lambda c: {c: [f"{c}_uni"]})
    response = client.get("/universities/")
    assert response.status_code == 200
    assert "turkey" in response.json()

@pytest.mark.asyncio
@patch("universities.get_all_universities_for_country_async", new_callable=AsyncMock)
async def test_get_universities_async(mock_async):
    mock_async.side_effect = lambda country, data: data.update({country: [f"{country}_uni"]})
    response = await client.get("/universities/async")
    assert response.status_code == 200
    data = response.json()
    assert "india" in data
    assert "australia" in data
