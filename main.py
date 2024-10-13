import re
import os
import csv
import time
import logging
import winsound
import urllib.parse    
from datetime import datetime
from bs4 import BeautifulSoup 
from typing import Optional, List
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

#configuring logging file
log_filename = "scraping_log.log"
logging.basicConfig(
    filename=log_filename, 
    level=logging.INFO,  # Set to DEBUG to log everything
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Class to represent product listing data
class ProductDTO:
    def __init__(self, Scrap_Source_Identifier, URL, Title, location, intake_method, Rating , Reviews,Price,Scrap_Source, Keywords, CreationDateTime, ScrappingStatus,IsSponsored=False):
        self.Scrap_Source_Identifier = Scrap_Source_Identifier
        self.URL = URL
        self.Title = Title
        self.location = location
        self.intake_method=intake_method
        self.IsSponsored = IsSponsored
        self.Rating = Rating
        self.Reviews = Reviews
        self.Scrap_Source = Scrap_Source
        self.Keywords = Keywords
        self.CreationDateTime = CreationDateTime
        self.ScrappingStatus = ScrappingStatus
        self.Price=Price



# Define the search keyword
keyword = 'probiotics'
products_filename="extracted_products.csv"
csv_file_path="yourfilepath.csv"

def clean_url(url):
    """Cleans the URL based on Amazon's URL structure."""
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    cleaned_url=(query_params["url"][0].split("/ref"))[0]
    if "url" not in query_params: return None
    return ("https://www.amazon.co.uk" + query_params)
    
def is_product_already_scraped(identifier, csv_file_path):
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['Scrap_Source_Identifier'] == identifier:
                    return True
        return False
    except FileNotFoundError:
        return False  # If the file doesn't exist, no duplicates are possible


def extract_product_details_from_main_page(page_number:int,soup) -> Optional[List[ProductDTO]]:
    products: List[ProductDTO] = []
    
    # Find all product containers using BeautifulSoup
    product_containers = soup.find_all("div", {"class": "s-result-item"})
    

    for i in range(len(product_containers)) :
        container=product_containers[i]
        try:
            # Extract product URL
            link_tag = container.find("a", {"class": ["a-link-normal", "s-underline-text", "s-underline-link-text", "s-link-style", "a-text-normal"]})
            if not link_tag: 
                print(f"skipping {container} on page: {page_number} ")
                continue
            
            product_url = ("https://www.amazon.co.uk" + link_tag['href']) if link_tag else "N/A"
            clean_product_url = clean_url(product_url)
            if not clean_product_url:
                print(f"skipping {product_url} on page: {page_number} ")
                continue 
            scrap_source_identifier = (clean_product_url.split("/"))[-1]
            if is_product_already_scraped(scrap_source_identifier, csv_file_path):
                print(f"Product {scrap_source_identifier} already exists, skipping.")
                continue  # Skip if already scraped
            
            #Extract location of products 
            location="United Kingdom"
            
            # Extract product title
            title_tag = container.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
            if not title_tag: 
                
                continue
            product_title = title_tag.get_text(strip=True) if title_tag else "N/A"
            
            # Extract product rating
            rating_tag = container.find("span", {"class": "a-icon-alt"})
            product_rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
            
            #product sponsor check
            sponsored_tag = container.find("span", {"class": "a-color-base"}, string="Sponsored")
            is_sponsored = sponsored_tag is not None  # True if found, False otherwise
            
            intake_method_element=container.find ("span",{"class":"a-size-base a-color-base s-background-color-platinum a-padding-mini aok-nowrap aok-align-top aok-inline-block"})
            product_intake_method=intake_method_element.get_text(strip=True) if intake_method_element else "N/A"
            
        
            # Extract product reviews
            reviews_tag = container.find("span", {"class": "a-size-base s-underline-text"})
            product_reviews = reviews_tag.get_text(strip=True) if reviews_tag else "N/A"

            # Extract product price
            price_whole_tag = container.find("span", {"class": "a-price-whole"})
            price_fraction_tag = container.find("span", {"class": "a-price-fraction"})
            price_symbol_tag = container.find("span", {"class": "a-price-symbol"})
            
            if price_whole_tag and price_fraction_tag and price_symbol_tag:
                product_price = f"{price_symbol_tag.get_text()}{price_whole_tag.get_text()}{price_fraction_tag.get_text()}"
            else:
                product_price = "N/A"
                
            # extract scrape source identifier and check for non duplication 
            
            
            # scraping other details 
            scrap_source = "Amazon"
            creation_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            scrapping_status = 1 if product_url != "N/A" else 0

            if scrapping_status:
                product = ProductDTO(
                    Scrap_Source_Identifier=scrap_source_identifier,
                    URL=clean_product_url,
                    Title=product_title,
                    Rating=product_rating,
                    location=location,
                    IsSponsored=is_sponsored,
                    product_intake_method=product_intake_method,
                    Reviews=product_reviews,
                    Price=product_price,  
                    Scrap_Source=scrap_source,
                    Keywords=[keyword],
                    CreationDateTime=creation_datetime,
                    ScrappingStatus=scrapping_status
                )
                products.append(product)

        except Exception as e:
            print(f"Error extracting product details: {e}")
            continue
    
    #return products




    products: List[ProductDTO] = []
    
    # Find all product containers using BeautifulSoup
    product_containers = soup.find_all("div", {"class": "s-result-item"})
    
    for container in product_containers:
        try:
            # Extract product URL
            link_tag = container.find("a", {"class": ["a-link-normal", "s-underline-text", "s-underline-link-text", "s-link-style", "a-text-normal"]})
            product_url = ("https://www.amazon.co.uk" + link_tag['href']) if link_tag else "N/A"
            clean_product_url = clean_url(product_url)
            
            #Extract location of products 
            location="United Kingdom"
            
            # Extract product title
            title_tag = container.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
            product_title = title_tag.get_text(strip=True) if title_tag else "N/A"
            
            # Extract product rating
            rating_tag = container.find("span", {"class": "a-icon-alt"})
            product_rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
            
            sponsored_tag = container.find("span", {"class": "a-color-base"}, string="Sponsored")
            is_sponsored = sponsored_tag is not None  # True if found, False otherwise
            
            # Extract product reviews
            reviews_tag = container.find("span", {"class": "a-size-base s-underline-text"})
            product_reviews = reviews_tag.get_text(strip=True) if reviews_tag else "N/A"

            # Extract product price
            price_whole_tag = container.find("span", {"class": "a-price-whole"})
            price_fraction_tag = container.find("span", {"class": "a-price-fraction"})
            price_symbol_tag = container.find("span", {"class": "a-price-symbol"})
            
            if price_whole_tag and price_fraction_tag and price_symbol_tag:
                product_price = f"{price_symbol_tag.get_text()}{price_whole_tag.get_text()}{price_fraction_tag.get_text()}"
            else:
                product_price = "N/A"
                
            # extract scrape source identifier and check for non duplication 
            scrap_source_identifier = container.get('data-asin') or 'N/A'
            if is_product_already_scraped(scrap_source_identifier, csv_file_path):
                print(f"Product {scrap_source_identifier} already exists, skipping.")
                continue  # Skip if already scraped
            
            # scraping other details 
            scrap_source = "Amazon"
            creation_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            scrapping_status = 1 if product_url != "N/A" else 0

            if scrapping_status:
                product = ProductDTO(
                    Scrap_Source_Identifier=scrap_source_identifier,
                    URL=clean_product_url,
                    Title=product_title,
                    Rating=product_rating,
                    location=location,
                    IsSponsored=is_sponsored,
                    Reviews=product_reviews,
                    Price=product_price,  
                    Scrap_Source=scrap_source,
                    Keywords=[keyword],
                    CreationDateTime=creation_datetime,
                    ScrappingStatus=scrapping_status
                )
                products.append(product)

        except Exception as e:
            print(f"Error extracting product details: {e}")
            continue
    
    return products

def decline_cookies(driver, page_number:int) -> None:
    try:
        # Attempt to find and click the cookies decline button
        cookies_decline_btn = driver.find_element(By.ID, "sp-cc-rejectall-link")
        if cookies_decline_btn:
            ActionChains(driver).click(cookies_decline_btn).perform()
            # print("Cookies declined.")
            with open('location_mismatch.log', 'a') as log_file:
                log_file.write(f"Cookies declined on page {page_number}.\n")
    except NoSuchElementException:
        # Handle case where cookies decline button is not found
        # print("Cookies decline button not found, proceeding without it.")
        with open('location_mismatch.log', 'a') as log_file:
            log_file.write(f"Cookies decline button not found, proceeding on page {page_number}.\n")

# Function to exit the sequence gracefully, ensuring driver shutdown
def perform_exit_sequence(msg: str, driver: uc.Chrome, exit_code: int = -1):
    print(msg)
    try:
        if driver:
            driver.quit()  # Attempt to quit the driver only if it's open
    except Exception as e:
        print(f"Error during driver quit: {e}")
    exit(code=exit_code)

#captcha check function
def check_for_captcha(driver: uc.Chrome, page_number:int):
    try:
        captcha_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Enter the characters you see')]")
        if captcha_element:
            print(f"CAPTCHA detected! on page {page_number}")
            # Play beep sound (frequency 1000 Hz, duration 500 ms)
            # winsound.Beep(1000, 500)
            return True
    except NoSuchElementException:
        # CAPTCHA not found, proceed as normal
        print(f"No CAPTCHA detected on page {page_number}")
        return False

def check_location(soup, page_number) -> bool:
    try:
        location_span = soup.find("span", attrs={"id": "glow-ingress-line1"})
        if location_span:
            location = location_span.text.strip()
            with open('location_mismatch.log', 'a') as log_file:
                if location == "Delivering to London EC4R":
                    # print(f"Location check passed: {location}")
                    log_file.write(f"Location check passed: {location} on page {page_number}\n")
                    return True
                else:
                    # print(f"Location is not 'Delivering to London EC4R'. Current location: {location}")
                    log_file.write(f"Location mismatch: {location} on page {page_number}\n")
                    return False
        else:
            print("Location information not found.")
            return False
    except Exception as e:
        print(f"Error checking location: {e}")
        return False

def save_page_source(keyword: str, page_number: int, page_source: str):
    # Create directory for the page source if it doesn't exist
    directory = os.path.join('page-source', keyword)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # File naming convention
    file_path = os.path.join(directory, f"{keyword}-{page_number}.html")
    
    # Write the page source to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(page_source)
    
    print(f"Page {page_number} source saved to {file_path}")

def is_next_button_enabled(soup):
    try:
        next_button = soup.find("a", {"class": "s-pagination-next"})
        if next_button and 's-pagination-disabled' in next_button.get('class', []):
            return False
        
        # If the button is found and is not disabled
        return next_button is not None
    except Exception as e:
        print(f"Error checking for next button: {e}")
        return False

def extract_product_range(soup):
    try:
        # Locate the product range element using its class
        range_element = soup.select_one(".a-section.a-spacing-small.a-spacing-top-small span")

        if range_element:
            product_range = range_element.text.strip()  # Extract the text content

            # Split the text by spaces to extract the range and total count
            product_range_parts = product_range.split()

            # Extract the start count and end count (first part of the string, split by '-')
            start_count, end_count = map(int, product_range_parts[0].split('-'))

            # Extract the total count (e.g., "over 2,000 results") and remove commas
            total_count = int(product_range_parts[-3].replace(',', ''))

            print(f"Start Count: {start_count}, End Count: {end_count}, Total Count: {total_count}")
            return start_count, end_count, total_count
        else:
            print("Could not find the product range element on this page.")
            return None, None, None

    
    except NoSuchElementException:
        print("Could not find the product range element on this page.")
        return None, None, None

def save_products_to_csv(page_number:int ,products: List[ProductDTO], filename: str = 'products.csv', append: bool = True):
    file_exists = os.path.isfile(filename)
    
    # Open the file in append or write mode based on the flag
    with open(filename, 'a' if append else 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Scrap_Source_Identifier', 'URL', 'Title', 'page_number','product_intake_method', 'Rating', 'Country', 'Reviews', 'Price', 'IsSponsored', 'Scrap_Source', 'Keywords', 'CreationDateTime', 'ScrappingStatus']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # If file does not exist, write the header
        if not file_exists:
            writer.writeheader()
        
        # Write each product as a row in the CSV
        for product in products:
            writer.writerow({
                'Scrap_Source_Identifier': product.Scrap_Source_Identifier,
                'URL': product.URL,
                'Title': product.Title,
                'Rating': product.Rating,
                'Country':product.location,
                'Reviews': product.Reviews,
                'Price': product.Price,
                'Intake_method':product.intake_method,
                'page_number':page_number,
                'IsSponsored':product.IsSponsored,
                'Scrap_Source': product.Scrap_Source,
                'Keywords': ', '.join(product.Keywords),
                'CreationDateTime': product.CreationDateTime,
                'ScrappingStatus': product.ScrappingStatus
            })
    print(f"Saved {len(products)} products to {filename}")

def traverse_pages(driver: uc.Chrome):
    page_number = 1
    while True:
        print(f"Scraping page {page_number}...")
        #check captcha 
        while check_for_captcha(driver, page_number):
            winsound.Beep(1000, 500)
            time.sleep(3)
        
        #cookies check 
        decline_cookies(driver,page_number)
        
        time.sleep(5)

        # Get the page source and save it to a file
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #saving to txt file 
        save_page_source(keyword, page_number, soup.prettify())
        
        #location check 
        if not check_location(soup,page_number):
            print(f"Location mismatch detected on page {page_number}. Skipping scraping for this page.")
            break
        
        #product range extractor
        start_count, end_count, total_count = extract_product_range(soup)
        
        products=extract_product_details_from_main_page(page_number,soup)
        # saving to csv before moving to another page 
        if products:
            save_products_to_csv(page_number,products, products_filename, append=True)
        else:
            print(f"No products found on page {page_number}.")
        
        #check for next button enable\disable
        if not is_next_button_enabled(soup):
            print("No 'Next' button found or it is disabled. Reached the last page or no further results.")
            break

        if start_count is not None and end_count is not None:
            # Check if we need to log or navigate to the next page

            if start_count > end_count or is_next_button_enabled(soup):
                
                # If start_count > end_count, log the warning
                if start_count > end_count:
                    print(f"Warning: Start count {start_count} is greater than end count {end_count}.")
                    with open('location_mismatch.log', 'a') as log_file:
                        log_file.write(f"Warning: Start count {start_count} > end count {end_count}. Exiting.\n")

                while True:
                    try:
                        # Scroll down to trigger lazy loading (if any)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                        # Re-locate and click the "Next" button for pagination
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next"))
                        )
                        next_button.click()

                        # Wait until the next button becomes stale (indicating page change)
                        WebDriverWait(driver, 10).until(EC.staleness_of(next_button))

                        # Increment the page number and log navigation
                        page_number += 1
                        print(f"Navigating to page {page_number}...")
                        break  # Break out of the retry loop if successful

                    except Exception as e:
                        print(f"Error navigating to next page: {e}. Retrying...")
                        time.sleep(2)

            else:
                print("No 'Next' button found or it is disabled. Reached the last page or no further results.")
                break
        


if __name__ == "__main__":
    # Instantiate a Chrome browser
    driver = uc.Chrome(use_subprocess=False, version_main=128)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 20)  # Explicit wait with a 20-second timeout
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    #ONE TIME FLOW  
    try:
        # Visit the target URL
        driver.get("https://www.amazon.co.uk")
        
        # Check for CAPTCHA before proceeding
        while check_for_captcha(driver,page_number=1):
            winsound.Beep(1000, 500)
            time.sleep(3)
            
        #cookies check 
        decline_cookies(driver,page_number=1)

        # Select Health & Personal Care from the dropdown
        dropdown = driver.find_element(By.CSS_SELECTOR, "select.nav-search-dropdown")
        select = Select(dropdown)
        select.select_by_visible_text('Health & Personal Care')

        # Search for the keyword
        search_box = driver.find_element(By.ID, "twotabsearchtextbox")
        search_box.send_keys(keyword)
        search_box.submit()

        # Select Health Care from the subcategory bar
        div_element = driver.find_element(By.ID, "nav-subnav")
        health_care_link = div_element.find_element(By.CSS_SELECTOR, "a[href='/health-care-medication/b/?ie=UTF8&node=66467031&ref_=sv_d_8']")
        health_care_link.click()
        
        # Perform the search again
        search_box = driver.find_element(By.ID, "twotabsearchtextbox")
        search_box.send_keys(keyword)
        search_box.submit()
        
        #LOOP FLOW:
        #traversal of pages 
        traverse_pages(driver)
        

    except Exception as e:
        print(f"An error occurred: {e}")
        perform_exit_sequence("An error occurred during the scraping process.", driver)

    finally:
        # Close the browser
        driver.quit()
