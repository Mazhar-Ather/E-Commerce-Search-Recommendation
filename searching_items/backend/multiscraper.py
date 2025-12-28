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
from urllib.parse import quote

# -------------------- DRIVER SETUP --------------------
def setup_driver():
    """Setup Chrome driver with options"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
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

# -------------------- WEBSITE CONFIGURATIONS --------------------
WEBSITE_CONFIGS = {
    "daraz": {
        "name": "Daraz",
        "base_url": "https://www.daraz.pk",
        "search_urls": {
            "protein powder": "/catalog/?q=protein%20powder",
            "creatine": "/catalog/?q=creatine",
            "whey protein": "/catalog/?q=whey%20protein",
            "mass gainer": "/catalog/?q=mass%20gainer",
            "vitamins": "/catalog/?q=vitamins"
        },
        "selectors": {
            "product_container": ".Bm3ON, .card-jty-li, .gridItem--Yd0sa",
            "product_link": "a[href*='/products/']",
            "product_image": "img",
            "product_name_attr": "alt",
            "price": ".ooOxS, .jcHByF",
            "rating": ".mdmmT span",
        },
        "accessible": False
    },
    "jacknutrition": {
        "name": "JackNutrition",
        "base_url": "https://jacknutrition.com.pk",
        "search_urls": {
            "protein": "/collections/whey-protein",
            "mass gainer": "/collections/mass-gainer",
            "pre workout": "/collections/pre-workout",
            "vitamins": "/collections/vitamins"
        },
        "selectors": {
            "product_container": ".product-item, .grid__item",
            "product_link": "a[href*='/products/']",
            "product_image": "img",
            "product_name_attr": "alt",
            "price": ".price, .money",
            "rating": ".rating",
        },
        "accessible": False
    },
    "amazon": {
        "name": "Amazon",
        "base_url": "https://www.amazon.com",
        "search_urls": {
            "protein powder": "/s?k=protein+powder",
            "whey protein": "/s?k=whey+protein",
            "creatine": "/s?k=creatine",
            "mass gainer": "/s?k=mass+gainer"
        },
        "selectors": {
            "product_container": "[data-component-type='s-search-result']",
            "product_link": "a.a-link-normal[href*='/dp/']",
            "product_name": "h2 a span",
            "price": ".a-price-whole",
            "rating": ".a-icon-alt",
        },
        "accessible": False
    }
}

# -------------------- DEMO DATA --------------------
DEMO_PRODUCTS = {
    "daraz": [
        {"name": "Optimum Nutrition Whey Protein 2kg", "price": "Rs. 12,999", "rating": "4.5", "quantity": "2 kg", "category": "protein powder", "link": "https://daraz.pk/protein1"},
        {"name": "MuscleTech Creatine 500g", "price": "Rs. 3,499", "rating": "4.3", "quantity": "500 g", "category": "creatine", "link": "https://daraz.pk/creatine1"},
        {"name": "Mass Gainer 5kg", "price": "Rs. 8,999", "rating": "4.2", "quantity": "5 kg", "category": "mass gainer", "link": "https://daraz.pk/mass1"},
    ],
    "jacknutrition": [
        {"name": "Jack Nutrition Whey 5lb", "price": "Rs. 14,999", "rating": "4.6", "quantity": "5 lb", "category": "protein", "link": "https://jacknutrition.com/whey1"},
        {"name": "Pre Workout 30 Servings", "price": "Rs. 3,499", "rating": "4.4", "quantity": "30 servings", "category": "pre workout", "link": "https://jacknutrition.com/pre1"},
    ],
    "amazon": [
        {"name": "Optimum Nutrition Whey 5lb", "price": "$64.99", "rating": "4.7", "quantity": "5 lb", "category": "protein powder", "link": "https://amazon.com/protein1"},
        {"name": "Dymatize ISO100 5lb", "price": "$89.99", "rating": "4.8", "quantity": "5 lb", "category": "protein powder", "link": "https://amazon.com/iso1"},
        {"name": "MuscleTech Creatine 400g", "price": "$19.99", "rating": "4.6", "quantity": "400 g", "category": "creatine", "link": "https://amazon.com/creatine1"},
    ]
}

# -------------------- QUANTITY EXTRACTION --------------------
def extract_quantity(product_name, website="daraz"):
    """Extract quantity from product name"""
    if not product_name:
        return "Not specified"
    
    text = product_name.lower()
    
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*(kg|kilogram)\b', 'kg'),
        (r'(\d+(?:\.\d+)?)\s*(g|gram)\b', 'g'),
        (r'(\d+)\s*(mg|milligram)\b', 'mg'),
        (r'(\d+(?:\.\d+)?)\s*(lb|pound)\b', 'lb'),
        (r'(\d+)\s*(capsules?|caps?)\b', 'capsules'),
        (r'(\d+)\s*(tablets?|tabs?)\b', 'tablets'),
        (r'(\d+)\s*(servings?)\b', 'servings'),
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, text)
        if match:
            amount = match.group(1)
            return f"{amount} {unit}"
    
    return "Not specified"

# -------------------- DEMO MODE --------------------
def scrape_demo_data(website_name, category):
    """Scrape demo data"""
    print(f"📱 Using DEMO MODE for {WEBSITE_CONFIGS[website_name]['name']}")
    
    db, cursor = setup_database()
    if not db:
        return 0
    
    cursor.execute("SELECT product_link FROM daraz_products WHERE website = %s", 
                   (WEBSITE_CONFIGS[website_name]['name'],))
    existing_links = {row[0] for row in cursor.fetchall()}
    
    new_count = 0
    demo_products = DEMO_PRODUCTS.get(website_name, [])
    
    for product in demo_products:
        if product['link'] in existing_links:
            continue
        
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
            new_count += 1
            print(f"   ✅ Demo: {product['name'][:40]}... | {product['price']}")
        except:
            db.rollback()
    
    cursor.close()
    db.close()
    return new_count

# -------------------- AMAZON SCRAPER --------------------
def scrape_amazon(driver, category):
    """Scrape Amazon products"""
    print(f"🛒 Scraping Amazon - {category}")
    
    config = WEBSITE_CONFIGS["amazon"]
    
    db, cursor = setup_database()
    if not db:
        return scrape_demo_data("amazon", category)
    
    cursor.execute("SELECT product_link FROM daraz_products WHERE website = %s", 
                   (config['name'],))
    existing_links = {row[0] for row in cursor.fetchall()}
    
    new_count = 0
    
    try:
        # Build search URL
        search_query = category.replace(" ", "+")
        url = f"{config['base_url']}/s?k={search_query}"
        
        print(f"   📄 URL: {url}")
        driver.get(url)
        time.sleep(4)
        
        # Find products
        products = driver.find_elements(By.CSS_SELECTOR, config['selectors']['product_container'])
        print(f"   Found {len(products)} products")
        
        for i, product in enumerate(products[:10]):  # Limit to 10
            try:
                # Get product link
                link_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['product_link'])
                link = link_elem.get_attribute("href")
                
                if link in existing_links:
                    continue
                
                # Get product name
                name_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['product_name'])
                name = name_elem.text
                
                # Get price
                price = "Price not available"
                try:
                    price_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['price'])
                    price = "$" + price_elem.text
                except:
                    pass
                
                # Get rating
                rating = "No Rating"
                try:
                    rating_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['rating'])
                    rating_text = rating_elem.get_attribute("textContent")
                    rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1)
                except:
                    pass
                
                # Extract quantity
                quantity = extract_quantity(name, "amazon")
                
                # Save to database
                insert_sql = """
                INSERT INTO daraz_products 
                (product_name, price, rating, category, website, product_link, page, quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (name, price, rating, category, config['name'], link, 1, quantity)
                
                cursor.execute(insert_sql, values)
                db.commit()
                new_count += 1
                print(f"   ✅ {i+1}/10: {name[:40]}... | {price}")
                
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"   ❌ Amazon error: {e}")
        return scrape_demo_data("amazon", category)
    finally:
        cursor.close()
        db.close()
    
    return new_count

# -------------------- DARAZ/JACKNUTRITION SCRAPER --------------------
def scrape_website(driver, website_name, category):
    """Scrape Daraz or JackNutrition"""
    if website_name not in ["daraz", "jacknutrition"]:
        return 0
    
    config = WEBSITE_CONFIGS[website_name]
    
    if not config['accessible']:
        return scrape_demo_data(website_name, category)
    
    print(f"🌐 Scraping {config['name']} - {category}")
    
    db, cursor = setup_database()
    if not db:
        return scrape_demo_data(website_name, category)
    
    cursor.execute("SELECT product_link FROM daraz_products WHERE website = %s", 
                   (config['name'],))
    existing_links = {row[0] for row in cursor.fetchall()}
    
    new_count = 0
    
    try:
        url = config['base_url'] + config['search_urls'][category]
        print(f"   📄 URL: {url}")
        
        driver.get(url)
        time.sleep(3)
        
        products = driver.find_elements(By.CSS_SELECTOR, config['selectors']['product_container'])
        print(f"   Found {len(products)} products")
        
        for i, product in enumerate(products[:10]):
            try:
                # Get link
                link_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['product_link'])
                link = link_elem.get_attribute("href")
                
                if link in existing_links:
                    continue
                
                # Get name from image alt
                img = product.find_element(By.CSS_SELECTOR, config['selectors']['product_image'])
                name = img.get_attribute(config['selectors']['product_name_attr'])
                
                # Get price
                price = "Price not available"
                try:
                    price_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['price'])
                    price = price_elem.text
                except:
                    pass
                
                # Get rating
                rating = "No Rating"
                if website_name == "daraz":
                    try:
                        rating_elem = product.find_element(By.CSS_SELECTOR, config['selectors']['rating'])
                        rating = rating_elem.text
                    except:
                        pass
                
                # Extract quantity
                quantity = extract_quantity(name, website_name)
                
                # Save to database
                insert_sql = """
                INSERT INTO daraz_products 
                (product_name, price, rating, category, website, product_link, page, quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (name, price, rating, category, config['name'], link, 1, quantity)
                
                cursor.execute(insert_sql, values)
                db.commit()
                new_count += 1
                print(f"   ✅ {i+1}/10: {name[:40]}... | {price}")
                
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"   ❌ {config['name']} error: {e}")
        return scrape_demo_data(website_name, category)
    finally:
        cursor.close()
        db.close()
    
    return new_count

# -------------------- WEBSITE CHECK --------------------
def check_websites_accessibility():
    """Check website accessibility"""
    print("\n🔍 Checking website accessibility...")
    
    for website in WEBSITE_CONFIGS:
        config = WEBSITE_CONFIGS[website]
        
        print(f"   {config['name']}: {config['base_url']}", end=" ")
        
        try:
            response = requests.get(config['base_url'], timeout=5)
            config['accessible'] = response.status_code == 200
            print("✅ ACCESSIBLE" if config['accessible'] else "❌ NOT ACCESSIBLE")
        except:
            config['accessible'] = False
            print("❌ NOT ACCESSIBLE")
    
    print("\n" + "="*60)

# -------------------- STATISTICS --------------------
def display_statistics():
    """Show database statistics"""
    db, cursor = setup_database()
    if not db:
        return
    
    try:
        cursor.execute("SELECT COUNT(*) FROM daraz_products")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT website, COUNT(*) FROM daraz_products GROUP BY website")
        by_website = cursor.fetchall()
        
        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print(f"Total Products: {total}")
        
        print("\n🏪 Products by Website:")
        for website, count in by_website:
            print(f"  • {website}: {count} products")
        
        print("\n🌐 Website Status:")
        for website in WEBSITE_CONFIGS:
            status = "✅ Online" if WEBSITE_CONFIGS[website]['accessible'] else "📱 Demo"
            print(f"  • {WEBSITE_CONFIGS[website]['name']}: {status}")
        
        print("\n🆕 Sample Products:")
        for website in WEBSITE_CONFIGS:
            cursor.execute("""
                SELECT product_name, price, quantity 
                FROM daraz_products 
                WHERE website = %s 
                LIMIT 1
            """, (WEBSITE_CONFIGS[website]['name'],))
            sample = cursor.fetchone()
            
            if sample:
                name, price, qty = sample
                print(f"  {WEBSITE_CONFIGS[website]['name']}: {name[:30]}... - {price} - Qty: {qty}")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        db.close()

# -------------------- MAIN FUNCTION --------------------
def main():
    """Main function"""
    print("="*60)
    print("🛒 MULTI-WEBSITE PRODUCT SCRAPER")
    print("="*60)
    print("Supports: Daraz | JackNutrition | Amazon")
    print("="*60)
    
    # Setup driver
    driver = setup_driver()
    
    # Check websites
    check_websites_accessibility()
    
    # Setup database
    db, cursor = setup_database()
    if db:
        cursor.close()
        db.close()
    
    # Main menu
    while True:
        print("\n📋 MAIN MENU:")
        print("  1. Scrape Daraz")
        print("  2. Scrape JackNutrition")
        print("  3. Scrape Amazon")
        print("  4. Scrape All Websites")
        print("  5. Show Statistics")
        print("  6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            print("\n📁 Daraz Categories:")
            categories = list(WEBSITE_CONFIGS["daraz"]["search_urls"].keys())
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            
            cat_choice = input("\nSelect category (1-5): ").strip()
            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    count = scrape_website(driver, "daraz", categories[cat_index])
                    print(f"\n✅ Added {count} products from Daraz")
                else:
                    print("❌ Invalid category")
            except:
                print("❌ Invalid input")
        
        elif choice == "2":
            print("\n📁 JackNutrition Categories:")
            categories = list(WEBSITE_CONFIGS["jacknutrition"]["search_urls"].keys())
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            
            cat_choice = input("\nSelect category (1-4): ").strip()
            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    count = scrape_website(driver, "jacknutrition", categories[cat_index])
                    print(f"\n✅ Added {count} products from JackNutrition")
                else:
                    print("❌ Invalid category")
            except:
                print("❌ Invalid input")
        
        elif choice == "3":
            print("\n📁 Amazon Categories:")
            categories = list(WEBSITE_CONFIGS["amazon"]["search_urls"].keys())
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            
            cat_choice = input("\nSelect category (1-4): ").strip()
            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    count = scrape_amazon(driver, categories[cat_index])
                    print(f"\n✅ Added {count} products from Amazon")
                else:
                    print("❌ Invalid category")
            except:
                print("❌ Invalid input")
        
        elif choice == "4":
            print("\n🔄 Scraping all websites...")
            total = 0
            
            # Daraz
            count = scrape_website(driver, "daraz", "protein powder")
            total += count
            
            # JackNutrition
            count = scrape_website(driver, "jacknutrition", "protein")
            total += count
            
            # Amazon
            count = scrape_amazon(driver, "protein powder")
            total += count
            
            print(f"\n✅ Total added from all websites: {total}")
        
        elif choice == "5":
            display_statistics()
        
        elif choice == "6":
            print("\n👋 Exiting...")
            break
        
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()