from typing import Optional
from time import sleep

from backend.bng_python.bng_api_connector import BungieConnector
from backend.python_mysql.mysql_executor import DatabaseExecutor
from backend.python_mysql.mysql_connector import SQLConnector
from backend.bng_python.bng_data import DataFactory
from backend.bng_python.bng_types import *
from backend.bng_python.bng_data import (
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

BNG_CONN = BungieConnector("10E792629C2A47E19356B8A79EEFA640")

class DatabasePlayerManager:
    def __init__(self, db_control: DatabaseExecutor) -> None:
        self.__control: DatabaseExecutor = db_control
        self.__players: list[PlayerData] = []
    
    def read_data(self) -> None:
        db_data = self.__control.retrieve_all("`Player`")
        
        if db_data:
            for tuple in db_data:
                self.add_existing_player(tuple)

    def add_existing_player(self, data) -> None:
        player = PlayerData(BNG_CONN, tuple[1], PLATFORM[tuple[6]].value) # type: ignore
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

        character_ids = str(result[0][0].replace("[", ""))  # type: ignore
        character_ids = character_ids.replace("]", "")
        character_ids = character_ids.replace("\'", "")
        character_ids = character_ids.split(", ")
        for i in range(len(character_ids)):
            character_ids[i] = int(character_ids[i])  # type: ignore

        return character_ids, result[0][1] # type: ignore
