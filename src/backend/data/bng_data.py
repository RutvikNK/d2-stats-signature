from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from dotenv import load_dotenv
import os

from backend.extract.bng_api_connector import BungieConnector
import backend.manifest.destiny_manifest as manifest
from backend.data.bng_types import (
    PLATFORM,
    CLASS,
    WEAPON_SLOT_TYPE,
    WEAPON_TYPE,
    ARMOR_SLOT_TYPE,
    AMMO_TYPE,
    DAMAGE_TYPE,
    RARITY
)
 
MANIFEST = manifest.DestinyManifest()

class BungieData(ABC):
    def __init__(self, connection: BungieConnector) -> None:
        self._bng_conn = connection
        self.root = "https://www.bungie.net/Platform"
        self.__data: dict = dict()

    def get_data(self, path):
        return self.bng_conn.get_url_request(path)

    @abstractmethod
    def define_data(self):
        pass
    
    @property
    def bng_conn(self):
        return self._bng_conn
    
    @property
    def data(self) -> dict:
        return self.__data

class PlayerData(BungieData):
    def __init__(self, connection: BungieConnector, membership_id: int, membership_type: int) -> None:
        super().__init__(connection)
        self.__data: dict = dict()
        self._id = membership_id
        self._type = membership_type
        self._bng_mem_endpoint = f"{self.root}/User/GetMembershipsById/{membership_id}/{membership_type}/"
        self._dst_prof_endpoint = f"{self.root}/Destiny2/{self._type}/Profile/{self._id}/?components={100}"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, PlayerData):
            return value._id == self._id
        else:
            return False

    def define_data(self, bng_member_endpoint: str="", destiny_prof_endpoint: str="") -> None:
        if not bng_member_endpoint:
            bng_member_endpoint = self._bng_mem_endpoint

        if not destiny_prof_endpoint:
            destiny_prof_endpoint = self._dst_prof_endpoint

        bng_mem_data = self.get_data(bng_member_endpoint)
        destiny_prof_data = self.get_data(destiny_prof_endpoint)
        
        if bng_mem_data and destiny_prof_data:
            try:
                self.__data["date_created"] = bng_mem_data["bungieNetUser"]["firstAccess"][:10]
                self.__data["date_last_played"] = destiny_prof_data["profile"]["data"]["dateLastPlayed"][:10]
                self.__data["bng_id"] = int(bng_mem_data["bungieNetUser"]["membershipId"])
                self.__data["destiny_id"] = self._id
                self.__data["bng_username"] = bng_mem_data["bungieNetUser"]["uniqueName"]
                self.__data["platform"] = PLATFORM(self._type).name
                self.__data["character_ids"] = destiny_prof_data["profile"]["data"]["characterIds"]
            except KeyError:
                self.__data.clear()

    @property
    def data(self) -> dict:
        return self.__data

class CharacterData(PlayerData):
    def __init__(self, connection: BungieConnector, membership_id: int, membership_type: int, character_id: int, player_id: int) -> None:
        super().__init__(connection, membership_id, membership_type)
        self.__data: dict = dict()
        self.__equipment: dict = dict()
        self._character_id = character_id
        self._player_id = player_id
        self._char_data_endpoint = f"{self.root}/Destiny2/{self._type}/Profile/{self._id}/Character/{self._character_id}/"
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, CharacterData):
            return value._character_id == self._character_id
        else:
            return False

    def define_data(self):
        char_data = self.get_data(f"{self._char_data_endpoint}?components=Characters")
        equipped_item_ids = self.get_all_equipped_items()
        
        if char_data:
            try:
                self.__data["bng_character_id"] = self._character_id
                self.__data["player_id"] = self._player_id
                self.__data["class"] = CLASS(char_data["character"]["data"]["classType"]).name
                self.__data["date_last_played"] = char_data["character"]["data"]["dateLastPlayed"][:10]
                if len(equipped_item_ids) == 8:
                    self.__equipment["weapons"] = equipped_item_ids[:3]
                    self.__equipment["armor"] = equipped_item_ids[3:]
                else:
                    self.__equipment["weapons"] = []
                    self.__equipment["armor"] = []
            except KeyError:
                self.__data.clear()
                self.__equipment.clear()

    def get_activity_hist_instances(self, mode: int, count: int, path: str="") -> list[int]:
        if not path:
            path = f"{self.root}/Destiny2/{self._type}/Account/{self._id}/Character/{self._character_id}/Stats/Activities/?count={count}&mode={mode}&page=1"
        data = self.get_data(path)

        instance_ids: list[int] = []
        if data:
            for activity in data["activities"]:
                instance_ids.append(int(activity["activityDetails"]["instanceId"]))

        return instance_ids

    def get_all_equipped_items(self, equip_path: str="") -> list[str]:
        if not equip_path:
            char_equipped_data = self.get_data(f"{self._char_data_endpoint}?components=CharacterEquipment")
        else:
            char_equipped_data = self.get_data(equip_path)
        
        item_ids = []
        if char_equipped_data:
            try:
                for item in char_equipped_data["equipment"]["data"]["items"]:
                    if len(item_ids) < 8:
                        item_ids.append(item["itemHash"])
                    else:
                        break
            except KeyError:
                pass
        
        return item_ids
    
    @property
    def data(self) -> dict:
        return self.__data
    
    @property
    def equipment(self) -> dict:
        return self.__equipment
    
    @property
    def character_id(self) -> int:
        return self._character_id

class WeaponData(BungieData):
    def __init__(self, connection: BungieConnector, weapon_id: int, manifest: manifest.DestinyManifest=MANIFEST) -> None:
        super().__init__(connection)
        self.__data: dict = dict()
        self._weapon_id = weapon_id
        try:
            self._manifest_data = manifest.all_data["DestinyInventoryItemDefinition"][self._weapon_id]
        except KeyError:
            self._manifest_data = dict()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, WeaponData):
            return value._weapon_id == self._weapon_id
        else:
            return False

    def define_data(self):
        if self._manifest_data:
            try:
                self.__data["bng_weapon_id"] = self._weapon_id
            
                weapon_type = self._manifest_data["itemTypeDisplayName"].upper().replace(" ", "_")
                self.__data["weapon_type"] = WEAPON_TYPE[weapon_type].name

                self.__data["weapon_name"] = self._manifest_data["displayProperties"]["name"]
                self.__data["ammo_type"] = AMMO_TYPE(self._manifest_data["equippingBlock"]["ammoType"]).name
                self.__data["slot"] = WEAPON_SLOT_TYPE(self._manifest_data["equippingBlock"]["equipmentSlotTypeHash"]).name
                self.__data["damage_type"]  = DAMAGE_TYPE(self._manifest_data["damageTypes"][0]).name
                self.__data["rarity"] = RARITY[self._manifest_data["itemTypeAndTierDisplayName"].split(" ")[0].upper()].name
            except KeyError:
                pass
        else:
            self.__data.clear()

    @property
    def data(self) -> dict:
        return self.__data

class EquippedWeaponData(BungieData):
    def __init__(self, connection: BungieConnector, weapon: WeaponData, bng_character_id: int, manifest: manifest.DestinyManifest=MANIFEST) -> None:
        super().__init__(connection)
        self.__weapon = weapon
        self.__bng_character_id = bng_character_id
        try:
            self.__bng_weapon_id = weapon.data["bng_weapon_id"]
            self._manifest_data = manifest.all_data["DestinyInventoryItemDefinition"][self.__bng_weapon_id]
        except KeyError:
            self.__bng_weapon_id = -1
            self._manifest_data = dict()
        self.__data: dict = dict()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, EquippedWeaponData):
            return self.__weapon.data["bng_weapon_id"] == value.__weapon.data["bng_weapon_id"] and self.__bng_character_id == value.__bng_character_id
        else:
            return False
    
    def define_data(self):
        if self._manifest_data:
            try:
                self.__data["slot_type"] = WEAPON_SLOT_TYPE(self._manifest_data["equippingBlock"]["equipmentSlotTypeHash"]).name
                if self.__weapon.data["weapon_type"] == "FUSION_RIFLE" or self.__weapon.data["weapon_type"] == "LINEAR_FUSION_RIFLE":
                    self.__data["main_stat"] = f"{self._manifest_data["stats"]["stats"]["2961396640"]["value"]}ms"
                elif self.__weapon.data["weapon_type"] == "SWORD":
                    self.__data["main_stat"] = f"{self._manifest_data["stats"]["stats"]["2837207746"]["value"]} swing speed"
                else:
                    self.__data["main_stat"] = f"{self._manifest_data["stats"]["stats"]["4284893193"]["value"]}rpm"
            except KeyError:
                pass
        else:
            self.__data.clear()

    @property
    def data(self) -> dict:
        return self.__data

class ArmorData(BungieData):
    def __init__(self, connection: BungieConnector, armor_id: int, manifest: manifest.DestinyManifest=MANIFEST) -> None:
        super().__init__(connection)
        self.__data: dict = dict()
        self.__armor_id = armor_id
        try:
            self._manifest_data = manifest.all_data["DestinyInventoryItemDefinition"][self.__armor_id]
        except KeyError:
            self._manifest_data = dict()
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, ArmorData):
            return value.__armor_id == self.__armor_id
        else:
            return False

    def define_data(self):
        if self._manifest_data:
            try:
                self.__data["bng_armor_id"] = self.__armor_id
                self.__data["armor_name"] = self._manifest_data["displayProperties"]["name"]
                self.__data["slot"] = ARMOR_SLOT_TYPE(self._manifest_data["equippingBlock"]["equipmentSlotTypeHash"]).name
                self.__data["rarity"] = RARITY[self._manifest_data["itemTypeAndTierDisplayName"].split(" ")[0].upper()].name
            except KeyError:
                pass
        else:
            self.__data.clear()
    @property
    def data(self) -> dict:
        return self.__data

class EquippedArmorData(BungieData):
    def __init__(self, connection: BungieConnector, armor_data: ArmorData, bng_character_id, manifest: manifest.DestinyManifest=MANIFEST) -> None:
        super().__init__(connection)
        self.__armor = armor_data
        self.__bng_character_id = bng_character_id
        try:
            self.__bng_armor_id = self.__armor.data["bng_armor_id"]
            self._manifest_data = manifest.all_data["DestinyInventoryItemDefinition"][self.__bng_armor_id]
        except KeyError:
            self.__bng_armor_id = -1
            self._manifest_data = dict()
        self.__data: dict = dict()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, EquippedArmorData):
            return self.__armor.data["bng_armor_id"] == value.__armor.data["bng_armor_id"] and self.__bng_character_id == value.__bng_character_id
        else:
            return False

    def define_data(self):
        if self._manifest_data:
            try:
                self.__data["slot_type"] = ARMOR_SLOT_TYPE(self._manifest_data["equippingBlock"]["equipmentSlotTypeHash"]).name
            except KeyError:
                pass
        else:
            self.__data.clear()

    @property
    def data(self) -> dict:
        return self.__data

class ActivityData(BungieData):
    def __init__(self, connection: BungieConnector, activity_id, manifest: manifest.DestinyManifest=MANIFEST) -> None:
        super().__init__(connection)
        self.__data: dict = dict()
        self.__activity_id = activity_id
        try:
            self._manifest_data = manifest.all_data["DestinyActivityDefinition"][self.__activity_id]
        except KeyError:
            self._manifest_data = dict()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ActivityData):
            return value.__activity_id == self.__activity_id
        else:
            return False

    def define_data(self):
        if self._manifest_data:
            try:
                self.__data["bng_activity_id"] = self.__activity_id
                self.__data["activity_name"] = self._manifest_data["displayProperties"]["name"]
                self.__data["max_fireteam_size"] = self._manifest_data["matchmaking"]["maxPlayers"]
                
                type_hash = self._manifest_data["activityTypeHash"]
                type_data = MANIFEST.all_data["DestinyActivityTypeDefinition"][type_hash]
                self.__data["type"] = type_data["displayProperties"]["name"]
                
                modifier_manifest = MANIFEST.all_data["DestinyActivityModifierDefinition"]
                modifiers = ""
                for modifier_hash in self._manifest_data["modifiers"]:
                    try:
                        curr_mod = modifier_manifest[modifier_hash["activityModifierHash"]]["displayProperties"]["name"]
                        if curr_mod:
                            modifiers += f"{curr_mod}, "
                    except KeyError:
                        continue
                else:
                    modifiers = modifiers[:-2]
                
                if len(modifiers) > 100:
                    modifiers = modifiers[:100] + "..."

                self.__data["modifiers"] = modifiers
            except KeyError:
                pass
        else:
            self.__data.clear()
    
    @property
    def data(self) -> dict:
        return self.__data

class ActivityInstanceData(BungieData):
    def __init__(self, connection: BungieConnector, instance_id: int) -> None:
        super().__init__(connection)
        self._instance_id = instance_id
        self._pgcr_path = f"{self.root}/Destiny2/Stats/PostGameCarnageReport/{self._instance_id}/"
        self._pgcr = self.get_data(self._pgcr_path)
        self._character_pgdata = dict()
        self.__instance_stats: list[ActivityStatsData] = []

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ActivityInstanceData):
            return value._instance_id == self._instance_id
        else:
            return False

    def define_data(self):
        if self._pgcr:
            try:
                self.__activity_id = self._pgcr["activityDetails"]["directorActivityHash"]
            except KeyError:
                return

            for character in self._pgcr["entries"]:
                try:
                    character_id = int(character["characterId"])

                    weapon_ids = []
                    for weapon in character["extended"]["weapons"]:
                        weapon_ids.append(weapon["referenceId"])

                    self._character_pgdata[character_id] = weapon_ids
                except ValueError:
                    continue
                except KeyError:
                    continue
            
    def create_stats(self) -> None:
        for character, weapons in self._character_pgdata.items():
            for weapon_id in weapons:
                new_stats = ActivityStatsData(self.bng_conn, self._instance_id, weapon_id, character, self.__activity_id)
                new_stats.define_data()
                self.__instance_stats.append(new_stats)

    def get_instance_stats(self) -> list[ActivityStatsData]:
        return self.__instance_stats

    @property
    def participants_data(self) -> dict:
        return self._character_pgdata
    
    @property
    def instance_id(self) -> int:
        return self._instance_id
                        
class ActivityStatsData(BungieData):
    def __init__(self, connection: BungieConnector, instance_id: int, weapon_id: int, char_id: int, activity_id: int) -> None:
        super().__init__(connection)
        self.__data: dict = dict()
        self.__og_data: dict = dict()
        self.__participant = dict()
        self.__weapon_id = weapon_id
        self.__character_id = char_id
        self.__instance_id = instance_id
        self.__activity_id = activity_id
        self._pgcr_path = f"{self.root}//Destiny2/Stats/PostGameCarnageReport/{self.__instance_id}/"

    def define_data(self):
        pgcr = self.get_data(self._pgcr_path)

        if pgcr:
            perf_report = self.__get_participating_character(pgcr)

            if perf_report:
                weapons_manifest = MANIFEST.all_data["DestinyInventoryItemDefinition"]
                activities_manifest = MANIFEST.all_data["DestinyActivityDefinition"]
                classes_manifesst = MANIFEST.all_data["DestinyClassDefinition"]

                self.__data["instance_id"] = self.__instance_id
                
                self.__og_data["bng_activity_id"] = self.__activity_id
                self.__og_data["bng_character_id"] = self.__character_id
                self.__og_data["bng_weapon_id"] = self.__weapon_id

                self.__participant["destiny_id"] = perf_report["player"]["destinyUserInfo"]["membershipId"]
                self.__participant["member_type"] = perf_report["player"]["destinyUserInfo"]["membershipType"]

                weapon_data = self.__get_weapon(perf_report)

                if weapon_data:
                    self.__data["kills"] = weapon_data["values"]["uniqueWeaponKills"]["basic"]["value"]
                    self.__data["precision_kills"] = weapon_data["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"]
                    
                    try:
                        self.__data["precision_kills_percent"] =  round((self.__data["precision_kills"] / self.__data["kills"]) * 100, 2)
                    except ZeroDivisionError:
                        self.__data["precision_kills_percent"] = 0.0

                self.__data["weapon_name"] = weapons_manifest[self.__weapon_id]["displayProperties"]["name"]
                try:
                    self.__data["activity_name"] = activities_manifest[pgcr["activityDetails"]["directorActivityHash"]]["displayProperties"]["name"]
                    self.__data["character_class"] = classes_manifesst[perf_report["player"]["classHash"]]["displayProperties"]["name"]
                except KeyError:
                    self.__data.clear()
                 
    def __get_participating_character(self, pgcr: dict) -> Optional[dict]:
        for player in pgcr["entries"]:
            if int(player["characterId"]) == self.__character_id:
                return player
    
    def __get_weapon(self, pgcr: dict) -> Optional[dict]:
        try:
            weapons_data = pgcr["extended"]["weapons"]
            for weapon in weapons_data:
                if weapon["referenceId"] == self.__weapon_id:
                    return weapon
        except KeyError:
            return

    @property
    def data(self) -> dict:
        return self.__data
    
    @property
    def og_data(self) -> dict:
        return self.__og_data
    
    @property
    def participant(self) -> dict:
        return self.__participant

class DataFactory:
    bng_conn = BungieConnector("10E792629C2A47E19356B8A79EEFA640") 

    @staticmethod
    def get_player(member_id: int, member_type: int) -> PlayerData:
        player = PlayerData(DataFactory.bng_conn, member_id, member_type)
        player.define_data()
        return player
    
    @staticmethod
    def get_character(member_id: int, member_type: int, char_id: int, player_id: int) -> CharacterData:
        character = CharacterData(DataFactory.bng_conn, member_id, member_type, char_id, player_id)
        character.define_data()
        return character
    
    @staticmethod
    def get_weapon(weapon_id: int) -> WeaponData:
        weapon = WeaponData(DataFactory.bng_conn, weapon_id)
        weapon.define_data()
        return weapon
    
    @staticmethod
    def get_armor(armor_id: int) -> ArmorData:
        armor = ArmorData(DataFactory.bng_conn, armor_id)
        armor.define_data()
        return armor
    
    @staticmethod
    def get_activity(activity_id: int) -> ActivityData:
        activity = ActivityData(DataFactory.bng_conn, activity_id)
        activity.define_data()
        return activity
    
    @staticmethod
    def get_activity_instance(instance_id: int) -> ActivityInstanceData:
        instance = ActivityInstanceData(DataFactory.bng_conn, instance_id)
        instance.define_data()
        return instance
    
    @staticmethod
    def get_equipped_weapon(weapon_data: WeaponData, bng_character_id: int) -> EquippedWeaponData:
        weapon = EquippedWeaponData(DataFactory.bng_conn, weapon_data, bng_character_id)
        weapon.define_data()
        return weapon
    
    @staticmethod
    def get_equipped_armor(armor_data: ArmorData, bng_character_id: int) -> EquippedArmorData:
        armor = EquippedArmorData(DataFactory.bng_conn, armor_data, bng_character_id)
        armor.define_data()
        return armor

# def main():
#     load_dotenv()

#     bng_conn = BungieConnector(os.getenv("X_API_KEY"))
#     mem_id = 4611686018441248186
#     mem_type = 1

#     player = PlayerData(bng_conn, mem_id, mem_type)
#     player.define_data()
#     for k, v in player.data.items():
#         print(f"{k}: {v}")
    
#     player_character = CharacterData(bng_conn, mem_id, mem_type, int(player.data["character_ids"][0]), 1)
#     player_character.define_data()
#     print()
#     for k, v in player_character.data.items():
#         print(f"{k}: {v}")

#     # riptide_id = player_character.equipment["weapons"][0]
#     # riptide = WeaponData(bng_conn, riptide_id)
#     # riptide.define_data()
#     # print()
#     # for k, v in riptide.data.items():
#     #     print(f"{k}: {v}")

#     # equipped_riptide = EquippedWeaponData(bng_conn, riptide, mem_id)
#     # equipped_riptide.define_data()
#     # print()
#     # for k, v in equipped_riptide.data.items():
#     #     print(f"{k}: {v}")

#     # helmet_id = player_character.equipment["equipped_armor"][0]
#     # helmet = ArmorData(bng_conn, helmet_id)
#     # helmet.define_data()
#     # print()
#     # for k, v in helmet.data.items():
#     #     print(f"{k}: {v}")

#     rumble_data = player_character.get_activity_hist_instances(48, 1)
#     # for k, v in rumble_data.items(): # type: ignore
#     #     print(f"{k}: {v}:")
        
#     # rumble_id = 2259621230
#     # rumble = ActivityData(bng_conn, rumble_id)
#     # rumble.define_data()
#     # print()
#     # for k, v in rumble.data.items():
#     #     print(f"{k}: {v}")
    
#     rumble_instance_id = int(rumble_data[0])  # type: ignore
#     rumble_instance = ActivityInstanceData(bng_conn, rumble_instance_id)
#     rumble_instance.define_data()
#     print()
#     for k, v in rumble_instance._character_pgdata.items():
#         print(f"{k}: {v}")

#     # rumble_all_stats = []
#     # for character, weapons in rumble_instance.participants_data.items():
#     #     for weapon_id in weapons:
#     #         new_stats = ActivityStatsData(bng_conn, rumble_instance_id, weapon_id, character, rumble_id)
#     #         new_stats.define_data()
#     #         rumble_all_stats.append(new_stats)
    
#     # for stat in rumble_all_stats:
#     #     print()
#     #     for k, v in stat.data.items():
#     #         print(f"{k}: {v}")

# if __name__ == "__main__":
#     main()