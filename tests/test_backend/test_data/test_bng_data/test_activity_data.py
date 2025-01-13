import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import ActivityData

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
