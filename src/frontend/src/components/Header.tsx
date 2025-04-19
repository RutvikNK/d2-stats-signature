import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css'; // Assuming you have Header.css

const Header: React.FC = () => {
    return (
        <header className="shared-header">
            <Link to="/" className="logo">D2</Link>
            <nav>
                {/* Placeholder buttons - replace with actual navigation */}
                <button disabled>Option 1</button>
                <button disabled>Option 2</button>
                <button disabled>Option 3</button>
                <button disabled>Option 4</button>
            </nav>
            <div className="search-bar-header">
                {/* Placeholder search bar in header */}
                <input type="text" placeholder="Search..." disabled />
                <button disabled>SEARCH</button>
            </div>
        </header>
    );
}

export default Header;
