from typing import Optional
from time import sleep
from dotenv import load_dotenv
import os

from backend.extract.bng_api_connector import BungieConnector
from backend.load.executor import DatabaseExecutor
from backend.load.connector import SQLConnector
from backend.data.bng_types import *
from backend.data.bng_data import (
    PlayerData, 
    CharacterData, 
    WeaponData,
    EquippedWeaponData, 
    ArmorData,
    EquippedArmorData, 
    ActivityData, 
    ActivityInstanceData, 
    ActivityStatsData,
    DataFactory
)

load_dotenv()

BNG_CONN = BungieConnector(os.getenv("X_API_KEY"))

class DatabasePlayerManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__players: list[PlayerData] = []
    
    def read_data(self) -> None:
        db_data = self.__control.retrieve_all("`Player`")
        
        if db_data:
            for tuple in db_data:
                self.add_existing_player(tuple)

    def update_date_last_played(self, member_id: int, platform: int):
        player = PlayerData(BNG_CONN, member_id, platform)
        player.define_data()

        data = {"date_last_played": player.data["date_last_played"]}
        conditions = {"destiny_id": member_id}

        if player.data:
            self.__control.update_row("`Player`", data, conditions)
            return player

    def add_player_by_username(self, username: str, platform: int) -> PlayerData | None:
        path = f"https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayerByBungieName/{platform}/"
        try:
            split_username = username.split("#")
            body = {"displayName": split_username[0], "displayNameCode": split_username[1]}
            resp = BNG_CONN.get_url_request(path, body)
        except ValueError:
            return None
        except IndexError:
            return None
        
        if resp:
            member_id = int(resp[0]["membershipId"])
            player = DataFactory.get_player(member_id, platform)
            if player not in self.__players:
                self.__players.append(player)
            
            self.__control.insert_row("`Player`", player)
            return player
        else:
            return None
    
    def add_existing_player(self, data) -> None:
        player = PlayerData(BNG_CONN, data[1], PLATFORM[data[6]].value) # type: ignore
        player.define_data()
        if player not in self.__players:
            self.__players.append(player)

    def add_new_player(self, member_id: int, member_type: int) -> None:
        # existing_player = self.__control.select_rows("`Player`", ["*"], {"destiny_id": member_id})
        
        # if not existing_player:
            new_player = DataFactory.get_player(member_id, member_type)
            if new_player not in self.__players:
                self.__players.append(new_player)

            self.__control.insert_row("`Player`", new_player)
        # else:
        #     self.add_existing_player(existing_player)

    def get_character_and_player_ids(self, member_id: int):
        result = self.__control.select_rows("`Player`", ["character_ids", "player_id"], {"destiny_id": member_id})

        if result:
            character_ids = str(result[0][0].replace("[", ""))  # type: ignore
            character_ids = character_ids.replace("]", "")
            character_ids = character_ids.replace("\'", "")
            character_ids = character_ids.split(", ")
            for i in range(len(character_ids)):
                character_ids[i] = int(character_ids[i])  # type: ignore

            return character_ids, result[0][1] # type: ignore
        else:
            return None, None

class DatabaseCharacterManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__characters: list[CharacterData] = []

    def add_new_character(self, member_id: int, member_type: int, character_id: int, player_id: int=-1) -> None:
        if player_id == -1:
            player = self.__control.select_rows("`Player`", ["player_id"], {"destiny_id": member_id})
            if player:
                player_id = player[0][0]  # type: ignore
        
        if player_id != -1:
            new_char = DataFactory.get_character(member_id, member_type, character_id, player_id)
            
            if new_char not in self.__characters:
                self.__characters.append(new_char)

            self.__control.insert_row("`Character`", new_char)

    def get_activity_history(self, character_id: int, mode: int, count: int):
        character = self.find_character(character_id)
        if character:
            instance_ids = character.get_activity_hist_instances(mode, count)
            return instance_ids

    def find_character(self, character_id: int) -> Optional[CharacterData]:
        for character in self.__characters:
            if character.character_id == character_id:
                return character

class DatabaseWeaponManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__weapons: list[WeaponData] = []

    def update_weapon(self, weapon_id: int):
        bng_weapon_id = self.__control.select_rows("`Weapon`", ["bng_weapon_id"], {"weapon_id": weapon_id})
        
        if bng_weapon_id and bng_weapon_id[0][0] != 0:  # type: ignore
            weapon = DataFactory.get_weapon(bng_weapon_id[0][0])  # type: ignore
            result = self.__control.update_row("`Weapon`", weapon.data, {"bng_weapon_id": weapon.data["bng_weapon_id"]})
            if result:
                return weapon.data

    def add_new_weapon(self, weapon_id: int) -> WeaponData:
        # exisiting_weapon = self.__control.select_rows("`Weapon`", ["weapon_id"], {"bng_weapon_id": weapon_id})
        
        # if not exisiting_weapon:
        new_weapon = DataFactory.get_weapon(weapon_id)  
        if new_weapon not in self.__weapons:
            self.__weapons.append(new_weapon)

        self.__control.insert_row("`Weapon`", new_weapon)

        return new_weapon

    def get_weapon(self, bng_weapon_id: int) -> Optional[WeaponData]:
        for weapon in self.__weapons:
            if weapon.data["bng_weapon_id"] == bng_weapon_id:
                return weapon

class DatabaseArmorManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__armor: list[ArmorData] = []

    def update_armor(self, armor_id: int):
        bng_armor_id = self.__control.select_rows("`Armor`", ["bng_armor_id"], {"armor_id": armor_id})
        
        if bng_armor_id and bng_armor_id[0][0] != 0:  # type: ignore
            armor = DataFactory.get_armor(bng_armor_id[0][0])  # type: ignore
            result = self.__control.update_row("`Armor`", armor.data, {"bng_armor_id": armor.data["bng_armor_id"]})
            if result:
                return armor.data

    def add_new_armor(self, armor_id: int) -> ArmorData:
        # existing_armor = self.__control.select_rows("`Armor`", ["armor_id"], {"bng_armor_id": armor_id})
        
        # if not existing_armor:
        new_armor = DataFactory.get_armor(armor_id)
        if new_armor not in self.__armor:
            self.__armor.append(new_armor)

        self.__control.insert_row("`Armor`", new_armor)

        return new_armor

    def get_armor(self, bng_armor_id: int) -> Optional[ArmorData]:
        for armor in self.__armor:
            if armor.data["bng_armor_id"] == bng_armor_id:
                return armor

class DatabaseActivityManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__activities: list[ActivityData] = []

    def add_new_activity(self, activitiy_id: int) -> None:
        # existing_activity = self.__control.select_rows("`Activity`", ["activitiy_id"], {"bng_activitiy_id": activitiy_id})

        # if not existing_activity:
            new_activity = DataFactory.get_activity(activitiy_id)
            if new_activity not in self.__activities:
                self.__activities.append(new_activity)

            self.__control.insert_row("`Activity`", new_activity)

class DatabaseActivityInstanceManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__instances: list[ActivityInstanceData] = []
    
    def create_instance(self, instance_id: int) -> ActivityInstanceData:
        new_instance = DataFactory.get_activity_instance(instance_id)

        if new_instance not in self.__instances:
            self.__instances.append(new_instance)

        return new_instance
    
    def find_instance(self, instance_id: int) -> Optional[ActivityInstanceData]:
        for instance in self.__instances:
            if instance.instance_id == instance_id:
                return instance

    def create_instance_stats(self, instance_id: int):
        instance = self.find_instance(instance_id)
        
        if instance:
            instance.create_stats()

    def get_instances(self) -> list[ActivityInstanceData]:
        return self.__instances

class EquipmentManager:
    def __init__(self, db_control: DatabaseExecutor, w_control: DatabaseWeaponManager, a_control: DatabaseArmorManager) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__weapons: list[EquippedWeaponData] = []
        self.__armor: list[EquippedArmorData] = []
        self.__w_manager: DatabaseWeaponManager = w_control
        self.__a_manager: DatabaseArmorManager = a_control

    def add_new_weapon(self, bng_weapon_id: int, bng_character_id: int) -> None:
        weapon = self.__w_manager.get_weapon(bng_weapon_id)

        if not weapon:
            self.__w_manager.add_new_weapon(bng_weapon_id)
            weapon = self.__w_manager.get_weapon(bng_weapon_id)

        weapon_equipment = DataFactory.get_equipped_weapon(weapon, bng_character_id)  # type: ignore
        if weapon_equipment not in self.__weapons:
            self.__weapons.append(weapon_equipment)

        char_id = self.__control.select_rows("`Character`", ["character_id"], {"bng_character_id": bng_character_id})
        weapon_id = self.__control.select_rows("`Weapon`", ["weapon_id"], {"bng_weapon_id": bng_weapon_id})
        if char_id and weapon_id:
            weapon_equipment.data["character_id"] = char_id[0][0]  # type: ignore
            weapon_equipment.data["weapon_id"] = weapon_id[0][0]  # type: ignore

            self.__control.insert_row("`Equipped_Weapons`", weapon_equipment)

    def add_new_armor(self, bng_armor_id: int, bng_character_id: int) -> None:
        armor = self.__a_manager.get_armor(bng_armor_id)
        

        if not armor:
            self.__a_manager.add_new_armor(bng_armor_id)
            armor = self.__a_manager.get_armor(bng_armor_id)

        armor_equipment = DataFactory.get_equipped_armor(armor, bng_character_id)  # type: ignore

        if armor_equipment not in self.__armor:
            self.__armor.append(armor_equipment)

        char_id = self.__control.select_rows("`Character`", ["character_id"], {"bng_character_id": bng_character_id})
        armor_id = self.__control.select_rows("`Armor`", ["armor_id"], {"bng_armor_id": bng_armor_id})
        if char_id:
            armor_equipment.data["character_id"] = char_id[0][0]  # type: ignore
            armor_equipment.data["armor_id"] = armor_id[0][0]  # type: ignore

            self.__control.insert_row("`Equipped_Armor`", armor_equipment)

class DatabaseManager:
    def __init__(
            self, 
            db_control: DatabaseExecutor, 
            a_control: DatabaseActivityManager, 
            w_control: DatabaseWeaponManager, 
            c_control: DatabaseCharacterManager, 
            p_control: DatabasePlayerManager,
            e_control: EquipmentManager) -> None:
        
        self.__control: DatabaseExecutor = db_control
        self.__a_manager: DatabaseActivityManager = a_control
        self.__w_manager: DatabaseWeaponManager = w_control
        self.__c_manager: DatabaseCharacterManager = c_control
        self.__p_manager: DatabasePlayerManager = p_control
        self.__e_manager: EquipmentManager = e_control

        self.__stats_data: list[ActivityStatsData] = []

    def add_new_stat_block(self, instance: ActivityInstanceData, bng_char_id: int=0) -> ActivityStatsData | bool:
        def define_stats(stat: ActivityStatsData):
            if stat.data:
                self.__a_manager.add_new_activity(stat.og_data["bng_activity_id"])
                self.__w_manager.add_new_weapon(stat.og_data["bng_weapon_id"])
                self.__p_manager.add_new_player(stat.participant["destiny_id"], stat.participant["member_type"])
                self.__c_manager.add_new_character(stat.participant["destiny_id"], stat.participant["member_type"], stat.og_data["bng_character_id"])

                # figure out a better way to do this :(
                activity_id_result = self.__control.select_rows("`Activity`", ["activity_id"], {"bng_activity_id": stat.og_data["bng_activity_id"]})
                if activity_id_result:
                    stat.data["activity_id"] = activity_id_result[0][0]  # type: ignore
                
                weapon_id_result = self.__control.select_rows("`Weapon`", ["weapon_id"], {"bng_weapon_id": stat.og_data["bng_weapon_id"]})
                if weapon_id_result:
                    stat.data["weapon_id"] = weapon_id_result[0][0]   # type: ignore

                character_id_result = self.__control.select_rows("`Character`", ["character_id"], {"bng_character_id": stat.og_data["bng_character_id"]})
                if character_id_result:
                    stat.data["character_id"] = character_id_result[0][0]   # type: ignore
                
                if stat not in self.__stats_data:
                    self.__stats_data.append(stat)

                self.__control.insert_row("`Activity_Stats`", stat)
                return stat

        if bng_char_id:
            result = self.__control.select_rows("Activity_Stats", ["*"], {"instance_id": instance.instance_id})
            if result:
                return False

        instance_stats = instance.get_instance_stats()
        for stat in instance_stats:
            if bng_char_id and stat.og_data["bng_character_id"] == bng_char_id:
                defined_stat_block = define_stats(stat)
                if defined_stat_block:
                    return defined_stat_block
            elif not bng_char_id:
                define_stats(stat)
        else:
            return True

    def add_character_equipment(self, character_id: int) -> None:
        character = self.__c_manager.find_character(character_id)
        if character:
            equipped_weapons = character.equipment["weapons"]
            equipped_armor = character.equipment["armor"]
            bng_character_id = character.data["bng_character_id"]
            
            if equipped_weapons:
                for weapon_id in equipped_weapons:
                    self.__e_manager.add_new_weapon(weapon_id, bng_character_id)

            if equipped_armor:
                for armor_id in equipped_armor:
                    self.__e_manager.add_new_armor(armor_id, bng_character_id)

    def delete_stat_block(self, character_id: int, instance_id: int):
        existing_stat_block = self.__control.select_rows("Activity_Stats", ["*"], {"character_id": character_id, "instance_id": instance_id})
        if existing_stat_block:
            delete_result = self.__control.delete_row("Activity_Stats", {"character_id": character_id, "instance_id": instance_id})
            if delete_result:
                for stat in self.__stats_data:
                    if stat.data["character_id"] == character_id and stat.data["instance_id"] == instance_id:
                        self.__stats_data.remove(stat)
                        break
                    
                return existing_stat_block

# def main():
#     connection = SQLConnector("test", 33061)
#     control = DatabaseExecutor(connection)
    
#     player_manager = DatabasePlayerManager(control)
#     char_manager = DatabaseCharacterManager(control)
#     weapon_manager = DatabaseWeaponManager(control)
#     armor_manager = DatabaseArmorManager(control)
#     activity_manager = DatabaseActivityManager(control)
#     instance_manager = DatabaseActivityInstanceManager(control)
#     equipment_manager = EquipmentManager(control, weapon_manager, armor_manager)

#     db_manager = DatabaseManager(control, activity_manager, weapon_manager, char_manager, player_manager, equipment_manager)

#     members = {
#         4611686018441248186: 1,
#         4611686018466583801: 2,
#         4611686018467428939: 3,
#         4611686018467632157: 3,
#         4611686018456510427: 1,
#     }
#     activities = [type.value for type in ACTIVITY_TYPE]

#     for member_id, player_type in members.items():
#         player_manager.add_new_player(member_id, player_type)
#         result = player_manager.get_character_and_player_ids(member_id)
#         character_ids = result[0]
#         player_id = result[1]

#         for char_id in character_ids:
#             char_manager.add_new_character(member_id, player_type, int(char_id), player_id)  # type: ignore
#             db_manager.add_character_equipment(int(char_id))

#         for activity in activities:
#             print(f"{member_id=}")
#             print(f"{player_type=}")
#             print(f"{activity=}")
#             sleep(5)
#             instance_ids = char_manager.get_activity_history(character_ids[0], activity, 5)  # type: ignore
#             print(instance_ids)
#             if instance_ids:
#                 for id in instance_ids:
#                     instance_manager.create_instance(id)
#                     instance_manager.create_instance_stats(id)
            
#             instance_list = instance_manager.get_instances()
#             db_manager.add_new_stat_block(instance_list[-1])
#         sleep(5)
    
#     print("DB population complete!")

# if __name__ == "__main__":
#     main()
    