/* Structure of the user data object returned by the /d2/user/{bng_username} API endpoint */
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

/* Structure for the filter values collected from the Filters component */
export interface FilterValues {
    activityType: string;
    activityName: string;
    weaponFilter: string;
    armorFilter: string;
}

/**
 * Placeholder structure for the data expected in the Gear/Activity Stats section.
 * Replace this with the actual structure returned by your stats API endpoint.
 */
export interface StatsData {
    message: string;
    filtersUsed: FilterValues;
    timestamp: string;
    // Add actual stats fields here, e.g., kills: number, efficiency: number, etc.
}

/**
 * Defines the expected structure of the raw API response array.
 */
export type GetUserApiResponse = [UserData, number];

