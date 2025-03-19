import unittest
from unittest.mock import MagicMock, patch
import json

from backend.load.managers import DatabasePlayerManager

class DBPlayerManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_exec = MagicMock()
        self.player_manager = DatabasePlayerManager(self.db_exec)

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_db_player_manager_successful_read_data_single(self, mock_urlopen):
        mock_member_response = {"Response": 
            {
                "bungieNetUser": {
                    "firstAccess": "2007-07-07T07:07:07Z",
                    "membershipId": "77777777777777777",
                    "uniqueName": "Bungie Net User"
                }
            }
        }   
        mock_profile_response = {"Response": 
            {
                "profile": {
                    "data": {
                        "dateLastPlayed": "2017-07-07T07:07:07Z",
                        "characterIds": [
                            "111111111111",
                            "222222222222",
                            "333333333333"
                        ]
                    }
                }
            }
        }
        mock_retrieve_all_response = [
            [
                1,
                1010101010101,
                77777777777777777,
                "Bungie Net User",
                "2007-07-07",
                "2017-07-07",
                "XBOX",
                "111111111111, 222222222222, 333333333333"
            ]
        ]

        self.db_exec.retrieve_all.return_value = mock_retrieve_all_response
        mock_urlopen.return_value.__enter__.return_value.read.side_effect = [json.dumps(mock_member_response), json.dumps(mock_profile_response)]

        self.player_manager.read_data()

        expected_player_data = {
            "date_created": "2007-07-07",
            "date_last_played": "2017-07-07",
            "bng_id": 77777777777777777,
            "destiny_id": 1010101010101,
            "bng_username": "Bungie Net User",
            "platform": "XBOX",
            "character_ids": [
                "111111111111",
                "222222222222",
                "333333333333"
            ]
        }
        self.db_exec.retrieve_all.assert_called_with("`Player`")
        assert self.player_manager._DatabasePlayerManager__players[0].data == expected_player_data

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_db_player_manager_successful_read_data_multiple(self, mock_urlopen):
        mock_retrieve_all = [
            [
                1,
                1010101010101,
                77777777777777777,
                "User 1",
                "2007-07-07",
                "2017-07-07",
                "XBOX",
                "111111111111, 222222222222, 333333333333"
            ],
            [
                2,
                2020202020202,
                99999999999999999,
                "User 2",
                "2010-10-10",
                "2012-12-12",
                "STEAM",
                "444444444444, 555555555555, 666666666666"
            ],
            [
                3,
                3030303030303,
                88888888888888888,
                "User 3",
                "2011-11-11",
                "2017-07-07",
                "PSN",
                "777777777777, 888888888888, 999999999999"
            ],
            [
                4,
                4040404040404,
                66666666666666666,
                "User 4",
                "2001-01-01",
                "2022-02-02",
                "XBOX",
                "111111222222, 222222333333, 333333444444"
            ]
        ]
        mock_api_response = [
            {"Response": 
                {   # member response 1
                    "bungieNetUser": {
                        "firstAccess": "2007-07-07T07:07:07Z",
                        "membershipId": "77777777777777777",
                        "uniqueName": "User 1"
                    }
                }
            },
            {"Response": 
                {   # profile response 1
                    "profile": {
                        "data": {
                            "dateLastPlayed": "2017-07-07T07:07:07Z",
                            "characterIds": [
                                "111111111111",
                                "222222222222",
                                "333333333333"
                            ]
                        }
                    }
            }
            },
            {"Response": 
            {   # member response 2
                "bungieNetUser": {
                    "firstAccess": "2010-10-10T10:10:10Z",
                    "membershipId": "99999999999999999",
                    "uniqueName": "User 2"
                }
            }},
            {"Response": 
                {   # profile response 2
                    "profile": {
                        "data": {
                            "dateLastPlayed": "2012-12-12T12:12:12Z",
                            "characterIds": [
                                "444444444444",
                                "555555555555",
                                "666666666666"
                            ]
                        }
                    }
                }
            },
            {"Response": 
                {   # member response 3
                    "bungieNetUser": {
                        "firstAccess": "2011-11-11T11:11:11Z",
                        "membershipId": "88888888888888888",
                        "uniqueName": "User 3"
                    }
                }
            },
            {"Response": 
                {   # profile response 3
                    "profile": {
                        "data": {
                            "dateLastPlayed": "2017-07-07T07:07:07Z",
                            "characterIds": [
                                "777777777777",
                                "888888888888",
                                "999999999999"
                            ]
                        }
                    }
                }
            },
            {"Response": 
                {   # member response 4
                    "bungieNetUser": {
                        "firstAccess": "2001-01-01T01:01:01Z",
                        "membershipId": "66666666666666666",
                        "uniqueName": "User 4"
                    }
                }
            },
            {"Response": 
                {   # profile response 4
                    "profile": {
                        "data": {
                            "dateLastPlayed": "2022-02-02T02:02:02Z",
                            "characterIds": [
                                "111111222222",
                                "222222333333",
                                "333333444444"
                            ]
                        }
                    }
                }
            }
        ]
        for i in range(len(mock_api_response)):
            mock_api_response[i] = json.dumps(mock_api_response[i])

        self.db_exec.retrieve_all.return_value = mock_retrieve_all
        mock_urlopen.return_value.__enter__.return_value.read.side_effect = mock_api_response

        self.player_manager.read_data()

        expected_players_data = [
            {
                "date_created": "2007-07-07",
                "date_last_played": "2017-07-07",
                "bng_id": 77777777777777777,
                "destiny_id": 1010101010101,
                "bng_username": "User 1",
                "platform": "XBOX",
                "character_ids": [
                    "111111111111",
                    "222222222222",
                    "333333333333"
                ]
            },
            {
                "date_created": "2010-10-10",
                "date_last_played": "2012-12-12",
                "bng_id": 99999999999999999,
                "destiny_id": 2020202020202,
                "bng_username": "User 2",
                "platform": "STEAM",
                "character_ids": [
                    "444444444444",
                    "555555555555",
                    "666666666666"
                ]
            },
            {
                "date_created": "2011-11-11",
                "date_last_played": "2017-07-07",
                "bng_id": 88888888888888888,
                "destiny_id": 3030303030303,
                "bng_username": "User 3",
                "platform": "PSN",
                "character_ids": [
                    "777777777777",
                    "888888888888",
                    "999999999999"
                ]
            },
            {
                "date_created": "2001-01-01",
                "date_last_played": "2022-02-02",
                "bng_id": 66666666666666666,
                "destiny_id": 4040404040404,
                "bng_username": "User 4",
                "platform": "XBOX",
                "character_ids": [
                    "111111222222",
                    "222222333333",
                    "333333444444"
                ]
            }
        ]

        self.db_exec.retrieve_all.assert_called_with("`Player`")
        players = self.player_manager._DatabasePlayerManager__players
        for i in range(len(players)):
            assert players[i].data == expected_players_data[i]

    def test_db_player_manager_unsuccessful_read_data(self):
        self.db_exec.retrieve_all.return_value = []
        self.player_manager.read_data()

        self.db_exec.retrieve_all.assert_called_with("`Player`")
        assert self.player_manager._DatabasePlayerManager__players == []

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_db_player_manager_successful_add_existing_player(self, mock_urlopen):
        mock_player_data = [
            1,
            1010101010101,
            77777777777777777,
            "User 1",
            "2007-07-07",
            "2017-07-07",
            "XBOX",
            "111111111111, 222222222222, 333333333333"
        ]
        mock_api_response = {"Response": 
            {   # member response
                "bungieNetUser": {
                    "firstAccess": "2007-07-07T07:07:07Z",
                    "membershipId": "77777777777777777",
                    "uniqueName": "User 1"
                }
            }
        }
        mock_profile_response = {"Response": 
            {   # profile response
                "profile": {
                    "data": {
                        "dateLastPlayed": "2017-07-07T07:07:07Z",
                        "characterIds": [
                            "111111111111",
                            "222222222222",
                            "333333333333"
                        ]
                    }
                }
            }
        }
        mock_api_response = json.dumps(mock_api_response)
        mock_profile_response = json.dumps(mock_profile_response)

        mock_urlopen.return_value.__enter__.return_value.read.side_effect = [mock_api_response, mock_profile_response]
        self.player_manager.add_existing_player(mock_player_data)

        expected_player_data = {
            "date_created": "2007-07-07",
            "date_last_played": "2017-07-07",
            "bng_id": 77777777777777777,
            "destiny_id": 1010101010101,
            "bng_username": "User 1",
            "platform": "XBOX",
            "character_ids": [
                "111111111111",
                "222222222222",
                "333333333333"
            ]
        }

        assert self.player_manager._DatabasePlayerManager__players[0].data == expected_player_data

    @patch("backend.extract.bng_api_connector.urlopen")
    def test_db_player_manager_unsuccessful_add_existing_player(self, mock_urlopen):
        mock_player_data = [
            1,
            1010101010101,
            77777777777777777,
            "User 1",
            "2007-07-07",
            "2017-07-07",
            "XBOX",
            "111111111111, 222222222222, 333333333333"
        ]
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps({})

        self.player_manager.add_existing_player(mock_player_data)
        assert self.player_manager._DatabasePlayerManager__players[0].data == {}

    def test_db_player_manager_successful_get_character_and_player_ids(self):
        self.db_exec.select_rows.return_value = [("[1, 2, 3]", 1)]

        character_ids, player_id = self.player_manager.get_character_and_player_ids(1)

        assert player_id == 1
        assert character_ids == [1, 2, 3]

    def test_db_player_manager_unsuccessful_get_character_and_player_ids(self):
        self.db_exec.select_rows.return_value = []

        character_ids, player_id = self.player_manager.get_character_and_player_ids(1)

        assert player_id is None
        assert character_ids is None
        