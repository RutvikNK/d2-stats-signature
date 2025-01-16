import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import ArmorData
from backend.manifest.destiny_manifest import DestinyManifest

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
    
    def test_armor_eq(self):
        a1 = ArmorData(self.conn, 555)
        a2 = ArmorData(self.conn, 555)

        assert a1 == a2

        a3 = ArmorData(self.conn, 111)
        assert a1 != a3

        not_a = "not an armor"
        assert a1 != not_a

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
