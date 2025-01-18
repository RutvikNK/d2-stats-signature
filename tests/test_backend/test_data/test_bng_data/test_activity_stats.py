import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import ActivityStatsData

from backend.manifest.destiny_manifest import DestinyManifest

class ActivityStatsDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.instance_id = 1000
        self.weapon_id = 2000
        self.char_id = 3000
        self.activity_id = 4000
        self.manifest = DestinyManifest()
        self.manifest_data = MagicMock()
        self.manifest.all_data = self.manifest_data

        self.activity_stats = ActivityStatsData(self.conn, self.instance_id, self.weapon_id, self.char_id, self.activity_id, self.manifest)

        self.pgcr_path = f"https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{self.instance_id}/"

        self.mock_pgcr = {
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

        self.mock_manifest = {
            "DestinyInventoryItemDefinition": {
                2000: {
                    "displayProperties": {
                        "name": "Weapon Name"
                    }
                }
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
                        "name": "Class Name"
                    }
                }
            }
        }

    def test_mock_manifest(self):
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        assert self.manifest.all_data["DestinyInventoryItemDefinition"][self.weapon_id]["displayProperties"]["name"] == "Weapon Name"
        self.manifest.all_data.__getitem__.assert_called_with("DestinyInventoryItemDefinition")

        assert self.manifest.all_data["DestinyActivityDefinition"][3782]["displayProperties"]["name"] == "Activity Name"
        self.manifest.all_data.__getitem__.assert_called_with("DestinyActivityDefinition")

        assert self.manifest.all_data["DestinyClassDefinition"][1]["displayProperties"]["name"] == "Class Name"
        self.manifest.all_data.__getitem__.assert_called_with("DestinyClassDefinition")
    
    def test_successful_get_participating_char(self):
        character = self.activity_stats._ActivityStatsData__get_participating_character(self.mock_pgcr)
        assert character == self.mock_pgcr["entries"][3]

    def test_unsuccessful_get_participating_char(self):
        mock_pgcr = {
            "entries": [
                {
                    "characterId": "1102"
                },
                {
                    "characterId": "7780"
                },
                {
                    "characterId": "1434"
                },
                {
                    "characterId": "5529"
                }
            ]
        }
        character = self.activity_stats._ActivityStatsData__get_participating_character(mock_pgcr)
        assert character is None

    def test_successful_get_weapon(self):
        mock_pgcr = {
            "extended": {
                "weapons": [
                    {
                        "referenceId": 4341
                    },
                    {
                        "referenceId": 2000
                    }
                ]
            }
        }
        weapon = self.activity_stats._ActivityStatsData__get_weapon(mock_pgcr)
        assert weapon == mock_pgcr["extended"]["weapons"][1]

    def test_unsuccessful_get_weapon(self):
        mock_pgcr = {
            "extended": {
                "weapons": [
                    {
                        "referenceId": 4341
                    },
                    {
                        "referenceId": 7673
                    }
                ]
            }
        }
        weapon = self.activity_stats._ActivityStatsData__get_weapon(mock_pgcr)
        assert weapon is None

    def test_successful_activity_stats_define_data(self):
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        assert self.manifest.all_data["DestinyInventoryItemDefinition"][self.weapon_id]["displayProperties"]["name"] == "Weapon Name"
        self.manifest.all_data.__getitem__.assert_called_with("DestinyInventoryItemDefinition")

        self.conn.get_url_request.return_value = self.mock_pgcr

        perf_report = self.activity_stats._ActivityStatsData__get_participating_character(self.mock_pgcr)
        assert perf_report == self.mock_pgcr["entries"][3]

        weapon_data = self.activity_stats._ActivityStatsData__get_weapon(perf_report)
        assert weapon_data == perf_report["extended"]["weapons"][0]

        expected_stats_data = {
            "instance_id": 1000,
            "kills": 15.0,
            "precision_kills": 8.0,
            "precision_kills_percent": 53.33,
            "weapon_name": "Weapon Name",
            "activity_name": "Activity Name",
            "character_class": "Class Name",
        }
        expected_og_data = {
            "bng_activity_id": 4000,
            "bng_character_id": 3000,
            "bng_weapon_id": 2000
        }
        expected_participant_data = {
            "destiny_id": "3314",
            "member_type": 1
        }

        self.activity_stats.define_data()
        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)
        
        assert self.activity_stats.data == expected_stats_data
        assert self.activity_stats.og_data == expected_og_data
        assert self.activity_stats.participant == expected_participant_data
    
    def test_unsuccessful_activity_stats_define_data_no_api_response(self):
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        with self.assertRaises(KeyError):
            self.manifest.all_data["DestinyInventoryItemDefinition"][9999]["displayProperties"]["name"]
        self.manifest.all_data.__getitem__.assert_called_with("DestinyInventoryItemDefinition")

        self.activity_stats.define_data()
        self.conn.get_url_request.assert_called_once_with(self.pgcr_path)

        assert self.activity_stats.data == {}
        assert self.activity_stats.og_data == {}
        assert self.activity_stats.participant == {}

    def test_unsuccesful_activity_stats_define_data_no_perf_report(self):
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__
        
        self.mock_pgcr["entries"][3]["characterId"] = "1602"
        self.conn.get_url_request.return_value = self.mock_pgcr

        pgcr = self.activity_stats.get_data(self.pgcr_path)
        self.conn.get_url_request.assert_called_with(self.pgcr_path)
        assert pgcr == self.mock_pgcr

        character = self.activity_stats._ActivityStatsData__get_participating_character(self.mock_pgcr)
        assert character is None

        self.activity_stats.define_data()
        self.conn.get_url_request.assert_called_with(self.pgcr_path)
        
        assert self.activity_stats.data == {}
        assert self.activity_stats.og_data == {}
        assert self.activity_stats.participant == {}

    def test_unsuccessful_activity_stats_define_data_incomplete_manifest(self):
        self.mock_manifest.pop("DestinyInventoryItemDefinition")
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__
        
        self.conn.get_url_request.return_value = self.mock_pgcr

        character = self.activity_stats._ActivityStatsData__get_participating_character(self.mock_pgcr)
        assert character == self.mock_pgcr["entries"][3]

        self.activity_stats.define_data()

        assert self.activity_stats.data == {}
        assert self.activity_stats.og_data == {}
        assert self.activity_stats.participant == {}

    def test_unsuccessful_activity_stats_define_data_no_weapon_data(self):
        self.mock_pgcr["entries"][3]["extended"]["weapons"][0]["referenceId"] = 7768
        self.conn.get_url_request.return_value = self.mock_pgcr

        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        character = self.activity_stats._ActivityStatsData__get_participating_character(self.mock_pgcr)
        assert character == self.mock_pgcr["entries"][3]
        
        weapon_data = self.activity_stats._ActivityStatsData__get_weapon(character)
        assert weapon_data is None

        self.activity_stats.define_data()
        
        assert self.activity_stats.data == {}
        assert self.activity_stats.og_data == {}
        assert self.activity_stats.participant == {}

    def test_activity_stats_precision_kills_division(self):
        self.mock_pgcr["entries"][3]["extended"]["weapons"][0]["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"] = 0.0

        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__
        self.conn.get_url_request.return_value = self.mock_pgcr

        self.activity_stats.define_data()
        
        expected_precision_kills_percent = 0.0
        assert self.activity_stats.data["precision_kills_percent"] == expected_precision_kills_percent

    def test_get_weapon_none(self):
        no_weapon = self.activity_stats._ActivityStatsData__get_weapon(dict())
        assert no_weapon is None
        