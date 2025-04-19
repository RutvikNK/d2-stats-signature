import React, { useState } from "react";
import "./SearchBar.css"

const SearchBar: React.FC = () => {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const apiUrl = "https://d2-sandbox-api-424001620434.us-central1.run.app/d2"

    const handleSearch = async () => {
        if (!query.trim()) return;

        setLoading(true);
        try {
            console.log(`${apiUrl}/user/${encodeURIComponent(query)}`)
            const response = await fetch(
                `${apiUrl}/user/${encodeURIComponent(query)}`
            );
            const data = await response.json();
            setResults(data)
        } catch (err) {
            console.error("Search Error: ", err);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            handleSearch()
        }
    };
    
    return (
        <>
            <div>
                <input 
                    type='text'
                    className='search-input'
                    placeholder='Search by Bungie Username'
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button className='search-button' onClick={handleSearch}>
                    {loading ? "Searching..." : "Search"}
                </button>
            </div>
            <div>
                {results && (
                    <pre>
                        {JSON.stringify(results, null, 2)}
                    </pre>
                )}
            </div>
        </>
    )
}

export default SearchBar