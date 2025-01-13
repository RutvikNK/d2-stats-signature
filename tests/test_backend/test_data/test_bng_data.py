import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import (
    PlayerData,
    CharacterData,
    WeaponData,
    EquippedWeaponData,
    ArmorData,
    EquippedArmorData,
    ActivityData,
    ActivityInstanceData,
    ActivityStatsData
)
from backend.manifest.destiny_manifest import DestinyManifest

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

    def test_unsuccessful_char_def_data(self):
        self.conn.get_url_request.return_value = None

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

class WeaponDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()

        self.manifest_data = MagicMock()
        self.manifest = DestinyManifest()
        self.manifest.all_data = self.manifest_data

        self.mock_manifest = {
            "DestinyInventoryItemDefinition": {
                199: {
                    "itemTypeDisplayName": "Auto Rifle",
                    "displayProperties": {
                        "name": "Weapon Name"
                    },
                    "equippingBlock": {
                        "ammoType": 2,
                        "equipmentSlotTypeHash": 1498876634
                    },
                    "damageTypes": [
                        7
                    ],
                    "itemTypeAndTierDisplayName": "Legendary Auto Rifle"
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        self.good_weapon_id = 199
        self.bad_weapon_id = 801

    def test_successful_weapon_manifest_init(self):
        weapon = WeaponData(self.conn, self.good_weapon_id, self.manifest)
        assert weapon._manifest_data
    
    def test_unsuccessful_weapon_manifest_init(self):
        weapon = WeaponData(self.conn, self.bad_weapon_id, self.manifest)
        assert not weapon._manifest_data
    
    def test_successful_weapon_def_data(self):
        weapon = WeaponData(self.conn, self.good_weapon_id, self.manifest)
        weapon.define_data()

        expected_weapon_data = {
            "bng_weapon_id": 199,
            "weapon_type": "AUTO_RIFLE",
            "weapon_name": "Weapon Name",
            "ammo_type": "SPECIAL",
            "slot": "KINETIC",
            "damage_type": "STRAND",
            "rarity": "LEGENDARY"
        }
        assert weapon.data == expected_weapon_data

    def test_unsuccessful_weapon_def_data(self):
        weapon = WeaponData(self.conn, self.bad_weapon_id, self.manifest)
        weapon.define_data()

        assert weapon.data == {}

class ArmorDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        
        self.manifest_data = MagicMock()
        self.manifest = DestinyManifest()
        self.manifest.all_data = self.manifest_data

        self.mock_manifest = {
            "DestinyInventoryItemDefinition": {
                883: {
                    "displayProperties": {
                        "name": "Helmet Name"
                    },
                    "equippingBlock": {
                        "equipmentSlotTypeHash": 3448274439
                    },
                    "itemTypeAndTierDisplayName": "Exotic Helmet"
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        self.good_armor_id = 883
        self.bad_armor_id = 144
    
    def test_successful_armor_manifest_init(self):
        armor = ArmorData(self.conn, self.good_armor_id, self.manifest)
        assert armor._manifest_data
    
    def test_unsuccessful_armor_manifest_init(self):
        armor = ArmorData(self.conn, self.bad_armor_id, self.manifest)
        assert not armor._manifest_data
    
    def test_successful_armor_def_data(self):
        armor = ArmorData(self.conn, self.good_armor_id, self.manifest)
        armor.define_data()

        expected_armor_data = {
            "bng_armor_id": 883,
            "armor_name": "Helmet Name",
            "slot": "HELMET",
            "rarity": "EXOTIC"
        }
        assert armor.data == expected_armor_data

    def test_unsuccessful_armor_def_data(self):
        armor = ArmorData(self.conn, self.bad_armor_id, self.manifest)
        armor.define_data()

        assert armor.data == {}

class EquippedWeaponTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.weapon_to_equip = WeaponData(self.conn, 1363886209)
        self.weapon_to_equip.define_data()

        self.equipped_weapon = EquippedWeaponData(self.conn, self.weapon_to_equip, 10101010101)

    def test_successful_equipped_weapon_init(self):
        expected_id = 1363886209
        actual_id = self.equipped_weapon._EquippedWeaponData__bng_weapon_id

        assert expected_id == actual_id
        assert self.equipped_weapon._manifest_data

    def test_unsuccessful_equipped_weapon_init(self):
        bad_id = 1234567890
        bad_weapon = WeaponData(self.conn, bad_id)
        bad_equipped_weapon = EquippedWeaponData(self.conn, bad_weapon, 10101010101)

        assert bad_equipped_weapon._EquippedWeaponData__bng_weapon_id == -1
        assert not bad_equipped_weapon._manifest_data

    def test_successful_equipped_weapon_define_rpm_data(self):
        expected_rpm_data = {
            "slot_type": "POWER",
            "main_stat": "15rpm"
        }
        
        self.equipped_weapon.define_data()
        assert expected_rpm_data == self.equipped_weapon.data

    def test_successful_equipped_weapon_define_charged_weapon_data(self):
        fusion_rifle = WeaponData(self.conn, 2715240478)
        fusion_rifle.define_data()
        
        equipped_fr = EquippedWeaponData(self.conn, fusion_rifle, 10101010101)
        equipped_fr.define_data()
        
        expected_fr_data = {
            "slot_type": "KINETIC",
            "main_stat": "500ms"
        }
        
        assert expected_fr_data == equipped_fr.data

    def test_successful_equipped_weapon_define_sword_data(self):
        sword = WeaponData(self.conn, 243425374)
        sword.define_data()
        
        squipped_sword = EquippedWeaponData(self.conn, sword, 10101010101)
        squipped_sword.define_data()
        
        exepected_sword_data = {
            "slot_type": "POWER",
            "main_stat": "40 swing speed"
        }
        
        assert exepected_sword_data == squipped_sword.data

class EquippedArmorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.armor_to_equip = ArmorData(self.conn, 1362342075)
        self.armor_to_equip.define_data()

        self.equipped_armor = EquippedArmorData(self.conn, self.armor_to_equip, 10101010101)

    def test_successful_equipped_armor_init(self):
        expected_id = 1362342075
        actual_id = self.equipped_armor._EquippedArmorData__bng_armor_id

        assert expected_id == actual_id
        assert self.equipped_armor._manifest_data

    def test_unsuccessful_equipped_armor_init(self):
        bad_id = 1234567890
        bad_armor = ArmorData(self.conn, bad_id)
        bad_equipped_armor = EquippedArmorData(self.conn, bad_armor, 10101010101)

        assert bad_equipped_armor._EquippedArmorData__bng_armor_id == -1
        assert not bad_equipped_armor._manifest_data

    def test_successful_equipped_armor_define_data(self):
        self.equipped_armor.define_data()

        assert self.equipped_armor.data == {"slot_type": "HELMET"}

class ActivityDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.rumble_id = 2259621230
        self.rumble_activity = ActivityData(self.conn, self.rumble_id)
    
    def test_successful_activity_data_init(self):
        assert self.rumble_activity._manifest_data
    
    def test_unsuccessful_activity_data_init(self):
        bad_id = 123456789
        bad_activity = ActivityData(self.conn, bad_id)

        assert not bad_activity._manifest_data

    def test_successful_activity_data_def(self):
        self.rumble_activity.define_data()
        expected_activity_data = {
            "bng_activity_id": 2259621230,
            "activity_name": "Rumble",
            "max_fireteam_size": 6,
            "type": "The Crucible",
            "modifiers": "Rumble Rules, Notswap, Increased Crucible Rank, Double Crucible Drops, Matchmaking, Longer Respawns"
        }

        assert self.rumble_activity.data == expected_activity_data
        
        modifiers = self.rumble_activity.data["modifiers"]
        assert not modifiers.endswith(", ")
    
    def test_unsuccessful_activity_data_def(self):
        bad_id = 123456789
        bad_activity = ActivityData(self.conn, bad_id)
        bad_activity.define_data()

        assert bad_activity.data == {}
    
    def test_overflowing_activity_data_modifiers(self):
        gm_id = 967120713
        gm_activity = ActivityData(self.conn, gm_id)
        gm_activity.define_data()

        expected_gm_data = {
            "bng_activity_id": 967120713,
            "activity_name": "Nightfall Grandmaster: Birthplace of the Vile",
            "max_fireteam_size": 3,
            "type": "Nightfall",
            "modifiers": "Shielded Foes, Shielded Foes, Overcharged Weapons, Champion Foes, Champion Foes, Void Threat, Overch..."
        }

        assert gm_activity.data == expected_gm_data

        modifiers = gm_activity.data["modifiers"] 
        assert modifiers.endswith("...")

class ActivityInstanceDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.mock_instance_id = 123456789
        self.pgcr_path = f"https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{self.mock_instance_id}/"

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
