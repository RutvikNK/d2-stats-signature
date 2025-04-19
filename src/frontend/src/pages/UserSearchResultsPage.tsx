import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AccountDetails from '../components/AccountDetails';
import Filters from '../components/Filters';
import GearActivityStats from '../components/StatDisplay';
import { fetchGearActivityStats } from '../api/d2Api';
import { UserData, StatsData, FilterValues } from '../types'; 
import './UserSearchResultsPage.css'; 

// Define the expected shape of the location state
interface LocationState {
    userData: UserData;
}

const ResultsPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();

    // Use a type assertion for location.state, be cautious or add checks
    const locationState = location.state as LocationState | null;
    const userData = locationState?.userData;

    // State for the stats section, explicitly typed
    const [statsData, setStatsData] = useState<StatsData | null>(null);
    const [isFetchingStats, setIsFetchingStats] = useState<boolean>(false);
    const [statsError, setStatsError] = useState<string | null>(null);

    // Effect to redirect if navigated directly without userData
    useEffect(() => {
        if (!userData) {
            console.warn("No user data found in location state. Redirecting home.");
            // Redirect back to the home page if userData is missing
            navigate('/', { replace: true }); // Use replace to avoid adding to history
        }
    }, [userData, navigate]);

    // Callback function for the Filters component, typed parameter
    const handleApplyFilters = async (filters: FilterValues) => {
        if (!userData) {
            console.error("Cannot apply filters: UserData is missing.");
            return;
        }

        setIsFetchingStats(true);
        setStatsError(null);
        setStatsData(null); // Clear previous stats

        try {
            // Pass filters and potentially needed user IDs to the API call
            const fetchedStats: StatsData = await fetchGearActivityStats(filters, {
                destiny_id: userData.destiny_id,
                character_ids_string: userData.character_ids // Pass necessary info
            });
            setStatsData(fetchedStats);
        } catch (err: unknown) { // Catch unknown error type
            console.error("Failed to fetch stats:", err);
            if (err instanceof Error) {
                setStatsError(err.message);
            } else {
                 setStatsError("An unknown error occurred while fetching stats.");
            }
        } finally {
            setIsFetchingStats(false);
        }
    };

    // Avoid rendering if userData is not yet available (e.g., during redirect)
    // Render null or a loading indicator
    if (!userData) {
        return null;
    }

    // Render the main content once userData is confirmed
    return (
        <main className="results-main">
            {/* Title Section */}
            <div className="title-section">
                <h2 id="titlePlaceholder">Player Information</h2>
                {/* Display Bungie Name from userData */}
                <h3 id="accountName">{userData.bng_username}</h3>
                <h4 id="gearActivityNamePlaceholder">Gear/Activity Overview</h4>
            </div>

            {/* Content Columns */}
            <div className="content-columns">
                {/* Left Column: Account Details and Filters */}
                <div className="account-details-column">
                    <h3>ACCOUNT DETAILS</h3>
                    {/* Pass userData to AccountDetails component */}
                    <AccountDetails userData={userData} />
                    {/* Pass callback and loading state to Filters component */}
                    <Filters onApplyFilters={handleApplyFilters} isFetchingStats={isFetchingStats} />
                </div>

                {/* Right Column: Gear/Activity Stats */}
                <div className="gear-activity-column">
                    <h3>GEAR/ACTIVITY STATS</h3>
                    {/* Pass stats data, loading state, and error state to GearActivityStats */}
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
