import { UserData, FilterValues, StatsData } from '../types'; // Import types

// Base URL for the user endpoint
const API_BASE_URL = import.meta.env.VITE_D2_SANDBOX_API_URL;
// Define the POST endpoint (Using the same base URL as confirmed)
const ADD_USER_ENDPOINT = `${API_BASE_URL}/user`;

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
 * Requires Bungie Name and Platform ID.
 * @param {string} bngUsername - The Bungie Name to add.
 * @param {number} platform - The integer platform ID.
 * @returns {Promise<void>} - Resolves on success, throws an error on failure.
 * @throws {Error} - Throws an error if the POST request fails.
 */
export async function addUser(bngUsername: string, platform: number): Promise<void> {
    const apiUrl = ADD_USER_ENDPOINT; // Using same base URL for POST
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


// --- Placeholder for future API calls ---
/**
 * Fetches gear/activity stats based on filters and user info.
 * (This is a placeholder and needs implementation based on your other API endpoints)
 *
 * @param {FilterValues} filters - Object containing filter values (activityType, etc.)
 * @param {object} userInfo - Basic user info (like destiny_id, character_ids_string)
 * @returns {Promise<StatsData>} - A promise that resolves with the stats data.
 */
export async function fetchGearActivityStats(
    filters: FilterValues,
    userInfo: { destiny_id?: number; character_ids_string?: string } // Type the user info needed
): Promise<StatsData> { // Return type is StatsData
    console.log("Fetching stats with filters:", filters, "and user info:", userInfo);

    // Replace with your actual API call logic using fetch()
    // Example simulation:
    return new Promise((resolve) => {
        setTimeout(() => {
            // Construct a StatsData object
            const simulatedStats: StatsData = {
                message: "Stats data loaded (simulated)",
                filtersUsed: filters,
                timestamp: new Date().toISOString(), // Use ISO string for consistency
                // Add actual stats fields here based on your StatsData interface
            };
            resolve(simulatedStats);
        }, 1500); // Simulate network delay
    });
}
