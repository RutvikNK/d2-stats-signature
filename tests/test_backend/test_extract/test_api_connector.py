import json

from backend.extract.bng_api_connector import BungieConnector

def test_successful_bng_api_response(mocker):
    conn = BungieConnector("test_api_key")

    mock_urlopen = mocker.patch("backend.extract.bng_api_connector.urlopen")
    response_data = {"Response": {"test_response": "player1"}}
    mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(response_data)

    test_path = "https://example.com/api"
    result = conn.get_url_request(test_path)
    assert result == response_data.get("Response")

def test_unsuccessful_bng_api_response(mocker):
    conn = BungieConnector("test_api_key")

    mock_urlopen = mocker.patch("backend.extract.bng_api_connector.urlopen")
    mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps("")

    test_path = "https://example.com/api"
    result = conn.get_url_request(test_path)
    assert result is None
