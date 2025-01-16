import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import PlayerData

class PlayerDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.member_response_data = {
                "bungieNetUser": {
                    "firstAccess": "2007-07-07T07:07:07Z",
                    "membershipId": "77777777777777777",
                    "uniqueName": "Bungie Net User"
                }
            }
        
        self.profile_response_data = {
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

        self.conn = MagicMock()
        self.player = PlayerData(self.conn, 1010101010101, 1)
        self.test_member_path = "https://example.com/api/member"
        self.test_profile_path = "https://example.com/api/profile"
    
    def test_player_eq(self):
        p1 = PlayerData(self.conn, 101, 2)
        p2 = PlayerData(self.conn, 101, 1)

        assert p1 == p2

        p3 = PlayerData(self.conn, 201, 1)
        assert p1 != p3

        not_p = "not a player"
        assert p1 != not_p

    def test_player_get_data_called(self):
        self.player.define_data()

        assert self.player.get_data(self.test_member_path)
        self.conn.get_url_request.assert_called_with(self.test_member_path)

    def test_player_get_data(self):
        self.conn.get_url_request.return_value = self.member_response_data

        data_response = self.player.get_data(self.test_member_path)
        assert data_response == self.member_response_data

    def test_successful_player_data_definition(self):
        self.conn.get_url_request.side_effect = [self.member_response_data, self.profile_response_data]

        self.player.define_data()

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

        assert self.player.data == expected_player_data

    def test_unsuccessful_player_data_definition(self):
        bad_member_response_data = {
                "bungieNetUser": {
                    "firstAccess": "2007-07-07T07:07:07Z",
                    "memberID": "77777777777777777",  # bad key, should raise a KeyError
                    "uniqueName": "Bungie Net User"
                }
            }
        
        bad_profile_response_data = {
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
        
        self.conn.get_url_request.side_effect = [bad_member_response_data, bad_profile_response_data]
        self.player.define_data()

        assert self.player.data == {}
