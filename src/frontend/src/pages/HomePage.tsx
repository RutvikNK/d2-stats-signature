import React from 'react';
import SearchBar from '../components/SearchBar';
import './HomePage.css';

const HomePage: React.FC = () => {
    return (
        <main className="home-main">
            <h1>Destiny 2 Sandbox Tracker</h1>
            <SearchBar />
        </main>
    );
}

export default HomePage;

