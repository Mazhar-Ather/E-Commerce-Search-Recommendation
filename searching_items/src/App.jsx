// App.jsx
import { useState, useEffect } from "react";
import SearchBox from "./components/SearchBox";
import Trie from "./datastructures/TrieTree";
import "./App.css";

function App() {
  const [suggestions, setSuggestions] = useState([]);
  const [trie, setTrie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  // Load product names from database on component mount
  useEffect(() => {
    loadProducts();
    loadStats();
  }, []);
  
  const loadProducts = async () => {
    try {
      console.log("🔄 Loading products from database...");
      
      const response = await fetch('http://localhost:5000/api/products');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const productNames = await response.json();
      
      if (!Array.isArray(productNames)) {
        throw new Error('Invalid data received from server');
      }
      
      if (productNames.length === 0) {
        throw new Error('No products found in database. Please run the scraper first.');
      }
      
      // Initialize Trie with database products
      const newTrie = new Trie();
      newTrie.loadWords(productNames);
      
      setTrie(newTrie);
      setLoading(false);
      setError(null);
      console.log(`✅ Loaded ${productNames.length} products into Trie`);
      
    } catch (err) {
      console.error('Error loading products:', err);
      setError(err.message);
      setLoading(false);
      
      // Show error message instead of fallback sample data
      setTrie(null);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setRetryCount(prev => prev + 1);
    loadProducts();
  };

  const handleInputChange = (value) => {
    if (!value || !trie) {
      setSuggestions([]);
      return;
    }

    const result = trie.getSuggestions(value, 8); // Get max 8 suggestions
    setSuggestions(result);
  };

  const handleSuggestionSelect = (suggestion) => {
    console.log("Selected:", suggestion);
    // You can implement navigation or detailed search here
    alert(`You selected: ${suggestion}`);
  };

  if (loading) {
    return (
      <div className="app-container loading">
        <div className="loader">
          <div className="spinner"></div>
          <p>Loading products from database...</p>
          <p className="loading-text">Please ensure:</p>
          <ul className="loading-checklist">
            <li>✅ MySQL server is running</li>
            <li>✅ Python scraper has populated the database</li>
            <li>✅ Backend server is running on port 5000</li>
          </ul>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-container error">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h2>Failed to Load Products</h2>
          <p className="error-message">{error}</p>
          
          <div className="troubleshooting">
            <h4>🔧 Troubleshooting Steps:</h4>
            <ol>
              <li>Start MySQL server</li>
              <li>Run your Python scraper to populate data</li>
              <li>Start backend server: <code>node server.js</code></li>
              <li>Check if API is accessible: <a href="http://localhost:5000/api/products" target="_blank" rel="noopener noreferrer">http://localhost:5000/api/products</a></li>
            </ol>
          </div>
          
          <button onClick={handleRetry} className="retry-button">
            🔄 Retry Loading
          </button>
          
          <div className="database-info">
            <h4>📊 Database Connection Info:</h4>
            <p>Host: localhost</p>
            <p>Database: ecommerce</p>
            <p>Table: daraz_products</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📱 Smartphone Search</h1>
        <p className="subtitle">
          Search through {trie ? trie.count().toLocaleString() : 'thousands of'} smartphone products
        </p>
        {stats && (
          <div className="header-stats">
            <span className="stat-badge">📊 {stats.total_products} Products</span>
            <span className="stat-badge">💰 {stats.min_price} - {stats.max_price}</span>
            {stats.last_updated && (
              <span className="stat-badge">🕒 Updated: {stats.last_updated}</span>
            )}
          </div>
        )}
      </header>

      <main className="app-main">
        <div className="search-container">
          <SearchBox
            onInputChange={handleInputChange}
            suggestions={suggestions}
            onSuggestionSelect={handleSuggestionSelect}
            placeholder="Search smartphones (e.g., iPhone, Samsung, Pixel...)"
          />
          
          {stats && (
            <div className="stats-container">
              <div className="stat-item">
                <span className="stat-label">Total Products:</span>
                <span className="stat-value">{stats.total_products}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Price Range:</span>
                <span className="stat-value">₹{stats.min_price} - ₹{stats.max_price}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Categories:</span>
                <span className="stat-value">{stats.categories || 1}</span>
              </div>
            </div>
          )}
        </div>

        <div className="instructions">
          <h3>💡 How to use:</h3>
          <ul>
            <li>Start typing to see instant suggestions</li>
            <li>Click on a suggestion to autocomplete</li>
            <li>Press Enter to search</li>
            <li>All data is loaded from MySQL database</li>
          </ul>
          
          {trie && (
            <div className="trie-info">
              <p><strong>Trie Stats:</strong> {trie.count()} words loaded • Memory efficient search</p>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by Trie Data Structure • Connected to MySQL Database</p>
        <p className="tech-stack">
          React • Node.js • MySQL • Trie Algorithm • 
          <span className="data-source">Data Source: Daraz.pk Smartphones</span>
        </p>
      </footer>
    </div>
  );
}

export default App;