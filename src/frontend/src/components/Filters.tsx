import React, { useState } from 'react';
import { FilterValues } from '../types'; 
import './Filters.css'; 

interface FiltersProps {
    onApplyFilters: (filters: FilterValues) => void; 
    isFetchingStats: boolean; 
}

const Filters: React.FC<FiltersProps> = ({ onApplyFilters, isFetchingStats }) => {
    // Type the state for each filter input
    const [activityType, setActivityType] = useState<string>('');
    const [activityName, setActivityName] = useState<string>('');
    const [weaponFilter, setWeaponFilter] = useState<string>('');
    const [armorFilter, setArmorFilter] = useState<string>('');

    // Type the event handlers for input changes
    const handleInputChange = (setter: React.Dispatch<React.SetStateAction<string>>) =>
        (event: React.ChangeEvent<HTMLInputElement>) => {
            setter(event.target.value);
        };

    // Handler for the apply button click
    const handleApplyClick = () => {
        // Construct the FilterValues object
        const currentFilters: FilterValues = {
            activityType,
            activityName,
            weaponFilter,
            armorFilter
        };
        // Call the callback function passed from the parent
        onApplyFilters(currentFilters);
    };

    return (
        <div className="filters">
            <h4>Filter Gear/Activity Stats:</h4>

            {/* Activity Type Input */}
            <label htmlFor="activityType">Activity Type:</label>
            <input
                type="text" id="activityType" placeholder="e.g., Raid, Crucible"
                value={activityType}
                onChange={handleInputChange(setActivityType)} // Use generic handler
                disabled={isFetchingStats}
            />

            {/* Activity Name Input */}
            <label htmlFor="activityName">Activity Name:</label>
            <input
                type="text" id="activityName" placeholder="e.g., Vault of Glass, Trials of Osiris"
                value={activityName}
                onChange={handleInputChange(setActivityName)}
                disabled={isFetchingStats}
            />

            {/* Weapon Filter Input */}
            <label htmlFor="weaponFilter">Weapon:</label>
            <input
                type="text" id="weaponFilter" placeholder="e.g., Gjallarhorn, Rose"
                value={weaponFilter}
                onChange={handleInputChange(setWeaponFilter)}
                disabled={isFetchingStats}
            />

            {/* Armor Filter Input */}
            <label htmlFor="armorFilter">Armor:</label>
            <input
                type="text" id="armorFilter" placeholder="e.g., Helmet, Class Item"
                value={armorFilter}
                onChange={handleInputChange(setArmorFilter)}
                disabled={isFetchingStats}
            />

            {/* Apply Button */}
            <button onClick={handleApplyClick} disabled={isFetchingStats}>
                {isFetchingStats ? 'Loading Stats...' : 'Apply Filters'}
            </button>
        </div>
    );
}

export default Filters;
