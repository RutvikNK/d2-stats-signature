import React from 'react';

interface CharacterIdListProps {
    idString: string | undefined | null;
}

/**
 * Parses the character ID string (e.g., "['id1', 'id2']") into an array of strings.
 * Returns an empty array on failure or invalid input.
 */
function parseCharacterIds(idString: string | undefined | null): string[] {
    if (!idString || typeof idString !== 'string') {
        return []; // Return empty array for invalid input
    }
    try {
        // Clean up the string (replace single quotes) and parse as JSON
        const cleanedString = idString.replace(/'/g, '"');
        const parsed = JSON.parse(cleanedString);
        // Ensure the parsed result is an array of strings
        if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string')) {
            return parsed as string[];
        }
        console.warn("Parsed character IDs is not an array of strings:", parsed);
        return []; // Return empty if format is wrong after parsing
    } catch (e) {
        console.error("Error parsing character IDs:", e, "Input string:", idString);
        return []; // Return empty array on parsing error
    }
}

const CharacterIdList: React.FC<CharacterIdListProps> = ({ idString }) => {
    const ids = parseCharacterIds(idString);

    if (ids.length === 0) {
        // Provide clearer feedback based on whether input was provided
        return <li>{idString === undefined || idString === null || idString === '' ? 'No character IDs provided.' : 'Could not parse character IDs.'}</li>;
    }

    return (
        <>
            {/* Render list items using parsed IDs */}
            {ids.map(id => <li key={id}>{id}</li>)}
        </>
    );
}

export default CharacterIdList;
