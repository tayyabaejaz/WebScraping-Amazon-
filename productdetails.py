import os
import csv
import time
import random
import requests
import winsound
import pandas as pd
from PIL import Image
from io import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from dataclasses import dataclass, asdict
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC







CSV_FILE_PATH = "D:\\Tayyaba Stuff\\JOB\\kodewizardz\\selenium-undetected\\amazon_products_details(rescrape).csv"






@dataclass
class Product:
    scrap_source_identifier: str
    title: str
    price: str
    rating: str
    reviews: str
    availability: str
    description: str
    product_description: str
    url: str
    store_name: str
    store_url: str
    internet_source: str
    basic_product_details: str
    extra_product_details:str
    pack_count_and_price:str
    additional_information:str
    time_created: str
    time_scanned: str
    time_updated: str = ""

def extract_product_details(scrap_source_identifier, url, index, soup):
    
        
    try:

        # # Check the location
        # if not check_location(soup):
        #     print(f"Skipping URL-{index} for ID-{scrap_source_identifier} due to location mismatch.")
        #     return {"id": scrap_source_identifier, "url": url, "reason": "Location mismatch"}

        #Extract product details if location matches
        title = get_title(soup)
        price = get_price(soup)
        rating = get_rating(soup)
        reviews = get_review_count(soup)
        availability = get_availability(soup)
        description = get_description(soup)
        product_description = get_product_description(soup)
        store_name, store_url = get_store(soup)
        basic_product_details = get_basic_product_details(soup)
        pack_count_and_price= extract_count_and_price(soup)
        additional_information=extract_additional_information(soup)
        extra_product_details=extract_extra_product_details(soup)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if title and url:
            internet_source = get_internet_source(url)
            product = Product(
                scrap_source_identifier=scrap_source_identifier,
                title=title,
                price=price,
                rating=rating,
                reviews=reviews,
                availability=availability,
                description=description,
                product_description=product_description,
                url=url,
                store_name=store_name,
                store_url=store_url,
                internet_source=internet_source,
                basic_product_details=basic_product_details,
                pack_count_and_price=pack_count_and_price,
                additional_information=additional_information,
                extra_product_details=extra_product_details,
                time_created=current_time,
                time_scanned=current_time
            )
            save_to_csv(product, CSV_FILE_PATH)
            return product
        else:
            print(f"Incomplete data for {scrap_source_identifier}.")
            return {"id": scrap_source_identifier, "url": url, "reason": "Incomplete data"}

    except Exception as e:
        print(f"Error extracting product details for {scrap_source_identifier}: {e}")
        return {"id": scrap_source_identifier, "url": url, "reason": str(e)}

def get_title(soup):
    try:
        return soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except AttributeError:
        return ""

def get_price(soup):
    try:
        price_symbol = soup.find("span", class_="a-price-symbol").text.strip()
        price_whole = soup.find("span", class_="a-price-whole").text.strip().replace('.', '')
        price_fraction = soup.find("span", class_="a-price-fraction").text.strip()
        return f"{price_symbol}{price_whole}.{price_fraction}"
    except AttributeError:
        return ""

def get_rating(soup):
    try:
        return soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
    except AttributeError:
        return ""

def get_review_count(soup):
    try:
        return soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip()
    except AttributeError:
        return ""

def get_availability(soup):
    try:
        return soup.find("div", attrs={'id': 'availability'}).find("span").string.strip()
    except AttributeError:
        return "Not Available"

def get_description(soup):
    try:
        return soup.find("div", attrs={'id': 'feature-bullets'}).get_text(separator=" ").strip()
    except AttributeError:
        return "No description available"

def get_basic_product_details(soup):
    # Find the table by its ID
    table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
    
    if table:
        # Initialize a dictionary to store the extracted data
        table_data = {}

        # Iterate over the rows of the table
        for row in table.find_all("tr"):
            # Extract the header and data
            header = row.find("th").text.strip()
            value = row.find("td").text.strip()

            # Store them in the dictionary
            table_data[header] = value

        return table_data
    else:
        return "Table with id 'productDetails_techSpec_section_1' not found"


def extract_count_and_price(soup):
    results = []
    
    try:
        # Targeting count and price elements with specified classes
        count_elements = soup.find_all("p", class_="a-text-left a-size-base")  # Adjusted for count
        price_whole_elements = soup.find_all("p", class_="a-spacing-none a-text-left a-size-mini twisterSwatchPrice")  # Adjusted for price

        # Ensure both elements have the same length for pairing
        min_length = min(len(count_elements), len(price_whole_elements))

        for i in range(min_length):
            count_text = count_elements[i].text.strip() if count_elements[i] else "Not found"
            price_text = price_whole_elements[i].text.strip() if price_whole_elements[i] else "Not found"

            # Format the result
            results.append(f"{count_text}: {price_text}")

        # Remove duplicates and return results
        unique_results = list(set(results))
        return "\n".join(unique_results) if unique_results else "Not found"

    except Exception as e:
        print(f"Error extracting counts and prices: {e}")
        return "Not found"


def extract_additional_information(soup):
    # Find the table by its ID
    table = soup.find("table", {"id": "productDetails_detailBullets_sections1"})
    
    if table:
        # Initialize a dictionary to store the extracted data
        table_data = {}

        # Iterate over the rows of the table
        for row in table.find_all("tr"):
            # Extract the header and data
            header = row.find("th").text.strip()
            value = row.find("td").text.strip()

            # Store them in the dictionary
            table_data[header] = value

        return table_data
    else:
        return "Table with id 'produproductDetails_detailBullets_sections1' not found"


def extract_extra_product_details(soup):
    extra_details = []

    # Find the list containing extra product details
    details_section = soup.find("div", id="detailBullets_feature_div")
    if details_section:
        list_items = details_section.find_all("li")
        for item in list_items:
            # Extract key and value
            key = item.find("span", class_="a-text-bold").text.strip().replace(":", "")
            value = item.find_all("span")[-1].text.strip()  # Gets the last <span> for the value
            
            # Clean up the key and value further to avoid excess whitespace
            key = key.replace("\u200e", "").strip()
            value = value.replace("\u200e", "").strip()
            
            # Append formatted string to the list
            extra_details.append(f"{key} : {value}")

    # Combine the extracted details into a single string with newline separation
    combined_extra_info = "\n".join(extra_details)
    
    return combined_extra_info

    
    
def get_product_description(soup):
    try:
        # Corrected the ID to match the given HTML structure
        description_div = soup.find("div", id="important-information")
        if description_div:
            product_details = []
            sections = description_div.find_all("div", class_="content")
            for section in sections:
                header = section.find("h4").get_text(strip=True) if section.find("h4") else "No Header"
                # Join the text of all <p> tags within each section
                paragraphs = section.find_all("p")
                content = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                product_details.append(f"{header}: {content}")
            return " | ".join(product_details)
        return "No product description available"
    except AttributeError:
        return "No product description available"


def get_store(soup):
    try:
        store_element = soup.find("a", id="bylineInfo")
        store_name = store_element.text.strip()
        store_url = f"https://www.amazon.co.uk{store_element['href']}"
        return store_name, store_url
    except AttributeError:
        return "", ""

def get_internet_source(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def save_to_csv(product, filename):
    if not isinstance(product, Product):
        print("Error: The product passed is not a dataclass instance.")
        return

    fieldnames = list(asdict(product).keys())
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        if not file_exists:
            dict_writer.writeheader()

        dict_writer.writerow(asdict(product))
        print(f"Saved product {product.title} to CSV.")


def get_processed_identifiers(csv_file):
    """Reads the CSV file and extracts the already processed scrap_source_identifiers."""
    processed_identifiers = set()  # Using a set for fast lookups
    if os.path.exists(csv_file):
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processed_identifiers.add(row['scrap_source_identifier'])  # Adjust the field name if necessary
    return processed_identifiers

def perform_exit_sequence(msg: str, driver: uc.Chrome, exit_code: int = -1):
    print(msg)
    try:
        if driver:
            driver.quit()  # Attempt to quit the driver only if it's open
    except Exception as e:
        print(f"Error during driver quit: {e}")
    exit(code=exit_code)

def check_for_captcha(driver: uc.Chrome):
    try:
        captcha_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Enter the characters you see')]")
        if captcha_element:
            print(f"CAPTCHA detected!")
            # Play beep sound (frequency 1000 Hz, duration 500 ms)
            # winsound.Beep(1000, 500)
            return True
    except NoSuchElementException:
        # CAPTCHA not found, proceed as normal
        print(f"No CAPTCHA detected ")
        return False
    
def check_location(soup) -> bool:
    try:
        location_span = soup.find("span", attrs={"class": "nav-line-1 nav-progressive-content"})
        if location_span:
            location = location_span.text.strip()
            print(f"Retrieved location: {location}")  # Add this line
            if "London" in location:
                print(f"Location check passed: {location}")
                
                return True
            else:
                print(f"Location is not London. Current location: {location}")
                
                return False
        else:
            print("Location information not found.")
            return False
    except Exception as e:
        print(f"Error checking location: {e}")
        return False

# Function to decline cookies
def decline_cookies(driver):
    try:
        cookies_button = driver.find_element(By.ID, "sp-cc-rejectall-link")
        cookies_button.click()
        print("Cookies declined.")
    except Exception as e:
        print("No cookies dialog found.")

def save_page_source(html_content, scrap_source_identifier):
    folder_path = "D:\\Tayyaba Stuff\\JOB\\kodewizardz\\selenium-undetected\\page_sources"
    os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists
    
    file_path = os.path.join(folder_path, f"pagesource_{scrap_source_identifier}.html")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
        print(f"Page source saved as {file_path}")

# Function to fetch URLs from CSV and open them
def open_product_urls_from_csv(csv_file, driver, wait):
    product_urls = read_urls_from_csv(csv_file)
    
    processed_identifiers = get_processed_identifiers(CSV_FILE_PATH)

    for index, (scrap_source_identifier, url) in enumerate(product_urls):
        if scrap_source_identifier in processed_identifiers:
            print(f"Skipping already processed product: {scrap_source_identifier}")
            continue  # Skip if already processed
        
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        while check_for_captcha(driver):
            winsound.Beep(1000, 500)
            time.sleep(3)

        # Decline cookies if necessary
        decline_cookies(driver)
        
        # Retrieve and save the page source after cookies have been declined
        html = driver.page_source
        save_page_source(html, scrap_source_identifier)

        # Extract product details
        result = extract_product_details(scrap_source_identifier, url, index, soup)
        if result is not None:
            print(f"Processed {scrap_source_identifier} successfully.")
        else: 
            print(f"Failed to Process {scrap_source_identifier} successfully.")

def read_urls_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [(row['scrap_source_identifier'], row['url']) for row in reader]

# Main function to perform one-time flow
def perform_amazon_flow():
    # Instantiate a Chrome browser
    driver = uc.Chrome(use_subprocess=False, version_main=128)
    driver.implicitly_wait(10)  # Set implicit wait of 10 seconds
    wait = WebDriverWait(driver, 20)  # Explicit wait with a 20-second timeout

    try:
        # Visit the target URL
        driver.get("https://www.amazon.co.uk")
        while check_for_captcha(driver):
            winsound.Beep(1000, 500)
            time.sleep(3)

        # Decline cookies if necessary
        decline_cookies(driver)

        # Read product URLs from the CSV and process them
        csv_file = 'amazon_scraping/missed_rescrape.csv'  # Replace with your actual CSV file path
        open_product_urls_from_csv(csv_file,driver,wait)
    except Exception as e:
        print(f"An error occurred: {e}")
        perform_exit_sequence("An error occurred during the scraping process.", driver)

    finally:
        # Close the browser after completing the task
        driver.quit()

if __name__ == "__main__":
    perform_amazon_flow()


'''google shopping ka page source nikalna hai and give to gp 
    run the selenium code for google shopping 
'''    