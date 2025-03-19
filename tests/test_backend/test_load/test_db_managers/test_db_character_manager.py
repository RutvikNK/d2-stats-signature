import unittest
from unittest.mock import MagicMock, patch
import json

from backend.load.managers import DatabaseCharacterManager

class TestDatabaseCharacterManager(unittest.TestCase):
    def setUp(self):
        self.db_exec = MagicMock()
        self.db_manager = DatabaseCharacterManager(self.db_exec)

    def test_db_character_manager_init(self):
        assert self.db_manager._DatabaseCharacterManager__control == self.db_exec
        
        assert self.db_manager._DatabaseCharacterManager__characters == []

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_db_character_manager_successful_add_new_character(self, mock_urlopen):
        mock_character_response = {"Response": 
            {"character": {
                "data": {
                    "classType": 1,
                    "dateLastPlayed": "2017-07-07T07:07:07Z"
                }
            }}
        }
        mock_equipment_response = {"Response": {
            "equipment": {
                "data": {
                    "items": [
                        {"itemHash": 9009009009},
                        {"itemHash": 8008008008},
                        {"itemHash": 7007007007},
                        {"itemHash": 6006006006},
                        {"itemHash": 5005005005},
                        {"itemHash": 4004004004},
                        {"itemHash": 3003003003},
                        {"itemHash": 2002002002}
                    ]
                }
            }}
        }
        mock_db_response = [
            (1, 101)
        ]
        self.db_exec.select_rows.return_value = mock_db_response
        mock_urlopen.return_value.__enter__.return_value.read.side_effect = [json.dumps(mock_character_response), json.dumps(mock_equipment_response)]

        self.db_manager.add_new_character(111, 1, 101)

        expected_character_data = {
                "bng_character_id": 101,
                "player_id": 1,
                "class": "HUNTER",
                "date_last_played": "2017-07-07",
            }
        assert self.db_manager._DatabaseCharacterManager__characters[0].data == expected_character_data

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_db_character_manager_unsuccessful_add_new_character_no_player(self, mock_urlopen):
        self.db_exec.select_rows.return_value = []

        self.db_manager.add_new_character(111, 1, 101)
        assert self.db_manager._DatabaseCharacterManager__characters[0].data == []
        