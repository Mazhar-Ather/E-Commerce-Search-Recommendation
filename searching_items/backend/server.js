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
// Get ALL product names
app.get("/api/products", (req, res) => {
    console.log("📡 GET /api/products called");
    
    // First, get total count from database
    db.query("SELECT COUNT(*) as total FROM daraz_products", (countErr, countResults) => {
        if (countErr) {
            console.error("❌ Count query error:", countErr.message);
            return res.status(500).json({ error: "Count query failed" });
        }
        
        const totalInDB = countResults[0].total;
        console.log(`📊 Database says: ${totalInDB} total products`);
        
        // Now get all product names
        const sql = "SELECT product_name FROM daraz_products";
        
        db.query(sql, (err, results) => {
            if (err) {
                console.error("❌ Database query error:", err.message);
                return res.status(500).json({ 
                    error: "Database error", 
                    details: err.message 
                });
            }
            
            console.log(`✅ Query returned: ${results.length} rows`);
            
            // Analyze the data
            const productNames = results
                .map(row => row.product_name)
                .filter(name => {
                    if (!name || typeof name !== 'string') {
                        console.log(`   Found non-string/null name: ${typeof name}`);
                        return false;
                    }
                    const trimmed = name.trim();
                    if (trimmed === "") {
                        console.log(`   Found empty name`);
                        return false;
                    }
                    return true;
                });
            
            console.log(`📦 After filtering: ${productNames.length} valid product names`);
            
            // Send detailed response for debugging
            res.json({
                debug: {
                    totalInDatabase: totalInDB,
                    rowsReturned: results.length,
                    validProductNames: productNames.length,
                    sample: productNames.slice(0, 5) // First 5 for checking
                },
                products: productNames
            });
        });
    });
});
// Debug endpoint to check data quality
app.get("/api/debug/products", (req, res) => {
    console.log("🔍 Debug endpoint called");
    
    const sql = `
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN product_name IS NULL THEN 1 ELSE 0 END) as null_names,
            SUM(CASE WHEN product_name = '' THEN 1 ELSE 0 END) as empty_names,
            SUM(CASE WHEN LENGTH(TRIM(product_name)) = 0 THEN 1 ELSE 0 END) as whitespace_names,
            SUM(CASE WHEN product_name IS NOT NULL AND LENGTH(TRIM(product_name)) > 0 THEN 1 ELSE 0 END) as valid_names
        FROM daraz_products
    `;
    
    db.query(sql, (err, results) => {
        if (err) {
            console.error("❌ Debug query error:", err);
            return res.status(500).json({ error: "Debug query failed" });
        }
        
        const stats = results[0];
        console.log("📊 Database Statistics:");
        console.log(`   Total rows: ${stats.total}`);
        console.log(`   Null names: ${stats.null_names}`);
        console.log(`   Empty names: ${stats.empty_names}`);
        console.log(`   Whitespace names: ${stats.whitespace_names}`);
        console.log(`   Valid names: ${stats.valid_names}`);
        
        // Get sample of invalid data
        const invalidSql = `
            SELECT id, product_name 
            FROM daraz_products 
            WHERE product_name IS NULL 
               OR product_name = '' 
               OR LENGTH(TRIM(product_name)) = 0
            LIMIT 10
        `;
        
        db.query(invalidSql, (invalidErr, invalidResults) => {
            if (invalidErr) {
                console.error("❌ Invalid data query error:", invalidErr);
            }
            
            res.json({
                statistics: stats,
                invalid_samples: invalidResults,
                message: `Only ${stats.valid_names} of ${stats.total} products have valid names`
            });
        });
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