import unittest
from unittest.mock import MagicMock

from backend.data.bng_data import ActivityData
from backend.manifest.destiny_manifest import DestinyManifest

class ActivityDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = MagicMock()
        
        self.manifest_data = MagicMock()
        self.manifest = DestinyManifest()
        self.manifest.all_data = self.manifest_data

        self.rumble_id = 771494
        self.rumble_activity = ActivityData(self.conn, self.rumble_id, self.manifest)
    
    def test_activity_data_eq(self):
        ad1 = ActivityData(self.conn, 441)
        ad2 = ActivityData(self.conn, 441)

        assert ad1 == ad2

        ad3 = ActivityData(self.conn, 301)
        assert ad1 != ad3

        not_ad = "not activity data"
        assert ad1 != not_ad

    def test_successful_activity_data_init(self):
        mock_manifest_data = {
            "DestinyActivityDefinition": {
                771494: "Activity Data"
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest_data.__getitem__

        assert self.rumble_activity._manifest_data
    
    def test_unsuccessful_activity_data_init(self):
        bad_id = 414
        bad_activity = ActivityData(self.conn, bad_id)

        assert not bad_activity._manifest_data

    def test_successful_activity_data_def(self):
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
                    ]
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__
        
        activity = ActivityData(self.conn, self.rumble_id, self.manifest)

        activity.define_data()
        expected_activity_data = {
            "bng_activity_id": 771494,
            "activity_name": "Activity Name",
            "max_fireteam_size": 3,
            "type": "Activity Type",
            "modifiers": "Modifier 1, Modifier 2, Modifier 3, Modifier 4, Modifier 5"
        }

        assert activity.data == expected_activity_data
        
        modifiers = activity.data["modifiers"]
        assert not modifiers.endswith(", ")
    
    def test_unsuccessful_activity_data_def_no_manifest(self):
        bad_id = 123456789
        bad_activity = ActivityData(self.conn, bad_id)
        bad_activity.define_data()

        assert bad_activity.data == {}
    
    def test_overflowing_activity_data_modifiers(self):
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
                    },
                6: {
                        "displayProperties": {
                            "name": "Modifier 6"
                        }
                    },
                7: {
                        "displayProperties": {
                            "name": "Modifier 7"
                        }
                    },
                8: {
                        "displayProperties": {
                            "name": "Modifier 8"
                        }
                    },
                9: {
                        "displayProperties": {
                            "name": "Modifier 9"
                        }
                    },
                10: {
                        "displayProperties": {
                            "name": "Modifier 10"
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
                        {
                            "activityModifierHash": 6
                        },
                        {
                            "activityModifierHash": 7
                        },
                        {
                            "activityModifierHash": 8
                        },
                        {
                            "activityModifierHash": 9
                        },
                        {
                            "activityModifierHash": 10
                        },
                    ]
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__

        activity = ActivityData(self.conn, self.rumble_id, self.manifest)
        activity.define_data()

        expected_activity_data = {
            "bng_activity_id": 771494,
            "activity_name": "Activity Name",
            "max_fireteam_size": 3,
            "type": "Activity Type",
            "modifiers": "Modifier 1, Modifier 2, Modifier 3, Modifier 4, Modifier 5, Modifier 6, Modifier 7, Modifier 8, Modi..."
        }

        assert activity.data == expected_activity_data

        modifiers = activity.data["modifiers"] 
        assert modifiers.endswith("...")

    def test_unsuccessful_activity_data_def_bad_modifier_key(self):
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
                            "bad key": 1
                        },
                        {
                            "activityModifierHash": 2
                        },
                        {
                            "bad key": 3
                        },
                        {
                            "activityModifierHash": 4
                        },
                        {
                            "activityModifierHash": 5
                        },
                    ]
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__
        
        activity = ActivityData(self.conn, self.rumble_id, self.manifest)

        activity.define_data()
        expected_activity_data = {
            "bng_activity_id": 771494,
            "activity_name": "Activity Name",
            "max_fireteam_size": 3,
            "type": "Activity Type",
            "modifiers": "Modifier 2, Modifier 4, Modifier 5"
        }

        assert activity.data == expected_activity_data
        
        modifiers = activity.data["modifiers"]
        assert not modifiers.endswith(", ")
    
    def test_unsuccessful_activity_data_def_bad_manifest(self):
        mock_manifest = {
            "DestinyActivityDefinition": {
                771494: {
                    "bad key": 100
                }
            }
        }
        self.manifest_data.__getitem__.side_effect = mock_manifest.__getitem__
        
        activity = ActivityData(self.conn, self.rumble_id, self.manifest)

        activity.define_data()
        assert activity.data == {}
    