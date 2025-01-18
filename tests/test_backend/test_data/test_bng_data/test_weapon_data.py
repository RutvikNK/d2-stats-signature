import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import WeaponData
from backend.manifest.destiny_manifest import DestinyManifest

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

    def test_weapon_eq(self):
        w1 = WeaponData(self.conn, 199)
        w2 = WeaponData(self.conn, 199)

        assert w1 == w2

        w3 = WeaponData(self.conn, 909)
        assert w1 != w3

        not_w = "not a weapon"
        assert w1 != not_w

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

    def test_unsuccessful_weapon_def_data_no_manifest_entry(self):
        weapon = WeaponData(self.conn, self.bad_weapon_id, self.manifest)
        weapon.define_data()

        assert weapon.data == {}

    def test_unsuccessful_weapon_def_data_bad_manifest_entry(self):
        bad_mock_manifest = {
            "DestinyInventoryItemDefinition": {
                199: {
                    "bad key": 100
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = bad_mock_manifest.__getitem__

        weapon = WeaponData(self.conn, self.good_weapon_id, self.manifest)
        weapon.define_data()

        assert weapon.data == {}