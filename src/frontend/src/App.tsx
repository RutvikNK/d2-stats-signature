import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/UserSearchResultsPage';
import './App.css';

const App: React.FC = () => {
    return (
        <Router>
            <div className="app-container">
                {/* Header appears on all pages */}
                <Header />
                {/* Define application routes */}
                <Routes>
                    {/* Route for the home page */}
                    <Route path="/" element={<HomePage />} />
                    {/* Route for the results page */}
                    <Route path="/results" element={<ResultsPage />} />
                </Routes>
            </div>
        </Router>
    );
}

// function App() {
//   return (
//     <div style={{ padding: '20px' }}>
//       <h1>Hello World! Does this render?</h1>
//       <p>If you see this, the basic React rendering is working.</p>
//     </div>
//   );
// }


export default App;
