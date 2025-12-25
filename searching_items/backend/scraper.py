from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
import time

# -------------------- DRIVER SETUP --------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# -------------------- BASE CATEGORY URL --------------------
base_url = "https://www.daraz.pk/catalog/?q=gym%20supplement"

# -------------------- DATABASE SETUP --------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mazhar334",
    database="ecommerce"
)

cursor = db.cursor()

# Create table if it doesn't exist (simplified structure)
create_table_sql = """
CREATE TABLE IF NOT EXISTS daraz_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(500),
    price VARCHAR(100),
    rating VARCHAR(50),
    category VARCHAR(100),
    website VARCHAR(50),
    product_link VARCHAR(1000) UNIQUE,
    page INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""
cursor.execute(create_table_sql)
db.commit()

# -------------------- SCRAPING FUNCTION --------------------
def scrape_products():
    print("🚀 Starting product scraping for Gym Supplements...")
    
    # Get existing links from database
    cursor.execute("SELECT product_link FROM daraz_products")
    existing_links = {row[0] for row in cursor.fetchall()}
    print(f"📊 Found {len(existing_links)} existing products in database")
    
    new_products_count = 0
    updated_products_count = 0
    total_pages = 3
    
    for page in range(1, total_pages + 1):
        page_start = time.time()
        
        # Build URL with pagination
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}&page={page}"
        
        print(f"\n📄 Scraping Page {page}: {url}")
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Find all product containers
        try:
            items = driver.find_elements(By.CSS_SELECTOR, ".Bm3ON, .card-jty-li, .gridItem--Yd0sa")
            print(f"   Found {len(items)} product containers")
        except:
            print("   No products found on this page")
            continue
        
        for index, item in enumerate(items):
            try:
                # Extract product link
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # Skip if already in database
                if link in existing_links:
                    continue
                
                # Extract product details
                try:
                    name = item.find_element(By.CSS_SELECTOR, "img").get_attribute("alt")
                    if not name or name.strip() == "":
                        name = "Unknown Product"
                except:
                    name = "Unknown Product"
                
                try:
                    price = item.find_element(By.CSS_SELECTOR, ".ooOxS, .jcHByF").text
                except:
                    price = "Price not available"
                
                try:
                    rating = item.find_element(By.CSS_SELECTOR, ".mdmmT span, .rating__yellow").text
                except:
                    rating = "No Rating"
                
                # Insert new product into database
                insert_sql = """
                INSERT INTO daraz_products 
                (product_name, price, rating, category, website, product_link, page)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (name, price, rating, "Gym Supplements", "Daraz", link, page)
                
                try:
                    cursor.execute(insert_sql, values)
                    db.commit()
                    new_products_count += 1
                    existing_links.add(link)  # Add to cache
                    print(f"   ✅ Added: {name[:50]}...")
                except mysql.connector.IntegrityError:
                    # Duplicate link (shouldn't happen with our check)
                    db.rollback()
                    print(f"   ⚠️  Duplicate skipped: {name[:50]}...")
                except Exception as e:
                    db.rollback()
                    print(f"   ❌ Insert error: {e}")
                
            except Exception as e:
                print(f"   ⚠️  Error processing product {index}: {str(e)[:50]}")
                continue
        
        print(f"   ⏱️  Page {page} completed in {time.time() - page_start:.2f}s")
    
    return new_products_count

# -------------------- UPDATE PRICES FUNCTION --------------------
def update_existing_prices():
    print("\n🔄 Checking for price updates on existing products...")
    
    # Get all existing products with their links and prices
    cursor.execute("SELECT id, product_link, price FROM daraz_products")
    existing_products = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}
    
    updated_count = 0
    
    # Check first 20 products for price updates
    sample_links = list(existing_products.keys())[:20]
    
    for link in sample_links:
        try:
            driver.get(link)
            time.sleep(1)
            
            # Get current price
            try:
                current_price = driver.find_element(By.CSS_SELECTOR, ".pdp-price, .price").text
            except:
                current_price = None
            
            product_id, old_price = existing_products[link]
            
            # Update if price changed
            if current_price and current_price != old_price:
                update_sql = "UPDATE daraz_products SET price = %s WHERE id = %s"
                cursor.execute(update_sql, (current_price, product_id))
                db.commit()
                updated_count += 1
                print(f"   💰 Updated price: {old_price} → {current_price}")
                
        except Exception as e:
            print(f"   ⚠️  Error checking price for {link[:50]}...: {e}")
            continue
    
    return updated_count

# -------------------- MAIN EXECUTION --------------------
if __name__ == "__main__":
    try:
        # Step 1: Scrape new products
        new_count = scrape_products()
        
        # Step 2: Update prices of existing products
        updated_count = update_existing_prices()
        
        # Step 3: Get final statistics
        cursor.execute("SELECT COUNT(*) FROM daraz_products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM daraz_products")
        categories_count = cursor.fetchone()[0]
        
        print("\n" + "="*50)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"📊 Total products in database: {total_products}")
        print(f"📦 New products added: {new_count}")
        print(f"💰 Prices updated: {updated_count}")
        print(f"🏷️  Categories: {categories_count}")
        
        # Show sample of what was added
        if new_count > 0:
            print(f"\n📝 Sample of new products added:")
            cursor.execute("SELECT product_name, price FROM daraz_products ORDER BY id DESC LIMIT 5")
            for product in cursor.fetchall():
                print(f"   • {product[0][:50]}... - {product[1]}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        driver.quit()
        cursor.close()
        db.close()
        print("\n🔌 Resources cleaned up.")