// src/components/Filters.tsx
import React, { useState, useEffect } from 'react';
// Import CharacterDetails type as well
import { FilterValues, UserData, CharacterDetails } from '../types';
import './Filters.css';

// Define props interface including the new characterDetails map
interface FiltersProps {
    userData: UserData | null | undefined; // Still needed for initial ID parsing? Maybe not.
    characterDetails: Map<string, CharacterDetails>; // Map of BungieCharacterID -> Details
    onApplyFilters: (filters: FilterValues) => void;
    isFetchingStats: boolean;
}

// Define Activity Mode options
const activityModeOptions = [
    { value: '', label: '-- Select Activity Type --', disabled: true },
    { value: 3, label: 'Strike' }, { value: 87, label: 'Lost Sector' }, { value: 69, label: 'Competitive Crucible' },
    { value: 19, label: 'Iron Banner' }, { value: 84, label: 'Trials of Osiris' }, { value: 48, label: 'Rumble' },
    { value: 70, label: 'Quickplay Crucible' }, { value: 82, label: 'Dungeon' }, { value: 4, label: 'Raid' },
];

// Define type for dropdown options
type SelectOption = { value: string; label: string; disabled?: boolean };

const Filters: React.FC<FiltersProps> = ({ characterDetails, onApplyFilters, isFetchingStats }) => {
    // State for filter inputs
    const [selectedModeValue, setSelectedModeValue] = useState<string>(''); // Stores the numeric value of the mode
    const [activityName, setActivityName] = useState<string>('');
    const [selectedCharacterId, setSelectedCharacterId] = useState<string>(''); // Stores the Bungie Character ID

    // State for character dropdown options - now derived from props
    const [characterOptions, setCharacterOptions] = useState<SelectOption[]>([]);

    useEffect(() => {
        const options: SelectOption[] = [{ value: '', label: '-- Select Character --', disabled: true }];
        if (characterDetails && characterDetails.size > 0) {
            // Iterate over the map entries [bngCharacterId, details]
            characterDetails.forEach((details, bngCharId) => {
                options.push({
                    value: bngCharId, // The value submitted is the Bungie Character ID
                    label: details.class ? details.class.charAt(0).toUpperCase() + details.class.slice(1).toLowerCase() : `Character (${bngCharId.substring(0,6)}...)` // Fallback label
                });
            });
        }

        setCharacterOptions(options);
        // Reset selection if the available options change (e.g., new search results)
        // Only reset if the currently selected ID is no longer valid
        if (selectedCharacterId && !characterDetails.has(selectedCharacterId)) {
             setSelectedCharacterId('');
        }
    // Dependencies: run when the details map changes
    }, [characterDetails, selectedCharacterId]); // Added selectedCharacterId dependency for reset logic


    // Event handlers remain largely the same
    const handleModeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newModeValue = event.target.value;
        setSelectedModeValue(newModeValue);
        if (newModeValue) { setActivityName(''); }
    };
    const handleActivityNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newName = event.target.value;
        setActivityName(newName);
        if (newName) { setSelectedModeValue(''); }
    };
    const handleCharacterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedCharacterId(event.target.value); // Store the Bungie Character ID
    };

    // Handler for the "Apply Filters" button click
    const handleApplyClick = () => {
        if (!selectedCharacterId) {
             alert("Please select a character."); return;
        }
        // Construct filters using the selected Bungie Character ID
        const filters: FilterValues = { characterId: selectedCharacterId };
        if (selectedModeValue) {
            const selectedOption = activityModeOptions.find(opt => opt.value.toString() === selectedModeValue);
            if (selectedOption) { filters.mode = selectedOption.label; } // Send label
            else { console.warn(`Could not find label for mode value: ${selectedModeValue}`); }
        } else if (activityName.trim()) {
            filters.activityName = activityName.trim();
        }
        onApplyFilters(filters);
    };

    return (
        <div className="filters">
            <h4>Filter Activity Stats:</h4>
            {/* Character Selection Dropdown - now uses derived options */}
            <label htmlFor="characterSelect">Character:</label>
            <select
                id="characterSelect"
                value={selectedCharacterId} // Value is the Bungie Character ID
                onChange={handleCharacterChange}
                disabled={isFetchingStats || characterOptions.length <= 1}
                required
            >
                {characterOptions.map(opt => (
                    <option key={opt.value || 'default-char'} value={opt.value} disabled={opt.disabled}>
                        {opt.label} {/* Label now shows class name */}
                    </option>
                ))}
            </select>

            {/* Activity Type (Mode) Dropdown */}
            <label htmlFor="activityTypeSelect">Activity Type (Mode):</label>
            <select id="activityTypeSelect" value={selectedModeValue} onChange={handleModeChange} disabled={isFetchingStats || !!activityName}>
                 {activityModeOptions.map(opt => ( <option key={opt.label} value={opt.value} disabled={opt.disabled}> {opt.label} </option> ))}
            </select>

            {/* Activity Name Input */}
            <label htmlFor="activityName">Specific Activity Name:</label>
            <input type="text" id="activityName" placeholder="e.g., Vault of Glass (overrides Type)" value={activityName} onChange={handleActivityNameChange} disabled={isFetchingStats || !!selectedModeValue} />

            {/* Apply Button */}
            <button onClick={handleApplyClick} disabled={isFetchingStats || !selectedCharacterId}>
                {isFetchingStats ? 'Loading Stats...' : 'Apply Filters'}
            </button>
        </div>
    );
}

export default Filters;
