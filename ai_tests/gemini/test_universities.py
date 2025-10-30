import pytest
import pytest_asyncio
import httpx
import json
from unittest.mock import MagicMock, AsyncMock

# We need to import the functions to test
from universities import get_all_universities_for_country, get_all_universities_for_country_async

# Mock response data from the external API
MOCK_API_RESPONSE = [
    {"name": "Test University 1", "country": "Testland", "web_pages": ["http://test1.com"]},
    {"name": "Test University 2", "country": "Testland", "web_pages": ["http://test2.com"]}
]
MOCK_JSON_RESPONSE = json.dumps(MOCK_API_RESPONSE)

@pytest.fixture
def mock_university_schema(mocker):
    """
    Mocks the University schema from the missing sql_app.schemas module.
    Pytest's 'mocker' fixture allows us to patch the import in universities.py.
    """
    
    # Create a mock class that simulates Pydantic's parse_obj
    # We'll just have it return a simple dict representation for testing
    mock_uni = MagicMock()
    mock_uni.parse_obj.side_effect = lambda x: {"parsed_name": x["name"]} # Simulate parsing
    
    # Patch the import location used *inside* the universities.py file
    mocker.patch('universities.University', mock_uni)
    return mock_uni

@pytest.fixture
def mock_httpx_client(mocker):
    """Mocks the synchronous httpx.Client."""
    
    # Create a mock response object
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.text = MOCK_JSON_RESPONSE
    mock_response.status_code = 200
    
    # Create a mock client
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response
    
    # Patch httpx.Client to return our mock client when instantiated
    mocker.patch('httpx.Client', return_value=mock_client)
    return mock_client

@pytest.fixture
def mock_httpx_async_client(mocker):
    """Mocks the asynchronous httpx.AsyncClient."""
    
    # Create a mock response object
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.text = MOCK_JSON_RESPONSE
    mock_response.status_code = 200
    
    # The async client is used in a context manager ('async with')
    # So we need to mock the async methods
    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    mock_async_client.get = AsyncMock(return_value=mock_response)
    
    # Mock the __aenter__ method to return the client instance
    mock_async_client.__aenter__.return_value = mock_async_client
    
    # Patch httpx.AsyncClient to return our mock client
    mocker.patch('httpx.AsyncClient', return_value=mock_async_client)
    return mock_async_client

def test_get_all_universities_for_country_sync(mock_httpx_client, mock_university_schema):
    """Tests the synchronous university fetching function."""
    country = "Testland"
    result = get_all_universities_for_country(country)
    
    # Check if httpx.Client.get was called correctly
    mock_httpx_client.get.assert_called_once_with(
        'http://universities.hipolabs.com/search',
        params={'country': country}
    )
    
    # Check if University.parse_obj was called for each item
    assert mock_university_schema.parse_obj.call_count == len(MOCK_API_RESPONSE)
    mock_university_schema.parse_obj.assert_any_call(MOCK_API_RESPONSE[0])
    mock_university_schema.parse_obj.assert_any_call(MOCK_API_RESPONSE[1])
    
    # Check the final returned data structure based on our mock parser
    expected_data = [
        {"parsed_name": "Test University 1"},
        {"parsed_name": "Test University 2"}
    ]
    assert result == {country: expected_data}

@pytest.mark.asyncio
async def test_get_all_universities_for_country_async(mock_httpx_async_client, mock_university_schema):
    """Tests the asynchronous university fetching function."""
    country = "Testland"
    data = {} # The function modifies this dict in-place
    
    await get_all_universities_for_country_async(country, data)
    
    # Check if httpx.AsyncClient.get was called correctly
    mock_httpx_async_client.get.assert_called_once_with(
        'http://universities.hipolabs.com/search',
        params={'country': country}
    )
    
    # Check if University.parse_obj was called for each item
    assert mock_university_schema.parse_obj.call_count == len(MOCK_API_RESPONSE)
    mock_university_schema.parse_obj.assert_any_call(MOCK_API_RESPONSE[0])
    
    # Check if the data dict was populated correctly
    expected_data = [
        {"parsed_name": "Test University 1"},
        {"parsed_name": "Test University 2"}
    ]
    assert data == {country: expected_data}
