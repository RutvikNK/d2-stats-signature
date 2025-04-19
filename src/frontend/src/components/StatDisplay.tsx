import React, { JSX } from 'react';
import { StatsData } from '../types'; 
import './StatDisplay.css'; 

interface GearActivityStatsProps {
    statsData: StatsData | null; 
    isLoading: boolean;
    error: string | null;
}

const GearActivityStats: React.FC<GearActivityStatsProps> = ({ statsData, isLoading, error }) => {
    let content: JSX.Element; // Type the content variable

    if (isLoading) {
        content = <p>Loading stats...</p>;
    } else if (error) {
        // Display error message if loading failed
        content = <p className="error-message">Error loading stats: {error}</p>;
    } else if (statsData) {
        // Render the actual stats data when available
        // Customize this based on your actual StatsData structure
        content = (
            <div>
                <h4>Stats Loaded</h4>
                {/* Example: Displaying the simulated data */}
                <pre>{JSON.stringify(statsData, null, 2)}</pre>
            </div>
        );
    } else {
        // Initial placeholder state before filters are applied or if no data found
        content = (
            <>
                <p>Apply filters to load gear and activity stats.</p>
                {/* Placeholder visual */}
                <div className="placeholder-box" aria-hidden="true"></div>
            </>
        );
    }

    return (
        <div id="gearActivityStats" className="stats-container">
            {content}
        </div>
    );
}

export default GearActivityStats;
