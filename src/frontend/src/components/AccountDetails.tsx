import React from 'react';
import CharacterIdList from './CharacterIdList';
import { UserData } from '../types'; 
import './AccountDetails.css'; 

interface AccountDetailsProps {
    userData: UserData | null | undefined;
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

const AccountDetails: React.FC<AccountDetailsProps> = ({ userData }) => {
    // Handle loading/null state
    if (!userData) {
        return <div className="account-details-content"><p>Loading account details...</p></div>;
    }

    return (
        <div className="account-details-content">
            <p><strong>Platform:</strong> <span>{userData.platform || 'N/A'}</span></p>
            <p><strong>Date Created:</strong> <span>{formatDate(userData.date_created)}</span></p>
            <p><strong>Last Played:</strong> <span>{formatDate(userData.date_last_played)}</span></p>

            {/* Character IDs Section */}
            <p><strong>Character IDs:</strong></p>
            <ul className="character-id-list">
                {/* Pass the character_ids string to the specialized component */}
                <CharacterIdList idString={userData.character_ids} />
            </ul>

            {/* Optional: Display other IDs */}
            {/* <p><strong>Player ID:</strong> <span>{userData.player_id ?? 'N/A'}</span></p> */}
            <p><strong>Destiny ID:</strong> <span>{userData.destiny_id?.toString() ?? 'N/A'}</span></p> {/* Handle large number */}
            {/* <p><strong>Bungie ID:</strong> <span>{userData.bng_id ?? 'N/A'}</span></p> */}
        </div>
    );
}

export default AccountDetails;
