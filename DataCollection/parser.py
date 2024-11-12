import os
import logging
from bs4 import BeautifulSoup
import csv
import asyncio
import aiofiles  
import json
import re
logging.basicConfig(level=logging.DEBUG)

MAIN_FOLDER = "michelin_restaurants"

OUTPUT_FILE = "michelin_restaurants_data.tsv"

async def extract_restaurant_data(html_content, url):
    """
    Parses the HTML content of a restaurant page to extract relevant information asynchronously.
    
    Parameters:
        html_content (str): HTML content of the restaurant page.
        url (str): URL of the restaurant page for reference.
        
    Returns:
        dict: A dictionary with the extracted information.
    """
    soup = BeautifulSoup(html_content, "html.parser") #parse the HTML, making it easy to search for specific elements by class, tag, or ID.

    def extract_text(selector, attr=None):
        element = soup.select_one(selector)
        if element:
            return element[attr].strip() if attr else element.get_text(strip=True)
        return ""
    
async def extract_restaurant_data(html_content, url):
    """
    Parses the HTML content of a restaurant page to extract relevant information asynchronously.
    
    Parameters:
        html_content (str): HTML content of the restaurant page.
        url (str): URL of the restaurant page for reference.
        
    Returns:
        dict: A dictionary with the extracted information.
    """
    soup = BeautifulSoup(html_content, "html.parser")
# Initially we used structured JSON-LD data
    # Extract restaurant name
    try:
        restaurant_name = soup.find("meta", itemprop="name")["content"] #locate the meta tag and pulls the content
    except (TypeError, KeyError):
        restaurant_name = ""
    #logging.debug(f"restaurant_name: {restaurant_name}")

    # Extract address 
    try:
        ld_json_data = soup.find("script", type="application/ld+json").string #locate string tag
        data = json.loads(ld_json_data) #json string to py dictionary
        # now it's easy to access to this info
        address = data["address"]["streetAddress"]
        city = data["address"]["addressLocality"]
        postal_code = data["address"]["postalCode"]
        country = data["address"]["addressCountry"]
    except (TypeError, KeyError, json.JSONDecodeError):
        address = city = postal_code = country = ""
    #logging.debug(f"address: {address}, city: {city}, postal_code: {postal_code}, country: {country}")

    # Extract price range and cuisine type
    try:
        price_and_cuisine = soup.find_all("div", class_="data-sheet__block--text")[1].get_text(strip=True).split("·") # we look for div element and split the text based on the separator "·"
        price_range = price_and_cuisine[0].strip() if price_and_cuisine else ""
        cuisine_type = price_and_cuisine[1].strip() if len(price_and_cuisine) > 1 else ""
    except (IndexError, AttributeError):
        price_range = ""
        cuisine_type = ""
    #logging.debug(f"price_range: {price_range}, cuisine_type: {cuisine_type}")

    # Extract description
    description = ""
    try:

        #description = data["review"]["description"] # in json is easy
        # Update: apparently json truncate by default
        description_div = soup.find('div', class_='data-sheet__description')
        if description_div:
            description = description_div.get_text(strip=True)
    except AttributeError:
        description = ""  # Set to empty if description is missing
    #logging.debug(f"description: {description}")


    # Extract facilities and services
    facilities_services = [] # list of servicies
    try:
        facilities_list = soup.select("div.restaurant-details__services ul li") #find li tag
        facilities_services = [facility.get_text(strip=True) for facility in facilities_list] # retrieve text under each specific section

    except AttributeError:
        facilities_services = []
    #logging.debug(f"facilities_services: {facilities_services}")

    # Extract credit cards accepted
    credit_cards = []
    try:
        credit_cards_section = soup.find("div", class_="list--card").find_all("img")  # from image sources
        credit_cards = [card["data-src"].split('/')[-1].split('-')[0] for card in credit_cards_section] # parse image URLs and isolates each credit card’s name
    except AttributeError:
        credit_cards = []
    #logging.debug(f"credit_cards: {credit_cards}")

    # Extract phone number
    try:
        phone_number = data["telephone"] #json metadata
    except KeyError:
        phone_number = ""
    #logging.debug(f"phone_number: {phone_number}")

    # Extract geographic coordinates from iframe src
    latitude, longitude = "", ""
    try:
        iframe_src = soup.select_one("div.google-map__static iframe")["src"]
        coordinates = re.search(r"q=([-.\d]+),([-.\d]+)", iframe_src) # using regex to find latitude and logitude in the iframe URL
        if coordinates:
            latitude, longitude = coordinates.groups()
    except (TypeError, KeyError, AttributeError):
        pass
    #logging.debug(f"latitude: {latitude}, longitude: {longitude}")

    # Extract Restaurant official link
    website_link = ""
    try:
        # div containing the website link
        container_div = soup.find('div', class_='collapse__block-item link-item')
        if container_div:
            # <a> tag within this div
            link_tag = container_div.find('a', class_='link js-dtm-link')
            if link_tag and link_tag.has_attr('href'):
                website_link = link_tag['href']
    except AttributeError:
        logging.error("Error finding website link.")

    #logging.debug(f"website_link: {website_link}")


# Initialize default opening hours, as NAs cause sometimes this info is not avaible
    opening_hours = {
        "Monday": "NA",
        "Tuesday": "NA",
        "Wednesday": "NA",
        "Thursday": "NA",
        "Friday": "NA",
        "Saturday": "NA",
        "Sunday": "NA"
    }

    # regex pattern for validating time ranges (e.g., "12:00-14:30")
    time_pattern = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}$")

    # List of valid weekday names
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    try:
        hours_sections = soup.select("div.open__time.d-flex") #Locate each section
        for hours_section in hours_sections:
            day_element = hours_section.select_one("div.col-6.col-lg-5 .open__time-hour") #  Extract day
            if day_element:
                day_text = day_element.get_text(strip=True)
                day_match = re.match(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", day_text) # ensuring it's valid
                if day_match:
                    day = day_match.group(0)  # day name
                    #logging.debug(f"Extracted day: {day}")
                else:
                    logging.warning(f"Invalid or malformed day entry: '{day_text}'")
                    continue  # Skip invalid day name
            else:
                logging.debug("Day element not found")
                continue  # Skip if day is missing

            if day in opening_hours:
                time_elements = hours_section.select("div.col-6.col-lg-7 div") # times for each valid day
                unique_times = sorted(set(
                    time.get_text(strip=True) for time in time_elements
                    if time_pattern.match(time.get_text(strip=True))
                )) # only way to parsing error were strings kept being concatenated when two times were avaible
                opening_hours[day] = ", ".join(unique_times) if unique_times else "closed"
                #logging.debug(f"{day}: {opening_hours[day]}")
    except AttributeError as e:
        logging.error(f"Error parsing opening hours: {e}")
        pass  # Keep 'NA' values if parsing fails

    # Log final opening hours
    #for day, hours in opening_hours.items():
        #logging.debug(f"{day}: {hours}")



    # Return all extracted information as a dictionary
    restaurant_data = {
        "restaurant_name": restaurant_name,
        "address": address,
        "city": city,
        "postal_code": postal_code,
        "country": country,
        "price_range": price_range,
        "cuisine_type": cuisine_type,
        "description": description,
        "facilities_services": ", ".join(facilities_services), # due to the structure we had to use .join for compatibility to output file 
        "credit_cards": ", ".join(credit_cards),  
        "phone_number": phone_number,
        "latitude": latitude,
        "longitude": longitude,
        "monday_hours": opening_hours.get("Monday", "closed"),
        "tuesday_hours": opening_hours.get("Tuesday", "closed"),
        "wednesday_hours": opening_hours.get("Wednesday", "closed"),
        "thursday_hours": opening_hours.get("Thursday", "closed"),
        "friday_hours": opening_hours.get("Friday", "closed"),
        "saturday_hours": opening_hours.get("Saturday", "closed"),
        "sunday_hours": opening_hours.get("Sunday", "closed"),
        "url_micheline": url,
        "url": website_link
    }

    # Debug log for each extracted field
    #for key, value in restaurant_data.items():
        #logging.debug(f"{key}: {value}")

    return restaurant_data

async def parse_all_restaurants(batch_size=100): # batch_size controls the number of files processed concurrently
    """
    Parses all HTML files in the michelin_restaurants directory asynchronously and saves extracted data to a TSV file.
    """
    logging.info("Starting to parse all restaurants.")

    async with aiofiles.open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as tsvfile:
        fieldnames = [
            "restaurant_name", "address", "city", "postal_code", "country",
            "price_range", "cuisine_type", "description", "facilities_services",
            "credit_cards", "phone_number", "latitude", "longitude",
            "monday_hours", "tuesday_hours", "wednesday_hours", "thursday_hours",
            "friday_hours", "saturday_hours", "sunday_hours", "url_micheline", "url",
        ]
        await tsvfile.write("\t".join(fieldnames) + "\n")
        logging.debug("TSV file header written.")

        # Gather all HTML files 
        tasks = []
        for folder_name in os.listdir(MAIN_FOLDER):
            folder_path = os.path.join(MAIN_FOLDER, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(".html"):
                        file_path = os.path.join(folder_path, file_name)
                        tasks.append(process_file(file_path))

        # process filew in batches
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            logging.info(f"Processing batch {i // batch_size + 1} with {len(batch)} files.")
            results = await asyncio.gather(*batch) 

            # Write results 
            for row in results:
                # Convert each field to a string and handle None values as empty strings
                output_row = [str(row.get(field, "")).replace("\n", " ") for field in fieldnames]
                await tsvfile.write("\t".join(output_row) + "\n")

    logging.info(f"Data extraction completed. Results saved to {OUTPUT_FILE}")

async def process_file(file_path):
    """
    Reads the HTML content of a file asynchronously, extracts data, and returns a dictionary.
    """
    async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
        lines = await file.readlines()
        url = lines[0].replace("<!-- URL: ", "").replace(" -->", "").strip()
        html_content = "".join(lines[1:])

    #logging.debug(f"Processing file: {file_path}, URL: {url}")
    restaurant_data = await extract_restaurant_data(html_content, url)
    return restaurant_data

#if __name__ == "__main__": 
    #asyncio.run(parse_all_restaurants()) #call all functions
