// src/components/SearchBar.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
// Import both fetchUserData and addUser
import { fetchUserData, addUser } from '../api/d2Api';
import { UserData } from '../types';
import './SearchBar.css'; // Make sure CSS is imported

// Define platform options with values provided by the user
const platformOptions = [
    // Default, non-selectable option
    { value: '', label: '-- Select Platform --', disabled: true },
    // Actual platform options
    { value: 1, label: 'Xbox' },
    { value: 2, label: 'PlayStation' },
    { value: 3, label: 'Steam' },
    { value: 4, label: 'Blizzard' }, // Added Blizzard
];


const SearchBar: React.FC = () => {
    const [username, setUsername] = useState<string>('');
    // Store selected platform value (as string from select)
    const [platform, setPlatform] = useState<string>(''); // Default to empty string for the placeholder option
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [statusMessage, setStatusMessage] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUsername(event.target.value);
    };

    const handlePlatformChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setPlatform(event.target.value);
    };

    // Define the primary search logic separately to allow retrying
    const performSearch = async (userToSearch: string) => {
        const userData: UserData = await fetchUserData(userToSearch);
        setStatusMessage(null); // Clear status message on success
        navigate('/results', { state: { userData } });
    };


    const handleSearch = async (event: React.MouseEvent<HTMLButtonElement> | React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const userToSearch = username.trim();

        // Validate username
        if (!userToSearch) {
            setError("Please enter a Bungie Name.");
            setStatusMessage(null); // Clear any previous status
            return;
        }

        setIsLoading(true);
        setError(null);
        setStatusMessage("Searching for user...");

        try {
            // Initial attempt to fetch the user
            await performSearch(userToSearch);

        } catch (err: unknown) {
            console.error("--- Initial Search Failed ---");
            console.error("Caught error object:", err);

            let errorMessage = "An unknown error occurred during search.";
            let errorCode: number | undefined = undefined;

            if (err instanceof Error) {
                errorMessage = err.message;
                // Access the status code we attached in fetchUserData
                errorCode = (err as any).status;
                console.error("Error details:", { name: err.name, message: err.message, code: errorCode });
            } else if (typeof err === 'string') {
                errorMessage = err;
            }
            // ... (add other checks if needed) ...

            // --- Add User Logic ---
            // Check specifically for 404 status code
            const shouldTryAddingUser = errorCode === 404;

            if (shouldTryAddingUser) {
                // NOW check if platform is selected before trying to add
                if (!platform) {
                    // Keep the 404 error message, but add guidance
                    setError("User not found (404). Please select a platform to add them.");
                    setStatusMessage(null);
                    setIsLoading(false); // Stop loading as we need user input
                    return; // Stop execution
                }

                const platformInt = parseInt(platform, 10); // Convert selected platform string to integer
                // This check is likely redundant due to the select options, but safe to keep
                if (isNaN(platformInt)) {
                     setError("Invalid platform selected.");
                     setStatusMessage(null);
                     setIsLoading(false);
                     return;
                }


                console.log(`User not found (404), attempting to add ${userToSearch} on platform ${platformInt}...`);
                setStatusMessage("User not found, attempting to add to database...");
                try {
                    // Call the addUser function
                    await addUser(userToSearch, platformInt);
                    setStatusMessage("User added successfully! Retrying search...");

                    // Automatically retry the search after successful add
                    await performSearch(userToSearch);
                    // If performSearch succeeds, it navigates. If it fails again, the error will be caught by the outer catch.
                    // Need to ensure the outer catch doesn't try to add *again* if the second search fails with 404.
                    // The current logic handles this ok - it would just show the 404 error message the second time.

                } catch (addError: unknown) {
                    console.error("--- Add User Failed ---");
                    console.error("Caught add error object:", addError);
                    setStatusMessage(null); // Clear status message
                    if (addError instanceof Error) {
                        setError(`Failed to add user: ${addError.message}`);
                    } else {
                        setError("Failed to add user due to an unknown error.");
                    }
                }
            } else {
                // If it wasn't a 404 error, just display the original search error
                 setStatusMessage(null);
                 setError(errorMessage);
            }
             // --- End Add User Logic ---

        } finally {
             // We only want to stop loading if an error occurred that prevents navigation
             // or if the add process failed. If navigation happens, loading state doesn't matter as much.
             // Let's clear loading only if there's a final error message set.
             if (error) { // If an error was set at the end, stop loading
                 setIsLoading(false);
             }
             // If statusMessage is still set (e.g. "Retrying search...") but no error occurred,
             // it implies navigation happened or is about to. Loading state will reset on component unmount/remount.
        }
    };

    return (
        // Wrap in form for semantics and Enter key submission
        <form className="search-container" onSubmit={handleSearch}>
             {/* Platform Selector */}
             <select
                 id="platformSelect"
                 value={platform} // Controlled component
                 onChange={handlePlatformChange}
                 disabled={isLoading}
                 // required // HTML5 validation - useful but check in code is more robust
                 aria-label="Platform"
             >
                 {/* Map over the updated platformOptions array */}
                 {platformOptions.map(opt => (
                     <option key={opt.label} value={opt.value} disabled={opt.disabled}>
                         {opt.label}
                     </option>
                 ))}
             </select>

            {/* Username Input */}
            <input
                type="text"
                id="bngUsernameInput"
                placeholder="Enter Bungie Name (e.g., Player#1234)"
                value={username} // Controlled component
                onChange={handleInputChange}
                disabled={isLoading}
                aria-label="Bungie Name"
                required // HTML5 validation
            />

            {/* Search Button */}
            <button type="submit" disabled={isLoading}>
                {/* Adjust button text based on loading state */}
                {isLoading ? 'Processing...' : 'Search'}
            </button>

            {/* Status/Error Messages */}
            {/* Show status only if not loading and no error */}
            {statusMessage && !isLoading && !error && <div className="status-message">{statusMessage}</div>}
            {/* Show error if present */}
            {error && <div className="error-message">{error}</div>}
        </form>
    );
}

export default SearchBar;

