import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import (
    WeaponData,
    EquippedWeaponData
)
from backend.manifest.destiny_manifest import DestinyManifest

class EquippedWeaponTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        
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
                        "ammoType": 1,
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
                },
                381: {
                    "itemTypeDisplayName": "Fusion Rifle",
                    "displayProperties": {
                        "name": "Weapon Name"
                    },
                    "equippingBlock": {
                        "ammoType": 2,
                        "equipmentSlotTypeHash": 2465295065
                    },
                    "damageTypes": [
                        7
                    ],
                    "itemTypeAndTierDisplayName": "Legendary Fusion Rifle",
                    "stats": {
                        "stats": {
                            "2961396640": {
                                "value": 750
                            }
                        }
                    }
                },
                556: {
                    "itemTypeDisplayName": "Sword",
                    "displayProperties": {
                        "name": "Weapon Name"
                    },
                    "equippingBlock": {
                        "ammoType": 3,
                        "equipmentSlotTypeHash": 953998645
                    },
                    "damageTypes": [
                        7
                    ],
                    "itemTypeAndTierDisplayName": "Exotic Sword",
                    "stats": {
                        "stats": {
                            "2837207746": {
                                "value": 275
                            }
                        }
                    }
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = self.mock_manifest.__getitem__

        self.weapon_to_equip = WeaponData(self.conn, 199, self.manifest)
        self.weapon_to_equip.define_data()

        self.equipped_weapon = EquippedWeaponData(self.conn, self.weapon_to_equip, 10101010101, self.manifest)

    def test_equipped_weapon_eq(self):
        weapon1 = MagicMock()
        mock_weapon_data_1 = {
            "bng_weapon_id": 322
        }
        weapon1.data.__getitem__.side_effect = mock_weapon_data_1.__getitem__

        ew1 = EquippedWeaponData(self.conn, weapon1, 999)
        ew2 = EquippedWeaponData(self.conn, weapon1, 999)
        
        assert ew1 == ew2

        weapon2 = MagicMock()
        mock_weapon_data_2 = {
            "bng_weapon_id": 124
        }
        weapon2.data.__getitem__.side_effect = mock_weapon_data_2.__getitem__
        ew3 = EquippedWeaponData(self.conn, weapon2, 999)
        assert ew1 != ew3

        ew4 = EquippedWeaponData(self.conn, weapon1, 231)
        assert ew1 != ew4

        ew5 = EquippedWeaponData(self.conn, weapon2, 231)
        assert ew1 != ew5

        not_ew = "not an equipped weapon"
        assert ew1 != not_ew

    def test_successful_equipped_weapon_init(self):
        expected_id = 199
        actual_id = self.equipped_weapon._EquippedWeaponData__bng_weapon_id

        assert expected_id == actual_id
        assert self.equipped_weapon._manifest_data

    def test_unsuccessful_equipped_weapon_init(self):
        bad_id = 515
        bad_weapon = WeaponData(self.conn, bad_id, self.manifest)
        bad_equipped_weapon = EquippedWeaponData(self.conn, bad_weapon, 10101010101, self.manifest)

        assert bad_equipped_weapon._EquippedWeaponData__bng_weapon_id == -1
        assert not bad_equipped_weapon._manifest_data

    def test_successful_equipped_weapon_define_rpm_data(self):
        expected_rpm_data = {
            "slot_type": "KINETIC",
            "main_stat": "500rpm"
        }
        
        self.equipped_weapon.define_data()
        assert expected_rpm_data == self.equipped_weapon.data

    def test_successful_equipped_weapon_define_charged_weapon_data(self):
        fusion_rifle = WeaponData(self.conn, 381, self.manifest)
        fusion_rifle.define_data()
        
        equipped_fr = EquippedWeaponData(self.conn, fusion_rifle, 10101010101, self.manifest)
        equipped_fr.define_data()
        
        expected_fr_data = {
            "slot_type": "ENERGY",
            "main_stat": "750ms"
        }
        
        assert expected_fr_data == equipped_fr.data

    def test_successful_equipped_weapon_define_sword_data(self):
        sword = WeaponData(self.conn, 556, self.manifest)
        sword.define_data()
        
        equipped_sword = EquippedWeaponData(self.conn, sword, 10101010101, self.manifest)
        equipped_sword.define_data()
        
        exepected_sword_data = {
            "slot_type": "POWER",
            "main_stat": "275 swing speed"
        }
        
        assert exepected_sword_data == equipped_sword.data

    def test_unsuccesful_equipped_weapon_define_data_bad_manifest_data(self):
        bad_mock_manifest = {
            "DestinyInventoryItemDefinition": {
                199: {
                    "itemTypeDisplayName": "Auto Rifle",
                    "displayProperties": {
                        "name": "Weapon Name"
                    },
                    "bad key": 100,
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
        self.manifest_data.__getitem__.side_effect = bad_mock_manifest.__getitem__

        weapon = WeaponData(self.conn, 199, self.manifest)
        weapon.define_data()

        equipped_weapon = EquippedWeaponData(self.conn, weapon, 111, self.manifest)
        equipped_weapon.define_data()

        assert equipped_weapon.data == {}