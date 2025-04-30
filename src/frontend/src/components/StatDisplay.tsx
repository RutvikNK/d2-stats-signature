import React, { JSX } from 'react';
import { StatsData, ActivityStatEntry } from '../types';
import './StatDisplay.css'; 

interface GearActivityStatsProps {
    statsData: StatsData | null; 
    isLoading: boolean;
    error: string | null;
}

// Optional: Helper component for rendering a single table row.
// This can make the main component's render logic cleaner.
const StatEntryRow: React.FC<{ entry: ActivityStatEntry }> = ({ entry }) => {
    // Use nullish coalescing (??) to provide 'N/A' for potentially missing data points
    return (
        <tr>
            <td>{entry.activity_name ?? 'N/A'}</td>
            <td>{entry.weapon_name ?? 'N/A'}</td>
            <td style={{ textAlign: 'center' }}>{entry.kills ?? 'N/A'}</td>
            <td style={{ textAlign: 'center' }}>{entry.precision_kills ?? 'N/A'}</td>
            <td style={{ textAlign: 'center' }}>
                {/* Format percentage nicely, handle null/undefined */}
                {entry.precision_kills_percent != null ? `${entry.precision_kills_percent.toFixed(1)}%` : 'N/A'}
            </td>
            <td>{entry.character_class ?? 'N/A'}</td>
            {/* Example: Add instance_id if useful for debugging or linking */}
            {/* <td title={entry.instance_id?.toString()}>{entry.instance_id ? entry.instance_id.toString().slice(-6) : 'N/A'}</td> */}
        </tr>
    );
};

// The main component to display the stats section
const GearActivityStats: React.FC<GearActivityStatsProps> = ({ statsData, isLoading, error }) => {
    let content: JSX.Element; // Variable to hold the JSX content to be rendered

    // --- Conditional Rendering Logic ---

    // 1. Show loading indicator if fetching data
    if (isLoading) {
        content = <p>Loading activity stats...</p>;
    }
    // 2. Show error message if an error occurred
    else if (error) {
        content = <p className="error-message">Error loading stats: {error}</p>;
    }
    // 3. Show the stats table if data exists and is not empty
    else if (statsData && statsData.length > 0) {
        content = (
            // Container allows horizontal scrolling on small screens if table is wide
            <div className="stats-table-container">
                <table>
                    <thead>
                        <tr>
                            {/* Define table headers */}
                            <th>Activity</th>
                            <th>Weapon Used</th>
                            <th>Kills</th>
                            <th>Precision Kills</th>
                            <th>Precision %</th>
                            <th>Class</th>
                            {/* Add more headers matching StatEntryRow if needed */}
                        </tr>
                    </thead>
                    <tbody>
                        {/* Map over the statsData array to render a row for each entry */}
                        {statsData.map((entry, index) => (
                            // Use a unique key for each row. instance_id is ideal if unique per request.
                            // Fallback to index if instance_id might not be present or unique.
                            <StatEntryRow key={entry.instance_id || `stat-entry-${index}`} entry={entry} />
                        ))}
                    </tbody>
                </table>
            </div>
        );
    }
    // 4. Show a message if data fetching was successful but returned an empty array
    else if (statsData && statsData.length === 0) {
        content = <p>No activity stats found for the selected filters.</p>;
    }
    // 5. Show the initial placeholder message before any filters are applied
    else {
        content = (
            <>
                <p>Apply filters to load activity stats.</p>
                {/* Placeholder visual (can be styled with CSS) */}
                <div className="placeholder-box" aria-hidden="true"></div>
            </>
        );
    }

    // Render the container div with the determined content
    return (
        <div id="gearActivityStats" className="stats-container">
            {content}
        </div>
    );
}

export default GearActivityStats;
