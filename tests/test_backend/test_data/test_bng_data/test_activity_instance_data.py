import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import ActivityInstanceData

from backend.manifest.destiny_manifest import DestinyManifest

class ActivityInstanceDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.mock_instance_id = 123456789
        self.pgcr_path = f"https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{self.mock_instance_id}/"

    def test_activity_instance_data_eq(self):
        aid1 = ActivityInstanceData(self.conn, 775)
        aid2 = ActivityInstanceData(self.conn, 775)

        assert aid1 == aid2

        aid3 = ActivityInstanceData(self.conn, 160)
        assert aid1 != aid3

        not_aid = "not activity instance data"
        assert aid1 != not_aid

    def test_successful_post_game_carnage_report(self):
        mock_pgcr_response = {
            "period": "2007-07-07T07:07:07Z",
            "startingPhaseIndex": 0,
            "activityWasStartedFromBeginning": False,
            "activityDetails": {},
            "entries": [],
            "teams": []
        }
        self.conn.get_url_request.return_value = mock_pgcr_response
        
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)
        
        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == mock_pgcr_response

    def test_unsuccessful_post_game_carnage_report(self):
        mock_pgcr_response = {}
        self.conn.get_url_request.return_value = mock_pgcr_response
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)
        
        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == {}

    def test_successful_activity_instance_define_data_multiple(self):
        mock_pgcr_response = {
            "activityDetails": {
                "directorActivityHash": 1029384756
            },
            "entries": [
                {
                    "characterId": "10101010101",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 111222333
                            },
                            {
                                "referenceId": 222333444
                            }
                        ]
                    }
                },
                {
                    "characterId": "20202020202",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 555666777
                            },
                            {
                                "referenceId": 777888999
                            }
                        ]
                    }
                },
                {
                    "characterId": "30303030303",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 111222333
                            }
                        ]
                    }
                },
                {
                    "characterId": "40404040404",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 555666777
                            },
                            {
                                "referenceId": 333444555
                            },
                            {
                                "referenceId": 222333444
                            }
                        ]
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr_response

        
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)

        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == mock_pgcr_response
        
        activity_instance.define_data()
        assert activity_instance._ActivityInstanceData__activity_id == 1029384756

        expected_instance_data = {
            10101010101: [111222333, 222333444],
            20202020202: [555666777, 777888999],
            30303030303: [111222333],
            40404040404: [555666777, 333444555, 222333444]
        }
        assert activity_instance.participants_data == expected_instance_data
    
    def test_successful_activity_instance_define_data_single(self):
        mock_pgcr_response = {
            "activityDetails": {
                "directorActivityHash": 1029384756
            },
            "entries": [
                {
                    "characterId": "10101010101",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 111222333
                            },
                            {
                                "referenceId": 222333444
                            }
                        ]
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr_response

        
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)

        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == mock_pgcr_response
        
        activity_instance.define_data()
        assert activity_instance._ActivityInstanceData__activity_id == 1029384756

        expected_instance_data = {
            10101010101: [111222333, 222333444]
        }
        assert activity_instance.participants_data == expected_instance_data

    def test_activity_instance_define_data_without_weapons(self):
        mock_pgcr_response = {
            "activityDetails": {
                "directorActivityHash": 1029384756
            },
            "entries": [
                {
                    "characterId": "10101010101",
                    "extended": {}
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr_response

        
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)

        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == mock_pgcr_response
        
        activity_instance.define_data()
        assert activity_instance._ActivityInstanceData__activity_id == 1029384756

        assert activity_instance.participants_data == {}
    
    def test_activity_instance_define_data_bad_character_id(self):
        mock_pgcr_response = {
            "activityDetails": {
                "directorActivityHash": 1029384756
            },
            "entries": [
                {
                    "characterId": "badId", # bad ID, should raise an error that skips this entry
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 111222333
                            },
                            {
                                "referenceId": 222333444
                            }
                        ]
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr_response

        
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)

        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == mock_pgcr_response
        
        activity_instance.define_data()
        assert activity_instance._ActivityInstanceData__activity_id == 1029384756

        assert activity_instance.participants_data == {}

    def test_activity_instance_define_data_bad_character_id_with_partial_data(self):
        mock_pgcr_response = {
            "activityDetails": {
                "directorActivityHash": 1029384756
            },
            "entries": [
                {
                    "characterId": "badId", # bad ID, should raise an error that skips this entry
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 111222333
                            }
                        ]
                    }
                },
                {
                    "characterId": "202020202",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 777888999
                            },
                            {
                                "referenceId": 444555666
                            }
                        ]
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr_response

        
        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)

        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        assert activity_instance._pgcr == mock_pgcr_response
        
        activity_instance.define_data()
        
        expected_instance_data = {
            202020202: [777888999, 444555666]
        }
        assert activity_instance._ActivityInstanceData__activity_id == 1029384756
        assert activity_instance.participants_data == expected_instance_data

    def test_successful_activity_instance_create_stats_multiple(self):
        manifest_data = MagicMock()
        manifest = DestinyManifest()
        manifest.all_data = manifest_data

        mock_manifest = {
            "DestinyInventoryItemDefinition": {
                5114: {
                    "displayProperties": {
                        "name": "Riptide"
                    }
                },
                1234: {
                    "displayProperties": {
                        "name": "Succession"
                    }
                },
                8807: {
                    "displayProperties": {
                        "name": "Fatebringer"
                    }
                },
                2000: {
                    "displayProperties": {
                        "name": "Tlaloc"
                    }
                },
                6900: {
                    "displayProperties": {
                        "name": "Oxygen SR3"
                    }
                },
                4769: {
                    "displayProperties": {
                        "name": "High Albedo"
                    }
                },
                3232: {
                    "displayProperties": {
                        "name": "Hezen Vengeance"
                    }
                },
                1666: {
                    "displayProperties": {
                        "name": "The Recluse"
                    }
                },
            },
            "DestinyActivityDefinition": {
                3782: {
                    "displayProperties": {
                        "name": "Activity Name"
                    }
                }
            },
            "DestinyClassDefinition": {
                1: {
                    "displayProperties": {
                        "name": "Hunter"
                    }
                },
                2: {
                    "displayProperties": {
                        "name": "Titan"
                    }
                },
                3: {
                    "displayProperties": {
                        "name": "Warlock"
                    }
                },
            }
        }
        manifest_data.__getitem__.side_effect = mock_manifest.__getitem__

        mock_pgcr = {
            "activityDetails": {
                "directorActivityHash": 3782,
            },
            "entries": [
                {
                    "player": {
                        "destinyUserInfo": {
                            "membershipType": 1,
                            "membershipId": "8908",
                        },
                        "classHash": 1
                    },
                    "characterId": "1102",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 1666,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 10.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 3.0,
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "player": {
                        "destinyUserInfo": {
                            "membershipType": 3,
                            "membershipId": "1444",
                        },
                        "classHash": 3
                    },
                    "characterId": "7780",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 3232,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 1.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 0.0,
                                        }
                                    }
                                }
                            },
                            {
                                "referenceId": 6900,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 4.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 2.0,
                                        }
                                    }
                                }
                            },
                        ]
                    }
                },
                {
                    "player": {
                        "destinyUserInfo": {
                            "membershipType": 2,
                            "membershipId": "5552",
                        },
                        "classHash": 2
                    },
                    "characterId": "1434",
                     "extended": {
                        "weapons": [
                            {
                                "referenceId": 1234,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 9.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 5.0,
                                        }
                                    }
                                }
                            },
                            {
                                "referenceId": 4769,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 1.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 0.0,
                                        }
                                    }
                                }
                            },
                        ]
                    }
                },               
                {
                    "player": {
                        "destinyUserInfo": {
                            "membershipType": 1,
                            "membershipId": "3314",
                        },
                        "classHash": 1
                    },
                    "characterId": "3000",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 2000,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 15.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 8.0,
                                        }
                                    }
                                }
                            },
                            {
                                "referenceId": 8807,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 3.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 2.0,
                                        }
                                    }
                                }
                            },
                            {
                                "referenceId": 5114,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 1.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 0.0,
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr

        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)
        activity_instance.define_data()
        expected_instance_data = {
            1102: [1666],
            7780: [3232, 6900],
            1434: [1234, 4769],
            3000: [2000, 8807, 5114]
        }
        assert activity_instance.participants_data == expected_instance_data

        activity_instance.create_stats(manifest)
        all_instance_stats = activity_instance.get_instance_stats()

        expected_stats_data = [
            {
                "instance_id": 123456789,
                "kills": 10.0,
                "precision_kills": 3.0,
                "precision_kills_percent": 30.00,
                "weapon_name": "The Recluse",
                "activity_name": "Activity Name",
                "character_class": "Hunter",
            },
            {
                "instance_id": 123456789,
                "kills": 1.0,
                "precision_kills": 0.0,
                "precision_kills_percent": 0.00,
                "weapon_name": "Hezen Vengeance",
                "activity_name": "Activity Name",
                "character_class": "Warlock",
            },
            {
                "instance_id": 123456789,
                "kills": 4.0,
                "precision_kills": 2.0,
                "precision_kills_percent": 50.00,
                "weapon_name": "Oxygen SR3",
                "activity_name": "Activity Name",
                "character_class": "Warlock",
            },
            {
                "instance_id": 123456789,
                "kills": 9.0,
                "precision_kills": 5.0,
                "precision_kills_percent": 55.56,
                "weapon_name": "Succession",
                "activity_name": "Activity Name",
                "character_class": "Titan",
            },
            {
                "instance_id": 123456789,
                "kills": 1.0,
                "precision_kills": 0.0,
                "precision_kills_percent": 0.00,
                "weapon_name": "High Albedo",
                "activity_name": "Activity Name",
                "character_class": "Titan",
            },
            {
                "instance_id": 123456789,
                "kills": 15.0,
                "precision_kills": 8.0,
                "precision_kills_percent": 53.33,
                "weapon_name": "Tlaloc",
                "activity_name": "Activity Name",
                "character_class": "Hunter",
            },
            {
                "instance_id": 123456789,
                "kills": 3.0,
                "precision_kills": 2.0,
                "precision_kills_percent": 66.67,
                "weapon_name": "Fatebringer",
                "activity_name": "Activity Name",
                "character_class": "Hunter",
            },
            {
                "instance_id": 123456789,
                "kills": 1.0,
                "precision_kills": 0.0,
                "precision_kills_percent": 0.00,
                "weapon_name": "Riptide",
                "activity_name": "Activity Name",
                "character_class": "Hunter",
            }
        ]

        expected_og_data = [
            {
                "bng_activity_id": 3782,
                "bng_character_id": 1102,
                "bng_weapon_id": 1666
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 7780,
                "bng_weapon_id": 3232
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 7780,
                "bng_weapon_id": 6900
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 1434,
                "bng_weapon_id": 1234
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 1434,
                "bng_weapon_id": 4769
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 3000,
                "bng_weapon_id": 2000
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 3000,
                "bng_weapon_id": 8807
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 3000,
                "bng_weapon_id": 5114
            },
        ]

        expected_participant_data = [
            {
                "destiny_id": "8908",
                "member_type": 1
            },
            {
                "destiny_id": "1444",
                "member_type": 3
            },
            {
                "destiny_id": "1444",
                "member_type": 3
            },
            {
                "destiny_id": "5552",
                "member_type": 2
            },
            {
                "destiny_id": "5552",
                "member_type": 2
            },
            {
            "destiny_id": "3314",
            "member_type": 1
            },
            {
            "destiny_id": "3314",
            "member_type": 1
            },
            {
            "destiny_id": "3314",
            "member_type": 1
            }
        ]
        
        assert len(all_instance_stats) == 8
        for i in range(len(all_instance_stats)):
            assert all_instance_stats[i].data == expected_stats_data[i]
            assert all_instance_stats[i].og_data == expected_og_data[i]
            assert all_instance_stats[i].participant == expected_participant_data[i]

    def test_successful_activity_instance_create_stats_single(self):
        manifest_data = MagicMock()
        manifest = DestinyManifest()
        manifest.all_data = manifest_data

        mock_manifest = {
            "DestinyInventoryItemDefinition": {
                1234: {
                    "displayProperties": {
                        "name": "Succession"
                    }
                },
                1666: {
                    "displayProperties": {
                        "name": "The Recluse"
                    }
                },
            },
            "DestinyActivityDefinition": {
                3782: {
                    "displayProperties": {
                        "name": "Activity Name"
                    }
                }
            },
            "DestinyClassDefinition": {
                1: {
                    "displayProperties": {
                        "name": "Hunter"
                    }
                }
            }
        }
        manifest_data.__getitem__.side_effect = mock_manifest.__getitem__

        mock_pgcr = {
            "activityDetails": {
                "directorActivityHash": 3782,
            },
            "entries": [
                {
                    "player": {
                        "destinyUserInfo": {
                            "membershipType": 1,
                            "membershipId": "8908",
                        },
                        "classHash": 1
                    },
                    "characterId": "1102",
                    "extended": {
                        "weapons": [
                            {
                                "referenceId": 1666,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 10.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 3.0,
                                        }
                                    }
                                }
                            },
                            {
                                "referenceId": 1234,
                                "values": {
                                    "uniqueWeaponKills": {
                                        "basic": {
                                            "value": 5.0
                                        }
                                    },
                                    "uniqueWeaponPrecisionKills": {
                                        "basic": {
                                            "value": 4.0,
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        self.conn.get_url_request.return_value = mock_pgcr

        activity_instance = ActivityInstanceData(self.conn, self.mock_instance_id)
        activity_instance.define_data()
        expected_instance_data = {
            1102: [1666, 1234]
        }
        assert activity_instance.participants_data == expected_instance_data

        activity_instance.create_stats(manifest)
        all_instance_stats = activity_instance.get_instance_stats()

        expected_stats_data = [
            {
                "instance_id": 123456789,
                "kills": 10.0,
                "precision_kills": 3.0,
                "precision_kills_percent": 30.00,
                "weapon_name": "The Recluse",
                "activity_name": "Activity Name",
                "character_class": "Hunter",
            },
            {
                "instance_id": 123456789,
                "kills": 5.0,
                "precision_kills": 4.0,
                "precision_kills_percent": 80.00,
                "weapon_name": "Succession",
                "activity_name": "Activity Name",
                "character_class": "Hunter",
            }
        ]

        expected_og_data = [
            {
                "bng_activity_id": 3782,
                "bng_character_id": 1102,
                "bng_weapon_id": 1666
            },
            {
                "bng_activity_id": 3782,
                "bng_character_id": 1102,
                "bng_weapon_id": 1234
            }
        ]

        expected_participant_data = [
            {
                "destiny_id": "8908",
                "member_type": 1
            },
            {
                "destiny_id": "8908",
                "member_type": 1
            }
        ]
        
        assert len(all_instance_stats) == 2
        for i in range(len(all_instance_stats)):
            assert all_instance_stats[i].data == expected_stats_data[i]
            assert all_instance_stats[i].og_data == expected_og_data[i]
            assert all_instance_stats[i].participant == expected_participant_data[i]
