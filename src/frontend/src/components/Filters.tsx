import React, { useState, useEffect } from 'react';
import { FilterValues, UserData } from '../types'; 
import './Filters.css'; 

interface FiltersProps {
    userData: UserData | null | undefined; 
    onApplyFilters: (filters: FilterValues) => void; 
    isFetchingStats: boolean; // Flag to disable inputs while loading
}

// Helper function to parse character IDs
function parseCharacterIds(idString: string | undefined | null): string[] {
    if (!idString || typeof idString !== 'string') {
        return []; // Return empty array if input is invalid
    }
    try {
        // Replace single quotes with double quotes for valid JSON
        const cleanedString = idString.replace(/'/g, '"');
        const parsed = JSON.parse(cleanedString);
        // Ensure the parsed result is an array of strings
        if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string')) {
            return parsed as string[];
        }
        console.warn("Parsed character IDs is not an array of strings:", parsed);
        return []; // Return empty array if format is wrong
    } catch (e) {
        console.error("Error parsing character IDs:", e, "Input string:", idString);
        return []; // Return empty array on parsing error
    }
}

const activityModeOptions = [
    { value: '', label: '-- Select Activity Type --', disabled: true }, // Placeholder option
    { value: 3, label: 'Strike' },
    { value: 87, label: 'Lost Sector' },
    { value: 69, label: 'Competitive Crucible' },
    { value: 19, label: 'Iron Banner' },
    { value: 84, label: 'Trials of Osiris' },
    { value: 48, label: 'Rumble' },
    { value: 70, label: 'The Crucible' },
    { value: 82, label: 'Dungeon' },
    { value: 4, label: 'Raid' },
];

const Filters: React.FC<FiltersProps> = ({ userData, onApplyFilters, isFetchingStats }) => {
    // State variables for the filter inputs
    const [selectedMode, setSelectedMode] = useState<string>(''); // Store mode ID as string from select
    const [activityName, setActivityName] = useState<string>(''); // Store specific activity name input
    const [selectedCharacterId, setSelectedCharacterId] = useState<string>(''); // Store selected character ID
    const [count, setCount] = useState<string>('25'); // Optional: State for count input if re-enabled

    // State for the character dropdown options
    const [characterOptions, setCharacterOptions] = useState<{ value: string, label: string, disabled?: boolean }[]>([]);

    // Effect hook to parse character IDs and populate dropdown when userData changes
    useEffect(() => {
        if (userData?.character_ids) {
            const ids = parseCharacterIds(userData.character_ids);
            const options = ids.map((id, index) => ({
                value: id,
                label: `Character ${index + 1} (${id.substring(0, 6)}...)`
            }));
            // Set the options, including a default placeholder
            setCharacterOptions([
                { value: '', label: '-- Select Character --', disabled: true },
                ...options
            ]);
        } else {
            setCharacterOptions([{ value: '', label: '-- Select Character --', disabled: true }]);
        }
        setSelectedCharacterId('');
    }, [userData]);

    // Event handler for Activity Type (Mode) dropdown change
    const handleModeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newMode = event.target.value;
        setSelectedMode(newMode);
        // Clear activity name input if a mode is selected (enforce mutual exclusivity)
        if (newMode) {
            setActivityName('');
        }
    };

    // Event handler for Specific Activity Name input change
    const handleActivityNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newName = event.target.value;
        setActivityName(newName);
        // Clear mode selection if an activity name is typed (enforce mutual exclusivity)
        if (newName) {
            setSelectedMode('');
        }
    };

    // Event handler for Character dropdown change
    const handleCharacterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedCharacterId(event.target.value);
    };

    // Handler for the "Apply Filters" button click
    const handleApplyClick = () => {
        // Validation: Ensure a character is selected
        if (!selectedCharacterId) {
             alert("Please select a character.");
             return;
        }

        // Construct the filters object based on current state
        const filters: FilterValues = {
            characterId: selectedCharacterId,
            count: parseInt(count, 10) || 25, // Uncomment and adjust if count input is used
        };

        // Add mode or activityName (only one should be active due to handlers above)
        if (selectedMode) {
            filters.mode = selectedMode; // Pass mode ID (as string or number based on API needs)
        } else if (activityName.trim()) {
            filters.activityName = activityName.trim(); // Pass activity name string
        }

        // Call the callback function passed from the parent (ResultsPage)
        onApplyFilters(filters);
    };

    // Render the filter form elements
    return (
        <div className="filters">
            <h4>Filter Activity Stats:</h4>

            {/* Character Selection Dropdown */}
            <label htmlFor="characterSelect">Character:</label>
            <select
                id="characterSelect"
                value={selectedCharacterId}
                onChange={handleCharacterChange}
                disabled={isFetchingStats || characterOptions.length <= 1} // Disable if loading or no characters
                required // HTML5 validation hint
            >
                {/* Map over character options to create <option> elements */}
                {characterOptions.map(opt => (
                    <option key={opt.value || 'default-char'} value={opt.value} disabled={opt.disabled}>
                        {opt.label}
                    </option>
                ))}
            </select>

            {/* Activity Type (Mode) Dropdown */}
            <label htmlFor="activityTypeSelect">Activity Type (Mode):</label>
            <select
                id="activityTypeSelect"
                value={selectedMode}
                onChange={handleModeChange}
                // Disable if loading stats OR if a specific activity name is entered
                disabled={isFetchingStats || !!activityName}
            >
                 {/* Map over activity mode options */}
                 {activityModeOptions.map(opt => (
                    <option key={opt.label} value={opt.value} disabled={opt.disabled}>
                        {opt.label}
                    </option>
                ))}
            </select>

            {/* Activity Name Input */}
            <label htmlFor="activityName">Specific Activity Name:</label>
            <input
                type="text" id="activityName" placeholder="e.g., Vault of Glass (overrides Type)"
                value={activityName}
                onChange={handleActivityNameChange}
                // Disable if loading stats OR if an activity type (mode) is selected
                disabled={isFetchingStats || !!selectedMode}
            />

            {/* Count Input (Optional - currently commented out) */}
            <label htmlFor="countInput">Number of Activities:</label>
            <input type="number" id="countInput" min="1" max="100" value={count} onChange={(e) => setCount(e.target.value)} disabled={isFetchingStats} placeholder="Default: 25"/>
            {/* Weapon/Armor filters removed as per previous discussion */}

            {/* Apply Button */}
            {/* Disable button if loading OR if no character is selected */}
            <button onClick={handleApplyClick} disabled={isFetchingStats || !selectedCharacterId}>
                {isFetchingStats ? 'Loading Stats...' : 'Apply Filters'}
            </button>
        </div>
    );
}

export default Filters;