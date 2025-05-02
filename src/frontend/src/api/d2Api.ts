import { UserData, FilterValues, StatsData, ActivityStatsApiResponse, CharacterDetails, CharacterDetailsApiResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_D2_SANDBOX_API_URL;

if (!API_BASE_URL) {
    console.error("CRITICAL ERROR: VITE_API_BASE_URL environment variable is not set!");
}

const USER_ENDPOINT_BASE = `${API_BASE_URL?.replace(/\/$/, '')}/user`;
const ADD_USER_ENDPOINT = USER_ENDPOINT_BASE; // Same URL as GET user
const ACTIVITY_STATS_ENDPOINT = `${USER_ENDPOINT_BASE}/activity_stats`; // GET /user/activity_stats/{player_id}?params
const CHARACTER_DETAIL_ENDPOINT = `${USER_ENDPOINT_BASE}/character` // // GET /user/character/{player_id}/{bng_character_id}

/**
 * Fetches user data from the API based on Bungie Name.
 * @param {string} bngUsername - The Bungie Name (e.g., Player#1234)
 * @returns {Promise<UserData>} - A promise that resolves with the user data object.
 * @throws {Error} - Throws an error if the fetch fails (non-2xx status) or parsing fails. Includes status code if possible.
 */
export async function fetchUserData(bngUsername: string): Promise<UserData> {
    const encodedUsername = encodeURIComponent(bngUsername);
    const apiUrl = `${API_BASE_URL}/user/${encodedUsername}`;
    console.log("Calling GET API:", apiUrl);

    const response = await fetch(apiUrl, { method: 'GET' }); // Specify GET

    if (!response.ok) {
        let errorData: { message?: string } = {};
        let errorMessage = `HTTP error! Status: ${response.status}`; // Default message
        try {
            errorData = await response.json();
            // Use API's message if available, include status code for context
            errorMessage = errorData.message ? `${errorData.message} (Status: ${response.status})` : errorMessage;
        } catch (e) {
            errorMessage = response.statusText ? `${response.statusText} (Status: ${response.status})` : errorMessage;
        }
        console.error("API Error Response:", errorData);
        // Throw an error that includes the status code if possible
        const error = new Error(errorMessage);
        (error as any).status = response.status; // Attach status code to error object
        throw error;
    }

    try {
        const userData: UserData = await response.json(); // Expecting the UserData object directly
        console.log("API Success Response (Parsed UserData):", userData);

        if (typeof userData === 'object' && userData !== null && 'bng_username' in userData) {
             return userData; // Return the parsed user data object
        } else {
             console.error("Parsed data is not the expected UserData object:", userData);
             throw new Error("Parsed data format is unexpected.");
        }

    } catch (parseError: unknown) {
        console.error("Failed to parse successful API response:", parseError);
        const message = (parseError instanceof Error) ? parseError.message : "Unknown parse error";
        throw new Error(`Failed to parse API response: ${message}`);
    }
}

/**
 * Attempts to add a new user via a POST request.
 * Requires Bungie Username and Platform ID.
 * @param {string} bngUsername - The Bungie Name to add.
 * @param {number} platform - The integer platform ID.
 * @returns {Promise<void>} - Resolves on success, throws an error on failure.
 * @throws {Error} - Throws an error if the POST request fails.
 */
export async function addUser(bngUsername: string, platform: number): Promise<void> {
    // Construct URL with Query Parameters
    const params = new URLSearchParams();
    params.append('username', bngUsername);
    params.append('platform', platform.toString()); 

    // Append parameters to the base POST endpoint URL
    const apiUrl = `${ADD_USER_ENDPOINT}?${params}`;
    console.log("Calling POST API with Query Params:", apiUrl);

    // Perform the POST request
    const response = await fetch(apiUrl, {
        method: 'POST',
    });

    // Check if the POST request was successful
    if (!response.ok) {
         let errorData: { message?: string } = {};
         let errorMessage = `Failed to add user. Status: ${response.status}`;
         try {
             // Try to parse error response from API
             errorData = await response.json();
             errorMessage = errorData.message || errorMessage;
         } catch (e) {
            // Fallback if error response isn't JSON
            errorMessage = response.statusText ? `${response.statusText} (Status: ${response.status})` : errorMessage;
         }
         console.error("Add User API Error:", errorData);
         // Throw an error to be caught by the calling function (in SearchBar.tsx)
         throw new Error(errorMessage);
    }

    // If POST is successful, log it and return (resolving the promise)
    console.log("User added successfully via POST:", bngUsername, "Platform:", platform);
}

/**
 * Fetches details for a specific character.
 * Expects API response format: [ CharacterDetails, status_code ]
 * GET /user/character/{player_id}/{bng_character_id}
 */
export async function fetchCharacterDetails(playerId: number, bngCharacterId: string): Promise<CharacterDetails> { // Return CharacterDetails object
    if (!CHARACTER_DETAIL_ENDPOINT) {
        throw new Error("Character Detail API Endpoint is not configured.");
    }
    if (playerId == null || bngCharacterId == null) {
        throw new Error("Player ID and Bungie Character ID are required.");
    }

    const apiUrl = `${CHARACTER_DETAIL_ENDPOINT}/${playerId}/${bngCharacterId}`;
    console.log("Calling GET Character Detail API:", apiUrl);

    const response = await fetch(apiUrl);

    if (!response.ok) {
        // Handle HTTP errors
        let errorData: { message?: string } = {};
        let errorMessage = `Failed to fetch character details for ${bngCharacterId}. Status: ${response.status}`;
        try { 
            errorData = await response.json(); 
            errorMessage = errorData.message || errorMessage; 
        } catch (e) { 
            errorMessage = response.statusText ? `${response.statusText} (Status: ${response.status})` : errorMessage; 
        }
        console.error("Fetch Character Detail API Error:", errorData);
        throw new Error(errorMessage);
    }

    // Handle successful HTTP response
    try {
        // Parse the JSON, expecting the [ char_details_object, status_code ] structure
        const apiResponse: unknown = await response.json();

        // Type Guard to check the structure
        const isCharDetailsApiResponse = (d: unknown): d is CharacterDetailsApiResponse => {
            return (
                Array.isArray(d) &&
                d.length === 2 &&
                typeof d[0] === 'object' && d[0] !== null && 'class' in d[0] && // Check for 'class' property
                typeof d[1] === 'number' // Check status code type
            );
        };

        if (isCharDetailsApiResponse(apiResponse)) {
            const [charDetails, statusCode] = apiResponse; // Destructure

            if (statusCode >= 200 && statusCode < 300) {
                // Ensure the object has the expected 'class' property before returning
                if ('class' in charDetails) {
                    // Add bng_character_id if API doesn't return it, useful for mapping later
                    if (!charDetails.bng_character_id) {
                         charDetails.bng_character_id = bngCharacterId;
                    }
                    return charDetails; // Return the inner CharacterDetails object
                } else {
                     console.error("Character details object missing 'class' property:", charDetails);
                     throw new Error("Unexpected format for character details object.");
                }
            } else {
                // Handle error status code within the response body
                console.error(`API returned status code ${statusCode} in character details response body.`);
                const errorMessage = (charDetails as any)?.message || `API returned status ${statusCode}`;
                throw new Error(errorMessage);
            }
        } else {
            // If the parsed JSON doesn't match the expected structure
            console.error("Parsed character details data is not the expected [data, statusCode] array structure:", apiResponse);
            throw new Error("Unexpected API response format for character details.");
        }

    } catch (parseError: unknown) {
        // Handle errors during JSON parsing
        console.error(`Failed to parse character details response for ${bngCharacterId}:`, parseError);
        const message = (parseError instanceof Error) ? parseError.message : "Unknown parse error";
        throw new Error(`Failed to parse character details response: ${message}`);
    }
}

/**
 * Fetches activity stats based on selected filters and player ID.
 */
export async function fetchGearActivityStats(filters: FilterValues, playerId: number): Promise<StatsData> { // Return type is still StatsData (ActivityStatEntry[])
    if (!ACTIVITY_STATS_ENDPOINT) {
        throw new Error("Activity Stats API Endpoint is not configured.");
    }
    if (!filters.characterId) {
        throw new Error("Character ID is required to fetch activity stats.");
    }
    if (playerId == null) {
        throw new Error("Player ID is required to fetch activity stats.");
    }

    const params = new URLSearchParams();
    params.append('character_id', filters.characterId);
    if (filters.mode) { params.append('mode', filters.mode); } // Send string label
    else if (filters.activityName) { params.append('activity_name', filters.activityName); }
    const count = filters.count || 25;
    params.append('count', count.toString());

    const apiUrl = `${ACTIVITY_STATS_ENDPOINT}/${playerId}?${params.toString()}`;
    console.log("Calling GET Activity Stats API:", apiUrl);

    const response = await fetch(apiUrl);

    if (!response.ok) {
        // Handle HTTP errors (non-2xx status codes)
        let errorData: { message?: string } = {};
        let errorMessage = `Failed to fetch activity stats. Status: ${response.status}`;
        try { errorData = await response.json(); errorMessage = errorData.message || errorMessage; } catch (e) { errorMessage = response.statusText ? `${response.statusText} (Status: ${response.status})` : errorMessage; }
        console.error("Fetch Activity Stats API Error:", errorData);
        throw new Error(errorMessage);
    }

    // Handle successful HTTP response (2xx)
    try {
        // Parse the JSON, expecting the [ data_array, status_code ] structure
        const apiResponse: unknown = await response.json();

        // --- Type Guard to check the structure ---
        const isStatsApiResponse = (d: unknown): d is ActivityStatsApiResponse => {
            return (
                Array.isArray(d) &&
                d.length === 2 &&
                Array.isArray(d[0]) && // Check if first element is an array
                typeof d[1] === 'number' // Check if second element is a number (status code)
            );
        };

        if (isStatsApiResponse(apiResponse)) {
            const [statsArray, statusCode] = apiResponse; // Destructure the validated response

            // Optionally check the status code within the response body if needed
            if (statusCode >= 200 && statusCode < 300) {
                 // Validate the inner array elements (optional but good practice)
                 if (statsArray.every(item => typeof item === 'object' && item !== null && 'activity_name' in item)) {
                    return statsArray as StatsData; // Return the inner array containing stats objects
                 } else {
                     console.error("Inner array elements do not match expected ActivityStatEntry structure.");
                     throw new Error("Unexpected structure within stats data array.");
                 }
            } else {
                // Handle cases where API returns 2xx HTTP status but error code in body
                console.error(`API returned status code ${statusCode} in response body.`);
                // Try to get an error message from the first element if it's not the stats array
                const errorMessage = (statsArray as any)?.message || `API returned status ${statusCode}`;
                throw new Error(errorMessage);
            }
        } else {
            // If the parsed JSON doesn't match the expected [ data_array, status_code ] structure
            console.error("Parsed activity stats data is not the expected [data, statusCode] array structure:", apiResponse);
            throw new Error("Unexpected API response format for activity stats.");
        }

    } catch (parseError: unknown) {
        // Handle errors during JSON parsing itself
        console.error("Failed to parse successful activity stats response:", parseError);
        const message = (parseError instanceof Error) ? parseError.message : "Unknown parse error";
        throw new Error(`Failed to parse activity stats response: ${message}`);
    }
}
