import React from 'react';
import { parseCharacterIds}  from './CharacterIdList';
import { UserData, CharacterDetails } from '../types'; 
import './AccountDetails.css'; 

interface AccountDetailsProps {
    userData: UserData | null | undefined;
    characterDetails: Map<string, CharacterDetails>
}

// Helper function to format date strings
const formatDate = (dateString: string | undefined | null): string => {
    if (!dateString) return 'N/A';
    try {
        // Use Intl for better date formatting options
        return new Intl.DateTimeFormat(undefined, { // Use user's locale
            year: 'numeric', month: 'long', day: 'numeric'
        }).format(new Date(dateString));
    } catch (e) {
        console.warn("Could not format date:", dateString, e);
        return dateString; // Fallback to original string on error
    }
};

// Helper function to format class name nicely (e.g., "WARLOCK" -> "Warlock")
const formatClassName = (className: string | undefined | null): string => {
    if (!className) return 'N/A'; // Handle null or undefined class names
    // Capitalize first letter, lowercase the rest
    return className.charAt(0).toUpperCase() + className.slice(1).toLowerCase();
}

const AccountDetails: React.FC<AccountDetailsProps> = ({ userData, characterDetails }) => {
    // Show loading state if primary user data isn't available yet
    if (!userData) {
        return <div className="account-details-content"><p>Loading account details...</p></div>;
    }

    // Parse the Bungie character IDs from the userData string
    // These IDs are used to look up the details in the characterDetails map
    const bngCharacterIds = parseCharacterIds(userData.character_ids);
    return (
        <div className="account-details-content">
            {/* Display basic user information */}
            <p><strong>Platform:</strong> <span>{userData.platform || 'N/A'}</span></p>
            <p><strong>Date Created:</strong> <span>{formatDate(userData.date_created)}</span></p>
            <p><strong>Last Played:</strong> <span>{formatDate(userData.date_last_played)}</span></p>

            {/* --- UPDATED: Display Character Classes --- */}
            <p><strong>Characters:</strong></p>
            {/* Use a standard list to display character classes */}
            <ul className="character-class-list">
                {bngCharacterIds.length > 0 ? (
                    // Map over the IDs obtained from the initial user data
                    bngCharacterIds.map(bngId => {
                        // Look up the details for this ID in the map passed via props
                        const details = characterDetails.get(bngId);
                        // Display the formatted class name if details were found,
                        // otherwise show a fallback indicating loading or missing data
                        return (
                            <li key={bngId}>
                                {details ? formatClassName(details.class) : `ID: ${bngId} (Loading...)`}
                                {/* Optionally display other fetched details */}
                                {/* {details?.light_level && ` - ${details.light_level} Light`} */}
                            </li>
                        );
                    })
                ) : (
                    // Display message if no character IDs were found in user data
                    <li>No characters found.</li>
                )}
            </ul>
            {/* --- End UPDATED --- */}

            {/* Display Bungie ID */}
            {/* <p><strong>Bungie ID:</strong> <span>{userData.bng_id ?? 'N/A'}</span></p> */}
            {/* Player ID and Destiny ID were removed in previous steps */}
        </div>
    );
}

export default AccountDetails;
