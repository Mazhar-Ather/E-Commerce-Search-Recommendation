// components/UI.jsx
import React from 'react';
import './UI.css'; // Optional: Create this file for UI-specific styles

// UI component is just a layout wrapper - it doesn't contain app logic
const UI = ({ children, className = '' }) => {
  return (
    <div className={`app-background ${className}`}>
      <div className="app-container">
        {/* Static Header - Doesn't change based on app state */}
        <header className="app-header">
          <h1>📱 Product Search System</h1>
          <p className="subtitle">
            Fast and efficient product search using Trie data structure
          </p>
          
          <div className="header-features">
            <span className="feature-badge">⚡ Instant Search</span>
            <span className="feature-badge">📊 Live Database</span>
            <span className="feature-badge">🔍 Smart Suggestions</span>
          </div>
        </header>

        {/* Main Content Area - This is where children (your app content) goes */}
        <main className="app-main">
          <div className="content-area">
            {children}
          </div>
        </main>

        {/* Sidebar (Optional) */}
        <aside className="app-sidebar">
          <div className="sidebar-section">
            <h3>🎯 Search Tips</h3>
            <ul className="tips-list">
              <li>Type at least 2 characters for suggestions</li>
              <li>Click suggestions to autocomplete</li>
              <li>Press Enter for detailed search</li>
            </ul>
          </div>
          
          <div className="sidebar-section">
            <h3>📈 Technology Stack</h3>
            <div className="tech-stack">
              <span className="tech-tag">React</span>
              <span className="tech-tag">Trie Algorithm</span>
              <span className="tech-tag">MySQL</span>
              <span className="tech-tag">Node.js</span>
              <span className="tech-tag">Express</span>
            </div>
          </div>
        </aside>

        {/* Footer */}
        <footer className="app-footer">
          <div className="footer-content">
            <div className="footer-section">
              <h4>Product Search</h4>
              <p>DSA Final Project - 3rd Semester</p>
            </div>
            <div className="footer-section">
              <h4>Database</h4>
              <p>Real-time MySQL Integration</p>
            </div>
            <div className="footer-section">
              <h4>Algorithm</h4>
              <p>Trie-based Prefix Search</p>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2024 Product Search System. Data sourced from Daraz.pk</p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default UI;