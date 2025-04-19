import uvicorn
import psutil
import os
from fastapi import FastAPI, Response, status
from time import sleep
from fastapi.middleware.cors import CORSMiddleware

from backend.data.bng_data import ActivityStatsData
from backend.data.bng_types import ACTIVITY_TYPE
from backend.load.connector import SQLConnector
from backend.load.managers import (
    DatabasePlayerManager,
    DatabaseCharacterManager,
    DatabaseWeaponManager,
    DatabaseArmorManager,
    EquipmentManager,
    DatabaseActivityInstanceManager,
    DatabaseActivityManager,
    DatabaseManager
)
from backend.load.executor import DatabaseExecutor

host = os.environ.get("DB_HOST", "d2-stats")
port = int(os.environ.get("DB_PORT", 3306))
unix_socket = f"/cloudsql/{os.environ.get('CLOUDSQL_CONNECTION_NAME', '/destiny2-sandbox-tracker-api:us-central1:d2-sandbox-cloudsql')}"
db_conn = SQLConnector("signature", port, host=host, unix=unix_socket)
db_exec = DatabaseExecutor(db_conn)

activities = [type.value for type in ACTIVITY_TYPE]

player_manager = DatabasePlayerManager(db_exec)
weapon_manager = DatabaseWeaponManager(db_exec)
armor_manager = DatabaseArmorManager(db_exec)
instance_manager = DatabaseActivityInstanceManager(db_exec)
activity_manager = DatabaseActivityManager(db_exec)
character_manager = DatabaseCharacterManager(db_exec)
equip_manager = EquipmentManager(db_exec, weapon_manager, armor_manager)

db_manager = DatabaseManager(db_exec, activity_manager, weapon_manager, character_manager, player_manager, equip_manager)

player_cols = [
    "player_id", 
    "destiny_id", 
    "bng_id", 
    "bng_username", 
    "date_created", 
    "date_last_played", 
    "platform", 
    "character_ids"
]
weapon_cols = [
    "weapon_id", 
    "ammo_type", 
    "bng_weapon_id", 
    "damage_type", 
    "weapon_name", 
    "weapon_type", 
    "slot", 
    "rarity"
]
armor_cols = [
    "armor_id", 
    "bng_armor_id", 
    "armor_name", 
    "slot", 
    "rarity"
]
activity_stats_cols = [
    "character_id", 
    "activity_id", 
    "instance_id", 
    "activity_name", 
    "weapon_id", 
    "weapon_name", 
    "kills", 
    "precision_kills", 
    "precision_kills_percent", 
    "character_class"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def convert_to_dict(cols: list, result):
    if len(cols) == len(result):
        resp: dict = {}
        for i, col in enumerate(cols):
            resp[col] = result[i]
        
        return resp
    else:
        return None
    
def get_character_ids(destiny_id: int):
    query = f"SELECT character_id FROM `Character` WHERE player_id = {destiny_id}"
    result = db_conn.execute(query)
    if result:
        for i in range(len(result)):
            result[i] = result[i][0]
        
        return result
    else:
        return None

def get_activity_ids_by_mode(mode: str):
    query = f"SELECT activity_id FROM `Activity` WHERE type = {mode}"
    result = db_conn.execute(query)
    if result and not isinstance(result, bool):
        for i in range(len(result)):
            result[i] = result[i][0]
        
        return result
    else:
        return None

def get_mult_activity_stats(char_id, act_id=0):
    mult_resp = []
    if act_id:
        query = f"SELECT * FROM `Activity_Stats` WHERE character_id = {char_id} AND activity_id = {act_id}"
    else:
        query = f"SELECT * FROM `Activity_Stats` WHERE character_id = {char_id}"
    
    result = db_conn.execute(query)
    if result:
        for item in result:
            single_resp = convert_to_dict(activity_stats_cols, item)
            if single_resp:
                mult_resp.append(single_resp)

    return mult_resp

def verify_platform(platform: int):
    if platform > 0 and platform <= 4:
        return True
    else:
        return False

def verify_bng_username(username: str) -> bool:
    try:
        split_username = username.split("#")
        if len(split_username[1]) > 4:
            return False
        else:
            username_code = int(split_username[1])
    except ValueError:
        return False
    except IndexError:
        return False
    
    return True

def verify_date_format(date: str) -> bool:
    try:
        split_date = date.split("-")
        if len(split_date) != 3:
            return False
        else:
            if len(split_date[0]) != 4 and len(split_date[1]) != 2 and len(split_date[2]) != 2:
                return False
            
            for i in range(3):
                int(split_date[i])
            
            if int(split_date[1]) > 12 or int(split_date[2]) > 31:
                return False

    except ValueError:
        return False
    
    return True

@app.get("/d2/user/{player_id}")
async def get_user_by_id(player_id: int):
    query = f"SELECT * FROM `Player` WHERE player_id = {player_id}"
    result = db_conn.execute(query)
    if result:
        resp = convert_to_dict(player_cols, result[0])
        if resp:
            return resp, 200
        else:
            return {"Error": "Error parsing player data"}, 500
    
    return {"Error": "Player not found"}, 404

@app.post("/d2/user")
async def post_new_user(username: str, platform: int):
    if verify_platform(platform) and verify_bng_username(username):
        new_player = player_manager.add_player_by_username(username, platform)
        if new_player:
            member_id = new_player.data["destiny_id"]
            result = player_manager.get_character_and_player_ids(member_id)
            character_ids = result[0]
            player_id = result[1]

            if character_ids:
                for char_id in character_ids:
                    try:
                        character_manager.add_new_character(member_id, platform, int(char_id), player_id)  # type: ignore
                        db_manager.add_character_equipment(int(char_id))

                        for activity in activities:
                            print(f"{member_id=}")
                            print(f"{platform=}")
                            print(f"{activity=}")
                            sleep(5)
                            instance_ids = character_manager.get_activity_history(char_id, activity, 5)  # type: ignore
                            print(instance_ids)
                            if instance_ids:
                                for id in instance_ids:
                                    instance_manager.create_instance(id)
                                    instance_manager.create_instance_stats(id)
                            
                            instance_list = instance_manager.get_instances()
                            db_manager.add_new_stat_block(instance_list[-1], int(char_id))
                        
                        return new_player.data, 201
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                return {"Error": f"Could not find character IDs for {username}"}
        else:
            return {"Error": f"Could not POST new player {username} with account on platform {platform}"}

@app.patch("/d2/user/{member_id}")
async def patch_user_last_played(member_id: int, platform: int, response: Response):
    if verify_platform(platform):
        result = player_manager.update_date_last_played(member_id, platform)
        if result:
            response.status_code = status.HTTP_200_OK
            return result.data, 200
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"Player {member_id} not found"}, 404
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Error": f"Invalid platform {platform} requested"}, 400

@app.get("/d2/weapon/{weapon_id}")
async def get_weapon_by_id(weapon_id: int):
    query = f"SELECT * FROM `Weapon` WHERE weapon_id = {weapon_id}"
    result = db_conn.execute(query)
    if result:
        resp = convert_to_dict(weapon_cols, result[0])
        if resp:
            return resp, 200
        else:
            return {"Error": "Error parsing weapon data"}, 500
    
    return {"Error": "Weapon not found"}, 404

@app.post("/d2/weapon/")
async def post_weapon(weapon_id: int):
    new_weapon = weapon_manager.add_new_weapon(weapon_id)
    if new_weapon:
        return new_weapon.data, 201
    else:
        return {"Error": f"Error posting new weapon {weapon_id}"}, 500

@app.put("/d2/weapon/{weapon_id}")
async def put_weapon(weapon_id: int, response: Response):
    update_result = weapon_manager.update_weapon(weapon_id)
    if update_result:
        response.status_code = status.HTTP_200_OK
        return update_result, 200
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": f"Weapon {weapon_id} not found"}, 404

@app.get("/d2/armor/{armor_id}")
async def get_armor_by_id(armor_id: int):
    query = f"SELECT * FROM `Armor` WHERE armor_id = {armor_id}"
    result = db_conn.execute(query)
    if result:
        resp = convert_to_dict(armor_cols, result[0])
        if resp:
            return resp, 200
        else:
            return {"Error": "Error parsing armor data"}, 500
    
    return {"Error": "Armor not found"}, 404

@app.post("/d2/armor/")
async def post_armor(armor_id: int):
    new_armor = armor_manager.add_new_armor(armor_id)
    if new_armor:
        return new_armor.data, 201
    else:
        return {"Error": f"Error posting new armor {armor_id}"}, 500

@app.put("/d2/armor/{armor_id}")
async def put_armor(armor_id: int, response: Response):
    update_result = armor_manager.update_armor(armor_id)
    if update_result:
        response.status_code = status.HTTP_200_OK
        return update_result, 200
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": f"Armor {armor_id} not found"}, 404

@app.get("/d2/user/activity_stats/{destiny_id}/")
async def get_activity_stats_by_id(destiny_id: int, activity_id: int=0, character_id: int=0, mode: str="", count: int=0):
    if mode and activity_id:
        return {"Error": "Incompatible filters requested"}, 400
    
    mult_activity_ids = []
    mult_character_ids = []

    if character_id == 0:
        mult_character_ids = get_character_ids(destiny_id)
        if not mult_character_ids:
            return {"Error": f"No characters found for the given user {destiny_id}"}, 404

    if activity_id == 0 and mode:
        mult_activity_ids = get_activity_ids_by_mode(mode)
        if not mult_activity_ids:
            return {"Error": f"No matching activities found for the given mode {mode}"}, 404

    if mult_character_ids:
        mult_resp = []
        for char_id in mult_character_ids:
            if mult_activity_ids:
                for act_id in mult_activity_ids:
                    act_resps = get_mult_activity_stats(char_id, act_id)
                    for single_resp in act_resps:
                        mult_resp.append(single_resp)
            elif activity_id:
                act_resps = get_mult_activity_stats(char_id, activity_id)
                for single_resp in act_resps:
                    mult_resp.append(single_resp)
            else:
                act_resps = get_mult_activity_stats(char_id)
                for single_resp in act_resps:
                    mult_resp.append(single_resp)
        
        if count > 0  and mult_resp:
            return mult_resp[:count], 200
        elif mult_resp:
            return mult_resp, 200
    elif character_id:
        mult_resp = []
        if mult_activity_ids:
            for act_id in mult_activity_ids:
                query = f"SELECT * FROM `Activity_Stats` WHERE character_id = {character_id} AND activity_id = {act_id}"
                result = db_conn.execute(query)
                if result and not isinstance(result, bool):
                    for item in result:
                        single_resp = convert_to_dict(activity_stats_cols, item)
                        if single_resp:
                            mult_resp.append(single_resp)
            else:
                if count > 0  and mult_resp:
                    return mult_resp[:count], 200
                elif mult_resp:
                    return mult_resp, 200
        elif activity_id:
            query = f"SELECT * FROM `Activity_Stats` WHERE character_id = {character_id} AND activity_id = {activity_id}"
            result = db_conn.execute(query)
            if result and not isinstance(result, bool):
                for item in result:
                    single_resp = convert_to_dict(activity_stats_cols, item)
                    if single_resp:
                        return single_resp, 200
        else:
            act_resps = get_mult_activity_stats(character_id)
            for single_resp in act_resps:
                mult_resp.append(single_resp)
            if count > 0 and mult_resp:
                return mult_resp[:count], 200
            elif mult_resp:
                return mult_resp, 200
    else:
        return {"Error": "Account characters not found"}, 404
    
    return "Activity stats not found", 404

@app.post("/d2/user/activity_stats")
async def post_activity_stats(character_id: int, instance_id: int, response: Response):
    instance_data = instance_manager.create_instance(instance_id)
    instance_data.create_stats()
    stat = db_manager.add_new_stat_block(instance_data, character_id)
    
    if isinstance(stat, ActivityStatsData):
        response.status_code = status.HTTP_201_CREATED
        return stat.data, stat.participant, 201
    elif not stat:
        response.status_code = status.HTTP_409_CONFLICT
        return {"Error": f"Activity instance {instance_id} already logged"}, 409

@app.delete("/d2/user/activity_stats")
async def delete_activity_stats(character_id: int, instance_id: int, response: Response):
    delete_result = db_manager.delete_stat_block(character_id, instance_id)
    if delete_result and isinstance(delete_result, list):
        delete_result = convert_to_dict(activity_stats_cols, delete_result[0])
        response.status_code = status.HTTP_200_OK
        return delete_result, 200
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": f"Activity instance {instance_id} for character {character_id} not found"}, 404

@app.get("/memory")
async def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "available": memory.available,
        "used": memory.used,
        "free": memory.free,
        "percent": memory.percent
    }

if __name__ == "__main__":
    # for debugging
    uvicorn.run(app, host="0.0.0.0", port=8080)
