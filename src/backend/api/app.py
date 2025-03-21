from fastapi import FastAPI

from backend.load.connector import SQLConnector

db_conn = SQLConnector("signature", 33061)
app = FastAPI()

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
    "weeapon_id", 
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

def convert_to_dict(cols: list[str], result):
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
    if result:
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
async def post_user(username: str):
    pass

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
    pass

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
    pass

@app.get("/d2/user/activity_stats/{destiny_id}/")
async def get_activity_stats_by_id(destiny_id: int, activity_id: int=0, character_id: int=0, mode: str="", count: int=0):
    if mode and activity_id:
        return {"Error": "Incompatible filters requested"}, 400
    
    mult_activity_ids = []
    mult_character_ids = []

    if character_id == 0:
        mult_character_ids = get_character_ids(destiny_id)

    if activity_id == 0 and mode:
        mult_activity_ids = get_activity_ids_by_mode(mode)

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
                if result:
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
            if result:
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

@app.post("/d2/user/activity")
async def post_activity_stats(char_id: int, instance_id: int):
    pass