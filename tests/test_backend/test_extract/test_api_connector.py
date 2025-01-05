import json
import unittest
from unittest.mock import patch

from backend.extract.bng_api_connector import BungieConnector

class APIConnectorTestCase(unittest.TestCase):
    @patch("backend.extract.bng_api_connector.urlopen")
    def test_successful_bng_api_response(self, mock_urlopen):
        conn = BungieConnector("test_api_key")

        response_data = {"Response": {"test_response": "player1"}}
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(response_data)

        test_path = "https://example.com/api"
        result = conn.get_url_request(test_path)
        assert result == response_data.get("Response")

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_unsuccessful_bng_api_response(self, mock_urlopen):
        conn = BungieConnector("test_api_key")
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps("")

        test_path = "https://example.com/api"
        result = conn.get_url_request(test_path)
        assert result is None
