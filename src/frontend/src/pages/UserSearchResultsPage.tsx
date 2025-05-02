import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AccountDetails from '../components/AccountDetails';
import Filters from '../components/Filters';
import GearActivityStats from '../components/StatDisplay';
import { parseCharacterIds}  from '../components/CharacterIdList';
import { fetchGearActivityStats, fetchCharacterDetails } from '../api/d2Api';
import { UserData, StatsData, FilterValues, CharacterDetails } from '../types';
import './UserSearchResultsPage.css';


interface LocationState {
    userData: UserData;
}

const ResultsPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const locationState = location.state as LocationState | null;
    const userData = locationState?.userData;

    // State for activity stats
    const [statsData, setStatsData] = useState<StatsData | null>(null);
    const [isFetchingStats, setIsFetchingStats] = useState<boolean>(false);
    const [statsError, setStatsError] = useState<string | null>(null);

    // --- State for Character Details ---
    const [characterDetailsMap, setCharacterDetailsMap] = useState<Map<string, CharacterDetails>>(new Map());
    const [isFetchingChars, setIsFetchingChars] = useState<boolean>(false);
    const [charError, setCharError] = useState<string | null>(null);

    // Effect to redirect if userData is missing
    useEffect(() => {
        if (!userData) {
            console.warn("No user data found in location state. Redirecting home.");
            navigate('/', { replace: true });
        }
    }, [userData, navigate]);

    // --- Effect to fetch character details when userData is available ---
    useEffect(() => {
        console.log("Character fetch effect triggered. UserData:", !!userData, "PlayerID:", userData?.player_id, "Map size:", characterDetailsMap.size, "Fetching:", isFetchingChars); // Log effect trigger conditions

        if (userData && userData.player_id != null && characterDetailsMap.size === 0 && !isFetchingChars) {
            const fetchAllCharacterDetails = async () => {
                setIsFetchingChars(true);
                setCharError(null);
                const characterIds = parseCharacterIds(userData.character_ids);

                if (characterIds.length === 0) {
                    console.warn("No character IDs found to fetch details for.");
                    setIsFetchingChars(false);
                    return;
                }

                const results = await Promise.allSettled(
                    characterIds.map(bngCharId => fetchCharacterDetails(userData.player_id, bngCharId))
                );

                const detailsMap = new Map<string, CharacterDetails>();
                let fetchErrors: string[] = [];

                results.forEach((result, index) => {
                    const bngCharId = characterIds[index];
                    if (result.status === 'fulfilled') {
                        const detail = result.value;
                        if (detail) {
                            detailsMap.set(bngCharId, detail);
                        }
                    } else {
                        console.error(`[ResultsPage Effect] Failed to fetch details for character ${bngCharId}:`, result.reason);
                        const errorMessage = (result.reason instanceof Error) ? result.reason.message : 'Unknown error';
                        fetchErrors.push(`Char ${bngCharId.substring(0, 6)}...: ${errorMessage}`);
                    }
                });

                setCharacterDetailsMap(detailsMap);
                if (fetchErrors.length > 0) {
                    const errorString = `Errors fetching some character details: ${fetchErrors.join(', ')}`;
                    console.error("[ResultsPage Effect]", errorString); // Log errors
                    setCharError(errorString);
                }
                setIsFetchingChars(false);
            };

            fetchAllCharacterDetails();
        }
    }, [userData, isFetchingChars, characterDetailsMap]);


    // Callback function for the Filters component
    const handleApplyFilters = async (filters: FilterValues) => {
        // ... (handleApplyFilters code remains the same) ...
        if (!userData || userData.player_id == null) { console.error("Cannot apply filters: UserData or Player ID is missing."); setStatsError("Cannot fetch stats: User information is incomplete."); return; }
        console.log("Applying filters received from component:", filters); console.log("Using Player ID:", userData.player_id);
        setIsFetchingStats(true); setStatsError(null); setStatsData(null);
        try { const fetchedStats: StatsData = await fetchGearActivityStats(filters, userData.player_id); setStatsData(fetchedStats); }
        catch (err: unknown) { console.error("Failed to fetch stats:", err); if (err instanceof Error) { setStatsError(err.message); } else { setStatsError("An unknown error occurred while fetching stats."); } }
        finally { setIsFetchingStats(false); }
    };

    if (!userData) {
        return null;
    }
    if (isFetchingChars && characterDetailsMap.size === 0) {
        return <main className="results-main"><p>Loading character details...</p></main>;
    }

    return (
        <main className="results-main">
            <div className="title-section">
                <h2 id="titlePlaceholder">Player Information</h2>
                <h3 id="accountName">{userData.bng_username}</h3>
                <h4 id="gearActivityNamePlaceholder">Gear/Activity Overview</h4>
            </div>
            {charError && <p className="error-message" style={{ textAlign: 'center', marginBottom: '15px' }}>{charError}</p>}
            <div className="content-columns">
                <div className="account-details-column">
                    <h3>ACCOUNT DETAILS</h3>
                    <AccountDetails
                        userData={userData}
                        characterDetails={characterDetailsMap} // Pass map to AccountDetails
                    />
                    <Filters
                        userData={userData}
                        characterDetails={characterDetailsMap} // Pass map to Filters
                        onApplyFilters={handleApplyFilters}
                        isFetchingStats={isFetchingStats}
                    />
                </div>
                <div className="gear-activity-column">
                    <h3>ACTIVITY STATS</h3>
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
