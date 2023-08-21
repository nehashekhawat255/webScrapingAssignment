import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def get_product_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    
    product_description_tag = soup.find("div", {"id": "productDescription"})
    product_description = product_description_tag.get_text(strip=True).strip() if product_description_tag else "N/A"
    
    manufacturer_tag = soup.find("a", {"href": re.compile(r"/s\?k=by\+[\w+]+")})
    manufacturer = manufacturer_tag.get_text(strip=True) if manufacturer_tag else "N/A"
    
    asin_tag = soup.find("th", string="ASIN")
    asin = asin_tag.find_next("td").get_text(strip=True) if asin_tag else "N/A"
    
    return product_description, manufacturer, asin

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"

product_info_data = []
product_details_data = []

# Scrape data for product URLs and gather additional details
for page in range(1, 51):
    url = base_url.format(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    product_items = soup.find_all("div", class_="s-result-item")
    
    for item in product_items:
        product_url_tag = item.find("a", class_="a-link-normal s-no-outline")
        product_url = "https://www.amazon.in" + product_url_tag["href"] if product_url_tag else "N/A"
        
        product_name_tag = item.find("span", class_="a-size-medium a-color-base a-text-normal")
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "N/A"
        
        price_tag = item.find("span", class_="a-price")
        product_price = price_tag.find("span", class_="a-offscreen").get_text(strip=True) if price_tag else "N/A"
        
        rating_tag = item.find("span", class_="a-icon-alt")
        product_rating = re.search(r"([\d.]+)", rating_tag.get_text(strip=True)).group(1) if rating_tag else "N/A"
        
        reviews_tag = item.find("span", {"aria-label": re.compile(r"(\d+) ratings?")})
        product_reviews = reviews_tag.get_text(strip=True) if reviews_tag else "N/A"
        
        if product_url != "N/A":  # Only proceed if the product URL is available
            product_info_data.append([product_url, product_name, product_price, product_rating, product_reviews])
            
            if len(product_info_data) >= 200:
                break

    if len(product_info_data) >= 200:
        break

# Create product info DataFrame
product_info_df = pd.DataFrame(product_info_data, columns=["Product URL", "Product Name", "Product Price", "Product Rating", "Number of Reviews"])

# Write DataFrame to CSV
product_info_df.to_csv("amazon_product_information.csv", index=False, encoding="utf-8")

print("CSV file 'amazon_product_information.csv' has been created.")

# Load product URLs from the first CSV file
product_urls = product_info_df["Product URL"]

# Scrape data for additional product details
for product_url in product_urls:
    if product_url != "N/A":  # Only proceed if the product URL is available
        product_description, manufacturer, asin = get_product_details(product_url)
        product_details_data.append([product_url, product_description, manufacturer, asin])

# Create product details DataFrame
product_details_df = pd.DataFrame(product_details_data, columns=["Product URL", "Product Description", "Manufacturer", "ASIN"])

# Write DataFrame to CSV
product_details_df.to_csv("amazon_product_details.csv", index=False, encoding="utf-8")

print("CSV file 'amazon_product_details.csv' has been created.")
