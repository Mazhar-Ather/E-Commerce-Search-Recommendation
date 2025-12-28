// App.jsx
import { useState, useEffect } from "react";
import SearchBox from "./components/SearchBox";
import Trie from "./datastructures/TrieTree";
import "./App.css";
import UI from "./components/UI";

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
  
  // In App.jsx - Update loadProducts function
const loadProducts = async () => {
    try {
        console.log("🔄 Loading products from database...");
        
        const response = await fetch('http://localhost:5000/api/products');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Handle both response formats (debug and simple)
        let productNames;
        if (data.products && Array.isArray(data.products)) {
            // Debug response format
            productNames = data.products;
            console.log("📊 Debug Response:", data.debug);
        } else if (Array.isArray(data)) {
            // Simple array format
            productNames = data;
        } else {
            throw new Error('Unexpected response format from server');
        }
        
        console.log(`📦 Received ${productNames.length} product names for Trie`);
        
        if (!Array.isArray(productNames)) {
            throw new Error('Invalid data received from server');
        }
        
        if (productNames.length === 0) {
            throw new Error('No valid product names found in database');
        }
        
        // Initialize Trie with database products
        const newTrie = new Trie();
        newTrie.loadWords(productNames);
        
        // Verify Trie loaded correctly
        const trieWordCount = newTrie.count();
        console.log(`✅ Trie loaded: ${trieWordCount} words`);
        console.log(`📈 Trie vs Received: ${trieWordCount}/${productNames.length}`);
        
        // Debug: Check if all words were inserted
        if (trieWordCount < productNames.length) {
            console.warn(`⚠️  Trie count (${trieWordCount}) < Received count (${productNames.length})`);
            console.warn("   Possible duplicates or insertion issues");
            
            // Check for duplicates
            const uniqueNames = new Set(productNames);
            console.log(`   Unique names: ${uniqueNames.size}`);
        }
        
        setTrie(newTrie);
        setLoading(false);
        setError(null);
        
    } catch (err) {
        console.error('❌ Error loading products:', err);
        setError(err.message);
        setLoading(false);
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
    alert(`You selected: ${suggestion}`);
  };

  // If loading, show loading state inside UI component
  if (loading) {
    return (
      <UI>
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
      </UI>
    );
  }

  // If error, show error state inside UI component
  if (error) {
    return (
      <UI>
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
      </UI>
    );
  }

  // Main content with search functionality
  return (
    <UI>
      <div className="main-content">
        <div className="search-container">
          <h2 className="search-title">🔍 Search Products</h2>
          <p className="search-description">
            Search through {trie ? trie.count().toLocaleString() : 'thousands of'} products in our database
          </p>
          
          <SearchBox
            onInputChange={handleInputChange}
            suggestions={suggestions}
            onSuggestionSelect={handleSuggestionSelect}
            placeholder="Type product name (e.g., iPhone, Samsung, Laptop...)"
          />
          
          {suggestions.length > 0 && (
            <div className="suggestions-summary">
              <p>Found {suggestions.length} suggestions</p>
            </div>
          )}
        </div>

        {stats && (
          <div className="stats-section">
            <h3>📊 Database Statistics</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📦</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.total_products}</div>
                  <div className="stat-label">Total Products</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.min_price || 'N/A'}</div>
                  <div className="stat-label">Min Price</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">💎</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.max_price || 'N/A'}</div>
                  <div className="stat-label">Max Price</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">🏷️</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.categories || 1}</div>
                  <div className="stat-label">Categories</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {trie && (
          <div className="trie-info">
            <h3>⚡ Trie Search Engine</h3>
            <p>
              Powered by Trie data structure • {trie.count().toLocaleString()} words indexed • Instant prefix search
            </p>
          </div>
        )}
      </div>
    </UI>
  );
}

export default App;