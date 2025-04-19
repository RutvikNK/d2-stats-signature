// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client'; // Import createRoot from react-dom/client
import App from './App';                // Import your main App component
import './index.css';                  // Optional: Import global styles if you have index.css
import './App.css';                    // Optional: Import App-specific global styles

// 1. Get the root DOM node
// This assumes your public/index.html file has <div id="root"></div>
const rootElement = document.getElementById('root');

// 2. Ensure the root element exists before trying to render
if (rootElement) {
  // 3. Create a React root attached to the DOM element
  const root = ReactDOM.createRoot(rootElement);

  // 4. Render the App component into the root
  // React.StrictMode helps catch potential problems in your components
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  // Log an error if the root element isn't found in index.html
  console.error("Failed to find the root element. Ensure your index.html includes <div id=\"root\"></div>.");
}
