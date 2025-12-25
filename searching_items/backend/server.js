const express = require("express");
const cors = require("cors");
const mysql = require("mysql2");

const app = express();

// IMPORTANT: Allow all CORS origins for development
app.use(cors({
    origin: '*',  // Allow all origins
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type']
}));
app.use(express.json());

// MySQL connection
const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "mazhar334",
    database: "ecommerce"
});

db.connect((err) => {
    if (err) {
        console.error("❌ MySQL connection error:", err.message);
        return;
    }
    console.log("✅ Connected to MySQL database!");
});

// Test endpoint
app.get("/", (req, res) => {
    res.json({ 
        message: "Product Search API is running!",
        endpoints: {
            getAllProducts: "GET /api/products",
            search: "GET /api/products/search?q=iphone",
            health: "GET /api/health"
        }
    });
});

// Get ALL product names
app.get("/api/products", (req, res) => {
    console.log("📡 GET /api/products called");
    
    const sql = "SELECT product_name FROM daraz_products LIMIT 100"; // Limit for testing
    
    db.query(sql, (err, results) => {
        if (err) {
            console.error("❌ Database query error:", err.message);
            return res.status(500).json({ 
                error: "Database error", 
                details: err.message 
            });
        }
        
        console.log(`✅ Found ${results.length} products`);
        
        // Return simple array of product names
        const productNames = results
            .map(row => row.product_name)
            .filter(name => name && name.trim() !== "");
        
        res.json(productNames);
    });
});

// Health check endpoint
app.get("/api/health", (req, res) => {
    db.query("SELECT 1", (err) => {
        if (err) {
            return res.status(500).json({ 
                status: "ERROR", 
                database: "Disconnected",
                message: err.message 
            });
        }
        res.json({ 
            status: "OK", 
            database: "Connected",
            timestamp: new Date().toISOString(),
            message: "Backend API is working"
        });
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {  // Listen on all interfaces
    console.log(`🚀 Server running on:`);
    console.log(`   http://localhost:${PORT}`);
    console.log(`   http://127.0.0.1:${PORT}`);
    console.log(`📡 API Endpoints:`);
    console.log(`   http://localhost:${PORT}/api/products`);
    console.log(`   http://localhost:${PORT}/api/health`);
});