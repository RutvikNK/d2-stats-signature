import { UserData, FilterValues, StatsData } from '../types'; // Import types

// Base URL for the user endpoint
const API_BASE_URL = import.meta.env.VITE_D2_SANDBOX_API_URL;
const USER_ENDPOINT_BASE = `${API_BASE_URL?.replace(/\/$/, '')}/user`;
const ADD_USER_ENDPOINT = `${USER_ENDPOINT_BASE}/`; // Same URL as GET
const ACTIVITY_STATS_ENDPOINT = `${USER_ENDPOINT_BASE}/activity_stats`; // GET /user/activity_stats


/**
 * Fetches user data from the API based on Bungie Name.
 * Assumes the API returns the UserData object directly on success (2xx status).
 * @param {string} bngUsername - The Bungie Name (e.g., Player#1234)
 * @returns {Promise<UserData>} - A promise that resolves with the user data object.
 * @throws {Error} - Throws an error if the fetch fails (non-2xx status) or parsing fails. Includes status code if possible.
 */
export async function fetchUserData(bngUsername: string): Promise<UserData> {
    const encodedUsername = encodeURIComponent(bngUsername);
    // Use GET method for fetching
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

        // Optional: Add a simple check for a key property to be more certain
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
    const apiUrl = ADD_USER_ENDPOINT;
    console.log("Calling POST API:", apiUrl, "for user:", bngUsername, "platform:", platform);

    // Construct the request body including platform
    const requestBody = JSON.stringify({
        bng_username: bngUsername,
        platform: platform // Include platform integer
    });

    // Perform the POST request
    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Add other headers like Authorization if required by your API
        },
        body: requestBody,
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
    // return; // Implicitly returns Promise<void>
}


/**
 * Fetches activity stats based on selected filters.
 * GET /user/activity_stats?character_id=...&mode=...&count=... (or &activity_id=...)
 * @param {FilterValues} filters - Object containing filter values like characterId, mode, activityName.
 * @returns {Promise<StatsData>} - A promise resolving with an array of activity stat entries (StatsData).
 * @throws {Error} - Throws on network error, non-2xx status, parse error, or missing required filters.
 */
export async function fetchGearActivityStats(filters: FilterValues, playerId: number): Promise<StatsData> {
    if (!ACTIVITY_STATS_ENDPOINT) {
        throw new Error("Activity Stats API Endpoint is not configured.");
    }
    // Ensure the required characterId filter is present
    if (!filters.characterId) {
        throw new Error("Character ID is required to fetch activity stats.");
    }

    // --- Construct Query Parameters ---
    const params = new URLSearchParams();

    // Add character_id (mandatory)
    params.append('character_id', filters.characterId);

    // Add mode OR activity_id (mutually exclusive as handled by Filters component)
    if (filters.mode) {
        params.append('mode', filters.mode.toString()); // Ensure mode is sent as a string
    } else if (filters.activityName) {
        // Send the activity name; backend is expected to convert it to an ID
        params.append('activity_id', filters.activityName);
    }

    // Add count (optional, using a default value if not provided in filters)
    const count = filters.count || 25; // Default to 25 entries if not specified
    params.append('count', count.toString());

    // Construct the full API URL with query parameters
    const apiUrl = `${ACTIVITY_STATS_ENDPOINT}/${playerId}/?${params.toString()}`;
    console.log("Calling GET Activity Stats API:", apiUrl);

    // --- Make the API Request ---
    const response = await fetch(apiUrl); // Default method is GET

    // Handle non-successful HTTP responses
    if (!response.ok) {
        let errorData: { message?: string } = {};
        let errorMessage = `Failed to fetch activity stats. Status: ${response.status}`;
        try {
            errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
        } catch (e) {
             errorMessage = response.statusText ? `${response.statusText} (Status: ${response.status})` : errorMessage;
        }
        console.error("Fetch Activity Stats API Error:", errorData);
        throw new Error(errorMessage); // Throw error to be caught by the caller
    }

    // Handle successful response
    try {
        // Parse the response body, expecting an array of ActivityStatEntry objects (StatsData)
        const statsData: StatsData = await response.json();
        console.log("Activity Stats API Success Response (Parsed):", statsData);

        // Optional but recommended: Validate the structure of the parsed data
        if (!Array.isArray(statsData)) {
            console.error("Parsed activity stats data is not an array:", statsData);
            throw new Error("Unexpected format for activity stats data.");
            // You could add more detailed validation here if needed (e.g., check properties of first item)
        }

        return statsData; // Return the successfully parsed array of stats
    } catch (parseError: unknown) { // Handle errors during JSON parsing
        console.error("Failed to parse successful activity stats response:", parseError);
        const message = (parseError instanceof Error) ? parseError.message : "Unknown parse error";
        throw new Error(`Failed to parse activity stats response: ${message}`);
    }
}
