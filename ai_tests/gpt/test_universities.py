import pytest
import universities
import httpx
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_university_data():
    return [
        {
            "name": "Test University",
            "country": "Testland",
            "alpha_two_code": "TL",
            "domains": ["testuniv.edu"],
            "web_pages": ["http://www.testuniv.edu"]
        }
    ]

@patch("universities.httpx.Client.get")
def test_get_all_universities_for_country(mock_get, mock_university_data):
    # Mock the HTTP response
    mock_response = MagicMock()
    mock_response.text = '[{"name": "Test University", "country": "Testland"}]'
    mock_get.return_value = mock_response

    result = universities.get_all_universities_for_country("Testland")
    assert "Testland" in result
    assert isinstance(result["Testland"], list)
    assert len(result["Testland"]) == 1


@pytest.mark.asyncio
@patch("universities.httpx.AsyncClient.get")
async def test_get_all_universities_for_country_async(mock_get, mock_university_data):
    # Mock async response
    mock_response = MagicMock()
    mock_response.text = '[{"name": "Async University", "country": "AsyncLand"}]'
    mock_get.return_value = mock_response

    data = {}
    await universities.get_all_universities_for_country_async("AsyncLand", data)
    assert "AsyncLand" in data
    assert isinstance(data["AsyncLand"], list)
    assert len(data["AsyncLand"]) == 1
