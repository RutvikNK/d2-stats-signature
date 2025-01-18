import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import CharacterData

class CharacterDataTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.character = CharacterData(self.conn, 1010101010101, 1, 111111111, 1)

        self.character_data = {
            "character": {
                "data": {
                    "classType": 1,
                    "dateLastPlayed": "2017-07-07T07:07:07Z"
                }
            }
        }

        self.equipment_data = {
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
            }
        }

        self.test_character_path = "https://example.com/api/character"
        self.test_equipment_path = "https://example.com/api/equipment"

    def test_character_eq(self):
        c1 = CharacterData(self.conn, 101, 1, 8989, 1)
        c2 = CharacterData(self.conn, 101, 1, 8989, 1)

        assert c1 == c2

        c3 = CharacterData(self.conn, 610, 1, 7413, 2)
        assert c1 != c3

        not_c = "not a character"
        assert c1 != not_c

    def test_character_get_data_called(self):
        self.conn.get_url_request.side_effect = [self.character_data, self.equipment_data]
        self.character.define_data()

        self.conn.get_url_request.side_effect = [self.equipment_data]
        assert self.character.get_all_equipped_items(self.test_equipment_path)
        self.conn.get_url_request.assert_called_with(self.test_equipment_path)

        self.conn.get_url_request.side_effect = [self.character_data, self.equipment_data]
        assert self.character.get_data(self.test_character_path)
        self.conn.get_url_request.assert_called_with(self.test_character_path)

        assert self.character.get_data(self.test_equipment_path)
        self.conn.get_url_request.assert_called_with(self.test_equipment_path)

    def test_character_get_data(self):
        self.conn.get_url_request.return_value = self.character_data

        data_response = self.character.get_data(self.test_character_path)
        assert data_response == self.character_data
    
    def test_successful_char_equipment_get(self):
        self.conn.get_url_request.return_value = self.equipment_data

        expected_data = [
            9009009009,
            8008008008,
            7007007007,
            6006006006,
            5005005005,
            4004004004,
            3003003003,
            2002002002
        ]
        actual_data = self.character.get_all_equipped_items(self.test_equipment_path)
        assert actual_data == expected_data

    def test_unsuccessful_char_equipment_get(self):
        # test empty return list
        actual_data = self.character.get_all_equipped_items(self.test_equipment_path)
        assert actual_data == []

        # test partial return list due to KeyError
        bad_equipment_data = {
            "equipment": {
                "data": {
                    "items": [
                        {"itemHash": 9009009009},
                        {"itemhash": 8008008008},  # bad key, should raise an error and stop the population of the list
                        {"itemHash": 7007007007},
                        {"itemHash": 6006006006},
                        {"itemHash": 5005005005},
                        {"itemHash": 4004004004},
                        {"itemHash": 3003003003},
                        {"itemHash": 2002002002}
                    ]
                }
            }
        }
        self.conn.get_url_request.return_value = bad_equipment_data
        actual_data = self.character.get_all_equipped_items(self.test_equipment_path)
        assert actual_data == [9009009009]

        self.conn.get_url_request.side_effect = [self.character_data, bad_equipment_data]
        self.character.define_data()
        
        expected_char_data = {
            "bng_character_id": 111111111,
            "player_id": 1,
            "class": "HUNTER",
            "date_last_played": "2017-07-07",
        }
        assert self.character.data == expected_char_data
        assert self.character.equipment == {"weapons": [], "armor": []}

    def test_successful_char_def_data(self):
        self.conn.get_url_request.side_effect = [self.character_data, self.equipment_data]

        self.character.define_data()
        assert self.conn.get_url_request.called_twice_with([self.test_character_path, self.test_equipment_path])
        
        expected_char_data = {
            "bng_character_id": 111111111,
            "player_id": 1,
            "class": "HUNTER",
            "date_last_played": "2017-07-07",
        }

        expected_equip_data = {
            "weapons": [9009009009, 8008008008, 7007007007],
            "armor": [6006006006, 5005005005, 4004004004, 3003003003, 2002002002]
        }

        assert self.character.data == expected_char_data
        assert self.character.equipment == expected_equip_data

    def test_unsuccessful_char_def_data_no_response(self):
        self.conn.get_url_request.return_value = None

        self.character.define_data()
        assert self.conn.get_url_request.called_twice_with([self.test_character_path, self.test_equipment_path])

        assert self.character.data == {}
        assert self.character.equipment == {}

    def test_unsuccessful_char_def_data_bad_response(self):
        self.conn.get_url_request.return_value = {
            "bad key": 100
        }

        self.character.define_data()
        assert self.conn.get_url_request.called_twice_with([self.test_character_path, self.test_equipment_path])

        assert self.character.data == {}
        assert self.character.equipment == {}

    def test_get_activity_inst_hist_single(self):
        mock_activity_inst_hist_data = {
            "activities": [
                {
                    "activityDetails": {
                        "instanceId": "101010101"
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_activity_inst_hist_data

        test_activity_inst_path = "https://example.com/api/activity-instance-history"
        instance_ids = self.character.get_activity_hist_instances(1, 1, test_activity_inst_path)
        expected_ids = [101010101]

        assert instance_ids == expected_ids

    def test_get_activity_inst_hist(self):
        mock_activity_inst_hist_data = {
            "activities": [
                {
                    "activityDetails": {
                        "instanceId": "101010101"
                    }
                },
                {
                    "activityDetails": {
                        "instanceId": "202020202"
                    }
                },
                {
                    "activityDetails": {
                        "instanceId": "303030303"
                    }
                },
                {
                    "activityDetails": {
                        "instanceId": "404040404"
                    }
                },
                {
                    "activityDetails": {
                        "instanceId": "505050505"
                    }
                }
            ]
        }

        self.conn.get_url_request.return_value = mock_activity_inst_hist_data

        test_activity_inst_path = "https://example.com/api/activity-instance-history"
        instance_ids = self.character.get_activity_hist_instances(1, 1, test_activity_inst_path)
        expected_ids = [101010101, 202020202, 303030303, 404040404, 505050505]

        assert instance_ids == expected_ids

    def test_unsuccessful_get_activity_inst_hist(self):
        self.conn.get_url_request.return_value = None

        test_activity_inst_path = "https://example.com/api/activity-instance-history"
        instance_ids = self.character.get_activity_hist_instances(1, 1, test_activity_inst_path)

        assert instance_ids == []
