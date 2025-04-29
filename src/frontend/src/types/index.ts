export interface UserData {
    player_id: number;
    destiny_id: number; 
    bng_id: number;
    bng_username: string;
    date_created: string; 
    date_last_played: string; 
    platform: string;
    character_ids: string; // String representation of a list of strings
}

export interface UserData {
    player_id: number; // Keep for potential future use, even if not displayed
    destiny_id: number; // Keep for potential future use
    bng_id: number;
    bng_username: string;
    date_created: string;
    date_last_played: string;
    platform: string;
    character_ids: string; // String representation of a list of strings
}

export interface FilterValues {
    mode?: string; 
    activityName?: string; 
    characterId?: string; // Selected character ID (string from parsed list
    count?: number; // Optional count
}

export interface ActivityStatEntry {
    character_id: number; 
    activity_id: number; 
    instance_id: number; 
    activity_name: string;
    weapon_id: number;
    weapon_name: string;
    kills: number;
    precision_kills: number;
    precision_kills_percent: number;
    character_class: string;
}

export type StatsData = ActivityStatEntry[];
export type GetUserApiResponse = [UserData, number];

