// src/pages/ResultsPage.tsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; // React Router hooks for navigation and location state
import AccountDetails from '../components/AccountDetails'; // Component to display basic user info
import Filters from '../components/Filters'; // Component for filter inputs
import GearActivityStats from '../components/StatDisplay'; // Component to display stats results
import { fetchGearActivityStats } from '../api/d2Api'; // API function to fetch activity stats
// Import necessary types from the types definition file
import { UserData, StatsData, FilterValues } from '../types';
import './UserSearchResultsPage.css'; // Stylesheet for the results page

// Define the expected structure of the state passed via navigation from SearchBar
interface LocationState {
    userData: UserData;
}

const ResultsPage: React.FC = () => {
    // React Router hooks
    const location = useLocation(); // Access location state
    const navigate = useNavigate(); // Function to navigate programmatically

    // Get userData passed from the SearchBar component via navigation state
    // Use type assertion carefully or add runtime checks if state might be missing/malformed
    const locationState = location.state as LocationState | null;
    const userData = locationState?.userData; // Extract the user data object

    // State variables for the activity stats section
    const [statsData, setStatsData] = useState<StatsData | null>(null); // Holds the fetched stats array or null
    const [isFetchingStats, setIsFetchingStats] = useState<boolean>(false); // Loading indicator flag
    const [statsError, setStatsError] = useState<string | null>(null); // Holds error messages if fetching stats fails

    // Effect hook to redirect to home page if userData is missing
    // This prevents accessing the /results route directly without a prior successful search
    useEffect(() => {
        if (!userData) {
            console.warn("No user data found in location state. Redirecting home.");
            // Navigate back to home page, replacing the current history entry
            navigate('/', { replace: true });
        }
        // Dependency array: this effect runs when userData or navigate changes
    }, [userData, navigate]);

    // Callback function passed to the Filters component
    // This function is triggered when the "Apply Filters" button is clicked in Filters.tsx
    const handleApplyFilters = async (filters: FilterValues) => {
        // --- Ensure userData and player_id are available before proceeding ---
        // Although the useEffect above should redirect, this provides an extra safety check
        if (!userData || userData.player_id == null) { // Check specifically for player_id presence
            console.error("Cannot apply filters: UserData or Player ID is missing.");
            // Optionally set an error message for the user
            setStatsError("Cannot fetch stats: User information is incomplete.");
            return; // Stop execution if necessary data is missing
        }

        console.log("Applying filters received from component:", filters);
        // --- Log the player ID being used for the API call ---
        console.log("Using Player ID:", userData.player_id);

        // Set loading state and clear previous results/errors
        setIsFetchingStats(true);
        setStatsError(null);
        setStatsData(null);

        try {
            // --- Call the API function with the filters object AND the player_id ---
            const fetchedStats: StatsData = await fetchGearActivityStats(filters, userData.player_id);
            // Update state with the fetched stats data on success
            setStatsData(fetchedStats);
        } catch (err: unknown) { // Catch potential errors from the API call
            console.error("Failed to fetch stats:", err);
            // Set error message based on the caught error type
            if (err instanceof Error) {
                setStatsError(err.message);
            } else {
                 setStatsError("An unknown error occurred while fetching stats.");
            }
        } finally {
            // Always set loading state back to false after API call completes (success or error)
            setIsFetchingStats(false);
        }
    };

    // Prevent rendering the page content if userData is missing (e.g., during redirect)
    if (!userData) {
        return null; // Render nothing while redirecting or if data is truly missing
    }

    // Render the main content of the results page
    return (
        <main className="results-main">
            {/* Top title section displaying basic info */}
            <div className="title-section">
                <h2 id="titlePlaceholder">Player Information</h2>
                {/* Display the Bungie username */}
                <h3 id="accountName">{userData.bng_username}</h3>
                <h4 id="gearActivityNamePlaceholder">Gear/Activity Overview</h4>
            </div>

            {/* Main content area with two columns */}
            <div className="content-columns">
                {/* Left Column: Account Details and Filters */}
                <div className="account-details-column">
                    <h3>ACCOUNT DETAILS</h3>
                    {/* Render the AccountDetails component, passing the fetched user data */}
                    <AccountDetails userData={userData} />
                    {/* Render the Filters component */}
                    {/* Pass userData (needed for character ID parsing), the callback function, and loading state */}
                    <Filters
                        userData={userData}
                        onApplyFilters={handleApplyFilters}
                        isFetchingStats={isFetchingStats}
                    />
                </div>

                {/* Right Column: Activity Stats Display */}
                <div className="gear-activity-column">
                    <h3>ACTIVITY STATS</h3> {/* Updated heading */}
                    {/* Render the GearActivityStats component */}
                    {/* Pass the fetched stats data, loading state, and error state */}
                    <GearActivityStats
                        statsData={statsData}
                        isLoading={isFetchingStats}
                        error={statsError}
                    />
                </div>
            </div>
        </main>
    );
}

export default ResultsPage;
