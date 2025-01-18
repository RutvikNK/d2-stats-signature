import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import (
    WeaponData,
    ArmorData,
    DataFactory
)
from backend.manifest.destiny_manifest import DestinyManifest

class DataFactoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        self.factory = DataFactory()
        self.factory.bng_conn = self.conn

        self.manifest_data = MagicMock()
        self.manifest = DestinyManifest()
        self.manifest.all_data = self.manifest_data

    def test_factory_connection(self):
        assert self.factory.bng_conn == self.conn
    
    def test_player_factory(self):
        member_response_data = {
                "bungieNetUser": {
                    "firstAccess": "2007-07-07T07:07:07Z",
                    "membershipId": "77777777777777777",
                    "uniqueName": "Bungie Net User"
                }
            }
        
        profile_response_data = {
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
        self.conn.get_url_request.side_effect = [member_response_data, profile_response_data]

        member_id = 1412
        member_type = 1
        player = self.factory.get_player(member_id, member_type, self.conn)

        expected_player_data = {
            "date_created": "2007-07-07",
            "date_last_played": "2017-07-07",
            "bng_id": 77777777777777777,
            "destiny_id": 1412,
            "bng_username": "Bungie Net User",
            "platform": "XBOX",
            "character_ids": [
                "111111111111",
                "222222222222",
                "333333333333"
            ]
        }

        assert player.data == expected_player_data
        assert player._id == 1412
        assert player._type == 1

    def test_character_factory(self):
        character_data = {
            "character": {
                "data": {
                    "classType": 1,
                    "dateLastPlayed": "2017-07-07T07:07:07Z"
                }
            }
        }

        equipment_data = {
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
        self.conn.get_url_request.side_effect = [character_data, equipment_data]

        member_id = 1412
        member_type = 1
        char_id = 22314
        player_id = 1
        character = self.factory.get_character(member_id, member_type, char_id, player_id, self.conn)
        
        expected_char_data = {
            "bng_character_id": 22314,
            "player_id": 1,
            "class": "HUNTER",
            "date_last_played": "2017-07-07",
        }

        expected_equip_data = {
            "weapons": [9009009009, 8008008008, 7007007007],
            "armor": [6006006006, 5005005005, 4004004004, 3003003003, 2002002002]
        }

        assert character.data == expected_char_data
        assert character.equipment == expected_equip_data

    def test_weapon_factory(self):
        mock_manifest = {
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
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__

        weapon = self.factory.get_weapon(199, self.conn, self.manifest)
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

    def test_armor_factory(self):
        mock_manifest = {
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
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__

        armor_id = 883
        armor = self.factory.get_armor(armor_id, self.conn, self.manifest)
        expected_armor_data = {
            "bng_armor_id": 883,
            "armor_name": "Helmet Name",
            "slot": "HELMET",
            "rarity": "EXOTIC"
        }
        assert armor.data == expected_armor_data

    def test_weapon_equipment_factory(self):
        mock_manifest = {
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
                    "itemTypeAndTierDisplayName": "Legendary Auto Rifle",
                    "stats": {
                        "stats": {
                            "4284893193": {
                                "value": 500
                            }
                        }
                    }
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__
        
        weapon = WeaponData(self.conn, 199, self.manifest)
        weapon.define_data()

        equipped_weapon = self.factory.get_equipped_weapon(weapon, 22314, self.conn, self.manifest)
        equipped_weapon.define_data()

        expected_equipment_data = {
            "slot_type": "KINETIC",
            "main_stat": "500rpm"
        }
        assert equipped_weapon.data == expected_equipment_data

    def test_armor_equipment_factory(self):
        mock_manifest = {
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
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__
        armor = ArmorData(self.conn, 883, self.manifest)
        armor.define_data()

        equipped_armor = self.factory.get_equipped_armor(armor, 22314, self.conn, self.manifest)
        equipped_armor.define_data()

        expected_equipement_data = {
            "slot_type": "HELMET"
        }
        assert equipped_armor.data == expected_equipement_data
    
    def test_activity_factory(self):
        mock_manifest = {
            "DestinyActivityTypeDefinition": {
                909: {
                    "displayProperties": {
                        "name": "Activity Type"
                    }
                }
            },
            "DestinyActivityModifierDefinition": {
                1: {
                        "displayProperties": {
                            "name": "Modifier 1"
                        }
                    },
                2: {
                        "displayProperties": {
                            "name": "Modifier 2"
                        }
                    },
                3: {
                        "displayProperties": {
                            "name": "Modifier 3"
                        }
                    },
                4: {
                        "displayProperties": {
                            "name": "Modifier 4"
                        }
                    },
                5: {
                        "displayProperties": {
                            "name": "Modifier 5"
                        }
                    }
            },
            "DestinyActivityDefinition": {
                771494: {
                    "displayProperties": {
                        "name": "Activity Name"
                    },
                    "matchmaking": {
                        "maxPlayers": 3
                    },
                    "activityTypeHash": 909,
                    "modifiers": [
                        {
                            "activityModifierHash": 1
                        },
                        {
                            "activityModifierHash": 2
                        },
                        {
                            "activityModifierHash": 3
                        },
                        {
                            "activityModifierHash": 4
                        },
                        {
                            "activityModifierHash": 5
                        },
                    ],
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__
        activity = self.factory.get_activity(771494, self.conn, self.manifest)

        expected_activity_data = {
            "bng_activity_id": 771494,
            "activity_name": "Activity Name",
            "max_fireteam_size": 3,
            "type": "Activity Type",
            "modifiers": "Modifier 1, Modifier 2, Modifier 3, Modifier 4, Modifier 5"
        }
        assert activity.data == expected_activity_data

    def test_activity_instance_factory(self):
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

        activity_instance = self.factory.get_activity_instance(123456789, self.conn)

        expected_instance_data = {
            10101010101: [111222333, 222333444],
            20202020202: [555666777, 777888999],
            30303030303: [111222333],
            40404040404: [555666777, 333444555, 222333444]
        }
        assert activity_instance.participants_data == expected_instance_data
