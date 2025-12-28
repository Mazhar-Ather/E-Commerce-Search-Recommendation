from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import mysql.connector
import time
import re
import requests
import socket

# -------------------- DRIVER SETUP --------------------
def setup_driver():
    """Setup Chrome driver with options"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Try to create driver
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"❌ Failed to create Chrome driver: {e}")
        return None

# -------------------- DATABASE SETUP --------------------
def setup_database():
    """Setup MySQL database connection"""
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mazhar334",
            database="ecommerce",
            autocommit=True
        )
        
        cursor = db.cursor()
        
        # Create table if it doesn't exist
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
            quantity VARCHAR(100),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        db.commit()
        
        return db, cursor
        
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return None, None

# -------------------- WEBSITE CHECK FUNCTION --------------------
def check_website_accessibility(url):
    """Check if a website is accessible"""
    try:
        # Try DNS resolution first
        domain = url.split('/')[2]
        socket.gethostbyname(domain)
        
        # Try HTTP request
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return response.status_code == 200
    except:
        return False

# -------------------- WEBSITE CONFIGURATIONS --------------------
WEBSITE_CONFIGS = {
    "daraz": {
        "name": "Daraz",
        "base_url": "https://www.daraz.pk",
        "search_urls": {
            "gym supplement": "/catalog/?q=gym%20supplement",
            "protein powder": "/catalog/?q=protein%20powder",
            "creatine": "/catalog/?q=creatine",
            "vitamins": "/catalog/?q=vitamins",
            "whey protein": "/catalog/?q=whey%20protein"
        },
        "selectors": {
            "product_container": ".Bm3ON, .card-jty-li, .gridItem--Yd0sa, .c1_t2i",
            "product_link": "a[href*='/products/']",
            "product_image": "img",
            "product_name_attr": "alt",
            "price": ".ooOxS, .jcHByF, .c13VH6",
            "rating": ".mdmmT span, .rating__yellow, .c2XhW",
        },
        "accessible": False  # Will be set dynamically
    },
    "jacknutrition": {
        "name": "JackNutrition",
        "base_url": "https://jacknutrition.com.pk",
        "search_urls": {
            "protein": "/collections/whey-protein",
            "mass gainer": "/collections/mass-gainer",
            "amino acids": "/collections/amino-acids",
            "pre workout": "/collections/pre-workout",
            "vitamins": "/collections/vitamins",
            "all products": "/collections/all"
        },
        "selectors": {
            "product_container": ".product-item, .grid__item, .product-card, .product",
            "product_link": "a[href*='/products/']",
            "product_image": "img",
            "product_name_attr": "alt",
            "price": ".price, .money, .product-price, .price-item",
            "rating": ".rating, .review-rating, .star-rating",
        },
        "accessible": False  # Will be set dynamically
    }
}

# -------------------- DEMO DATA FOR OFFLINE TESTING --------------------
DEMO_PRODUCTS = {
    "daraz": [
        {
            "name": "Optimum Nutrition Gold Standard Whey Protein 2kg",
            "price": "Rs. 12,999",
            "rating": "4.5",
            "quantity": "2 kg",
            "category": "protein powder",
            "link": "https://www.daraz.pk/products/optimum-nutrition-whey-protein-i12345678.html"
        },
        {
            "name": "MuscleTech Creatine 500g",
            "price": "Rs. 3,499",
            "rating": "4.3",
            "quantity": "500 g",
            "category": "creatine",
            "link": "https://www.daraz.pk/products/muscletech-creatine-i23456789.html"
        },
        {
            "name": "Dymatize ISO100 Hydrolyzed Protein 5lb",
            "price": "Rs. 18,500",
            "rating": "4.7",
            "quantity": "5 lb",
            "category": "protein powder",
            "link": "https://www.daraz.pk/products/dymatize-iso100-i34567890.html"
        },
        {
            "name": "Multivitamin Tablets 60 Capsules",
            "price": "Rs. 1,299",
            "rating": "4.2",
            "quantity": "60 capsules",
            "category": "vitamins",
            "link": "https://www.daraz.pk/products/multivitamin-capsules-i45678901.html"
        },
        {
            "name": "BSN Syntha-6 Protein Powder 4.5kg",
            "price": "Rs. 15,999",
            "rating": "4.4",
            "quantity": "4.5 kg",
            "category": "protein powder",
            "link": "https://www.daraz.pk/products/bsn-syntha6-i56789012.html"
        }
    ],
    "jacknutrition": [
        {
            "name": "Jack Nutrition Whey Protein 5lb",
            "price": "Rs. 14,999",
            "rating": "4.6",
            "quantity": "5 lb",
            "category": "protein",
            "link": "https://jacknutrition.com.pk/products/whey-protein-5lb"
        },
        {
            "name": "Mass Gainer 12lb",
            "price": "Rs. 12,500",
            "rating": "4.4",
            "quantity": "12 lb",
            "category": "mass gainer",
            "link": "https://jacknutrition.com.pk/products/mass-gainer-12lb"
        },
        {
            "name": "BCAA 30 Servings",
            "price": "Rs. 2,999",
            "rating": "4.3",
            "quantity": "30 servings",
            "category": "amino acids",
            "link": "https://jacknutrition.com.pk/products/bcaa-30-servings"
        },
        {
            "name": "Pre-Workout 40 Servings",
            "price": "Rs. 3,499",
            "rating": "4.5",
            "quantity": "40 servings",
            "link": "https://jacknutrition.com.pk/products/pre-workout-40"
        },
        {
            "name": "Vitamin D3 60 Tablets",
            "price": "Rs. 899",
            "rating": "4.1",
            "quantity": "60 tablets",
            "category": "vitamins",
            "link": "https://jacknutrition.com.pk/products/vitamin-d3-60"
        }
    ]
}

# -------------------- QUANTITY EXTRACTION FUNCTION --------------------
def extract_quantity(product_name, website="daraz"):
    """
    Extract quantity from product name
    Returns quantity in kg, g, ml, litre, capsule, tablet, etc.
    """
    if not product_name:
        return "Not specified"
    
    # Convert to lowercase for easier matching
    text = product_name.lower()
    
    # Common quantity patterns for both websites
    patterns = [
        # Weight patterns
        (r'(\d+(?:\.\d+)?)\s*(kg|kilogram|kilo)\b', 'kg'),
        (r'(\d+(?:\.\d+)?)\s*(g|gm|gram)\b', 'g'),
        (r'(\d+)\s*(mg|milligram)\b', 'mg'),
        
        # Volume patterns
        (r'(\d+(?:\.\d+)?)\s*(l|litre|liter)\b', 'L'),
        (r'(\d+(?:\.\d+)?)\s*(ml|milliliter)\b', 'ml'),
        
        # Count patterns
        (r'(\d+)\s*(capsules?|caps?)\b', 'capsules'),
        (r'(\d+)\s*(tablets?|tabs?)\b', 'tablets'),
        (r'(\d+)\s*(pills?)\b', 'pills'),
        (r'(\d+)\s*(pieces?|pcs?)\b', 'pieces'),
        (r'(\d+)\s*(servings?)\b', 'servings'),
        
        # Pack patterns
        (r'(\d+)\s*(packs?|pk?)\b', 'pack'),
        (r'(\d+)\s*(bottles?)\b', 'bottle'),
        (r'(\d+)\s*(jars?)\b', 'jar'),
        (r'(\d+)\s*(tubs?)\b', 'tub'),
        (r'(\d+)\s*(scoops?)\b', 'scoops'),
        
        # Multi-pack patterns
        (r'(\d+)\s*x\s*(\d+)\s*(mg|g|kg|ml|l|capsules?|tablets?|servings?)\b', 'multi-pack'),
        
        # Size patterns
        (r'(\d+(?:\.\d+)?)\s*(oz|ounce)\b', 'oz'),
        (r'(\d+(?:\.\d+)?)\s*(lb|pound)\b', 'lb'),
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, text)
        if match:
            if unit == 'multi-pack':
                count = match.group(1)
                amount = match.group(2)
                sub_unit = match.group(3)
                return f"{count} x {amount}{sub_unit}"
            else:
                amount = match.group(1)
                return f"{amount} {unit}"
    
    # Check for common phrases without spaces
    common_phrases = {
        # Daraz common formats
        '1kg': '1 kg', '2kg': '2 kg', '5kg': '5 kg',
        '500g': '500 g', '250g': '250 g', '1l': '1 L',
        '500ml': '500 ml', '30capsules': '30 capsules',
        '60tablets': '60 tablets', '90caps': '90 capsules',
        
        # JackNutrition common formats
        '2lb': '2 lb', '5lb': '5 lb', '10lb': '10 lb',
        '907g': '907 g', '2268g': '2268 g',
        '30servings': '30 servings', '60servings': '60 servings',
    }
    
    for phrase, quantity in common_phrases.items():
        if phrase in text.replace(" ", ""):
            return quantity
    
    return "Not specified"

# -------------------- DEMO MODE FUNCTIONS --------------------
def scrape_demo_data(website_name, category):
    """Scrape demo data when website is not accessible"""
    print(f"📱 Using DEMO MODE for {WEBSITE_CONFIGS[website_name]['name']} - {category}")
    
    db, cursor = setup_database()
    if not db:
        return 0
    
    # Get existing links
    cursor.execute("SELECT product_link FROM daraz_products WHERE website = %s", 
                   (WEBSITE_CONFIGS[website_name]['name'],))
    existing_links = {row[0] for row in cursor.fetchall()}
    
    new_products_count = 0
    
    # Use demo products
    demo_products = DEMO_PRODUCTS.get(website_name, [])
    
    for product in demo_products:
        if product['link'] in existing_links:
            continue
        
        # Extract quantity if not already set
        if 'quantity' not in product or product['quantity'] == 'Not specified':
            product['quantity'] = extract_quantity(product['name'], website_name)
        
        # Insert into database
        insert_sql = """
        INSERT INTO daraz_products 
        (product_name, price, rating, category, website, product_link, page, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            product['name'],
            product['price'],
            product['rating'],
            category,
            WEBSITE_CONFIGS[website_name]['name'],
            product['link'],
            1,
            product['quantity']
        )
        
        try:
            cursor.execute(insert_sql, values)
            db.commit()
            new_products_count += 1
            print(f"   ✅ Demo: {product['name'][:40]}... | {product['price']} | Qty: {product['quantity']}")
            time.sleep(0.3)  # Small delay for realism
        except mysql.connector.IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"   ❌ Demo insert error: {e}")
    
    cursor.close()
    db.close()
    return new_products_count

# -------------------- REAL SCRAPING FUNCTIONS --------------------
def scrape_real_website(driver, website_name, category, max_pages=2):
    """Scrape real website data"""
    if website_name not in WEBSITE_CONFIGS:
        return 0
    
    config = WEBSITE_CONFIGS[website_name]
    
    # Check if website is accessible
    if not config['accessible']:
        print(f"   ⚠️ {config['name']} is not accessible. Switching to demo mode...")
        return scrape_demo_data(website_name, category)
    
    print(f"🌐 Scraping REAL DATA from {config['name']} - {category}")
    
    db, cursor = setup_database()
    if not db:
        return 0
    
    # Get existing links
    cursor.execute("SELECT product_link FROM daraz_products WHERE website = %s", 
                   (config['name'],))
    existing_links = {row[0] for row in cursor.fetchall()}
    
    new_products_count = 0
    
    for page in range(1, max_pages + 1):
        # Build URL
        if page == 1:
            url = config['base_url'] + config['search_urls'][category]
        else:
            if website_name == "daraz":
                url = f"{config['base_url']}{config['search_urls'][category]}&page={page}"
            else:
                url = f"{config['base_url']}{config['search_urls'][category]}?page={page}"
        
        print(f"   📄 Page {page}: {url}")
        
        try:
            # Try to load page with timeout
            driver.set_page_load_timeout(20)
            driver.get(url)
            time.sleep(3)
            
            # Find product containers
            containers = driver.find_elements(By.CSS_SELECTOR, config['selectors']['product_container'])
            
            if not containers:
                print(f"   ⚠️ No products found, trying alternative approach...")
                # Try to find any product links
                all_links = driver.find_elements(By.TAG_NAME, "a")
                product_links = []
                for link in all_links:
                    href = link.get_attribute("href")
                    if href and '/products/' in href:
                        product_links.append(href)
                
                if product_links:
                    print(f"   Found {len(product_links)} product links")
                    # Use demo data since we can't parse the page properly
                    return scrape_demo_data(website_name, category)
                else:
                    print(f"   ⚠️ Could not find any products")
                    continue
            
            print(f"   Found {len(containers)} products")
            
            for i, container in enumerate(containers[:10]):  # Limit to 10 products per page
                try:
                    # Extract product info
                    product_info = extract_product_info(container, config, website_name)
                    if not product_info:
                        continue
                    
                    # Skip if already exists
                    if product_info['link'] in existing_links:
                        continue
                    
                    # Save to database
                    insert_sql = """
                    INSERT INTO daraz_products 
                    (product_name, price, rating, category, website, product_link, page, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (
                        product_info['name'],
                        product_info['price'],
                        product_info['rating'],
                        category,
                        config['name'],
                        product_info['link'],
                        page,
                        product_info['quantity']
                    )
                    
                    try:
                        cursor.execute(insert_sql, values)
                        db.commit()
                        new_products_count += 1
                        existing_links.add(product_info['link'])
                        print(f"   ✅ {i+1}/{len(containers)}: {product_info['name'][:40]}...")
                    except mysql.connector.IntegrityError:
                        db.rollback()
                    except Exception as e:
                        db.rollback()
                        print(f"   ❌ Insert error: {e}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ⚠️ Error with product {i+1}: {str(e)[:50]}")
                    continue
            
            time.sleep(2)  # Delay between pages
            
        except TimeoutException:
            print(f"   ⚠️ Timeout loading page {page}")
            continue
        except WebDriverException as e:
            print(f"   ❌ Browser error: {str(e)[:100]}")
            # Switch to demo mode
            return scrape_demo_data(website_name, category)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    cursor.close()
    db.close()
    return new_products_count

def extract_product_info(container, config, website_name):
    """Extract product information from container"""
    try:
        # Get product link
        try:
            link_element = container.find_element(By.CSS_SELECTOR, config['selectors']['product_link'])
            link = link_element.get_attribute("href")
        except:
            # Try to find any link in container
            link_element = container.find_element(By.TAG_NAME, "a")
            link = link_element.get_attribute("href")
        
        # Get product name
        try:
            if website_name == "daraz":
                img = container.find_element(By.CSS_SELECTOR, config['selectors']['product_image'])
                name = img.get_attribute(config['selectors']['product_name_attr'])
            else:
                # For JackNutrition, try to find title
                try:
                    name_element = container.find_element(By.CSS_SELECTOR, ".title, .product-title, .name")
                    name = name_element.text
                except:
                    img = container.find_element(By.CSS_SELECTOR, config['selectors']['product_image'])
                    name = img.get_attribute(config['selectors']['product_name_attr'])
            
            if not name or name.strip() == "":
                name = "Unknown Product"
        except:
            name = "Unknown Product"
        
        # Get price
        try:
            price_element = container.find_element(By.CSS_SELECTOR, config['selectors']['price'])
            price = price_element.text
        except:
            price = "Price not available"
        
        # Get rating
        rating = "No Rating"
        if website_name == "daraz":
            try:
                rating_element = container.find_element(By.CSS_SELECTOR, config['selectors']['rating'])
                rating = rating_element.text
            except:
                pass
        
        # Extract quantity
        quantity = extract_quantity(name, website_name)
        
        return {
            'name': name,
            'price': price,
            'rating': rating,
            'quantity': quantity,
            'link': link
        }
        
    except Exception as e:
        print(f"   ⚠️ Extraction error: {str(e)[:50]}")
        return None

# -------------------- MAIN FUNCTIONS --------------------
def check_websites_accessibility():
    """Check which websites are accessible"""
    print("\n🔍 Checking website accessibility...")
    
    for website in WEBSITE_CONFIGS:
        config = WEBSITE_CONFIGS[website]
        test_url = config['base_url']
        
        print(f"   {config['name']}: {test_url}", end=" ")
        
        if check_website_accessibility(test_url):
            config['accessible'] = True
            print("✅ ACCESSIBLE")
        else:
            config['accessible'] = False
            print("❌ NOT ACCESSIBLE (Using demo data)")
    
    print("\n" + "="*60)

def display_statistics():
    """Display database statistics"""
    db, cursor = setup_database()
    if not db:
        return
    
    try:
        cursor.execute("SELECT COUNT(*) FROM daraz_products")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT website, COUNT(*) FROM daraz_products GROUP BY website")
        by_website = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM daraz_products WHERE quantity != 'Not specified'")
        with_qty = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print(f"Total Products: {total}")
        print(f"Products with Quantity: {with_qty} ({with_qty/total*100:.1f}%)")
        
        print("\n📈 Products by Website:")
        for website, count in by_website:
            print(f"  • {website}: {count} products")
        
        # Show accessibility status
        print("\n🌐 Website Status:")
        for website in WEBSITE_CONFIGS:
            status = "✅ Online" if WEBSITE_CONFIGS[website]['accessible'] else "📱 Demo Mode"
            print(f"  • {WEBSITE_CONFIGS[website]['name']}: {status}")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        db.close()

def main():
    """Main function"""
    print("="*60)
    print("🛒 SMART PRODUCT SCRAPER")
    print("="*60)
    print("This scraper automatically detects website accessibility")
    print("and uses demo data when websites are not accessible.")
    print("="*60)
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        print("❌ Failed to start browser. Running in demo-only mode.")
    
    # Check website accessibility
    check_websites_accessibility()
    
    # Setup database
    db, cursor = setup_database()
    if not db:
        print("❌ Database connection failed!")
        return
    cursor.close()
    db.close()
    
    # Main menu
    while True:
        print("\n📋 MAIN MENU:")
        print("  1. Scrape Daraz")
        print("  2. Scrape JackNutrition")
        print("  3. Scrape both websites")
        print("  4. Show statistics")
        print("  5. Clear database")
        print("  6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            print("\n📁 Daraz Categories:")
            categories = list(WEBSITE_CONFIGS["daraz"]["search_urls"].keys())
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            
            cat_choice = input("\nSelect category number or 'all': ").strip()
            
            if cat_choice.lower() == 'all':
                total = 0
                for cat in categories:
                    if driver and WEBSITE_CONFIGS["daraz"]["accessible"]:
                        count = scrape_real_website(driver, "daraz", cat, max_pages=1)
                    else:
                        count = scrape_demo_data("daraz", cat)
                    total += count
                print(f"\n✅ Total added from Daraz: {total}")
            else:
                try:
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categories):
                        cat = categories[cat_index]
                        if driver and WEBSITE_CONFIGS["daraz"]["accessible"]:
                            count = scrape_real_website(driver, "daraz", cat)
                        else:
                            count = scrape_demo_data("daraz", cat)
                        print(f"\n✅ Added {count} products from Daraz")
                    else:
                        print("❌ Invalid category number")
                except:
                    print("❌ Invalid input")
        
        elif choice == "2":
            print("\n📁 JackNutrition Categories:")
            categories = list(WEBSITE_CONFIGS["jacknutrition"]["search_urls"].keys())
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            
            cat_choice = input("\nSelect category number or 'all': ").strip()
            
            if cat_choice.lower() == 'all':
                total = 0
                for cat in categories:
                    if driver and WEBSITE_CONFIGS["jacknutrition"]["accessible"]:
                        count = scrape_real_website(driver, "jacknutrition", cat, max_pages=1)
                    else:
                        count = scrape_demo_data("jacknutrition", cat)
                    total += count
                print(f"\n✅ Total added from JackNutrition: {total}")
            else:
                try:
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categories):
                        cat = categories[cat_index]
                        if driver and WEBSITE_CONFIGS["jacknutrition"]["accessible"]:
                            count = scrape_real_website(driver, "jacknutrition", cat)
                        else:
                            count = scrape_demo_data("jacknutrition", cat)
                        print(f"\n✅ Added {count} products from JackNutrition")
                    else:
                        print("❌ Invalid category number")
                except:
                    print("❌ Invalid input")
        
        elif choice == "3":
            print("\n🔄 Scraping both websites...")
            total = 0
            
            # Daraz
            print("\n📦 Daraz:")
            if driver and WEBSITE_CONFIGS["daraz"]["accessible"]:
                count = scrape_real_website(driver, "daraz", "protein powder", max_pages=1)
            else:
                count = scrape_demo_data("daraz", "protein powder")
            total += count
            
            # JackNutrition
            print("\n📦 JackNutrition:")
            if driver and WEBSITE_CONFIGS["jacknutrition"]["accessible"]:
                count = scrape_real_website(driver, "jacknutrition", "protein", max_pages=1)
            else:
                count = scrape_demo_data("jacknutrition", "protein")
            total += count
            
            print(f"\n✅ Total added from both websites: {total}")
        
        elif choice == "4":
            display_statistics()
        
        elif choice == "5":
            confirm = input("\n⚠️ Are you sure you want to clear the database? (yes/no): ").strip().lower()
            if confirm == 'yes':
                db, cursor = setup_database()
                cursor.execute("DELETE FROM daraz_products")
                db.commit()
                cursor.close()
                db.close()
                print("✅ Database cleared!")
        
        elif choice == "6":
            print("\n👋 Exiting...")
            break
        
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        # Install required packages if missing
        try:
            import requests
        except ImportError:
            print("Installing required packages...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "mysql-connector-python", "selenium"])
        
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("\n🔌 Browser closed.")