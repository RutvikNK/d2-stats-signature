import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import (
    ArmorData,
    EquippedArmorData
)
from backend.manifest.destiny_manifest import DestinyManifest

class EquippedArmorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()

        self.manifest_data = MagicMock()
        self.manifest = DestinyManifest()
        self.manifest.all_data = self.manifest_data

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


        self.armor_to_equip = ArmorData(self.conn, 883, self.manifest)
        self.armor_to_equip.define_data()

        self.equipped_armor = EquippedArmorData(self.conn, self.armor_to_equip, 10101010101, self.manifest)

    def test_equipped_armor_eq(self):
        armor1 = MagicMock()
        mock_armor_data_1 = {
            "bng_armor_id": 481
        }
        armor1.data.__getitem__.side_effect = mock_armor_data_1.__getitem__

        ea1 = EquippedArmorData(self.conn, armor1, 999)
        ea2 = EquippedArmorData(self.conn, armor1, 999)
        assert ea1 == ea2

        armor2 = MagicMock()
        mock_armor_data_2 = {
            "bng_armor_id": 198
        }
        armor2.data.__getitem__.side_effect = mock_armor_data_2.__getitem__

        ea3 = EquippedArmorData(self.conn, armor2, 999)
        assert ea1 != ea3

        ea4 = EquippedArmorData(self.conn, armor1, 183)
        assert ea1 != ea4

        ea5 = EquippedArmorData(self.conn, armor2, 183)
        assert ea1 != ea5

        not_ea = "not an equipped armor"
        assert ea1 != not_ea

    def test_successful_equipped_armor_init(self):
        expected_id = 883
        actual_id = self.equipped_armor._EquippedArmorData__bng_armor_id

        assert expected_id == actual_id
        assert self.equipped_armor._manifest_data

    def test_unsuccessful_equipped_armor_init(self):
        bad_id = 331
        bad_armor = ArmorData(self.conn, bad_id, self.manifest)
        bad_equipped_armor = EquippedArmorData(self.conn, bad_armor, 10101010101, self.manifest)

        assert bad_equipped_armor._EquippedArmorData__bng_armor_id == -1
        assert not bad_equipped_armor._manifest_data

    def test_successful_equipped_armor_define_data(self):
        self.equipped_armor.define_data()

        assert self.equipped_armor.data == {"slot_type": "HELMET"}
