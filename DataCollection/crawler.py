from bs4 import BeautifulSoup # parse and navigate the HTML content of web pages
import logging #for debugging
import requests # HTTP requests to retrieve web page data
import aiohttp #chronous version of request
import asyncio #to manage asynchronous tasks
import os
import time #just to flex how fast the process is
import random

# chatgpt trick to not be identified as bot: see "AmazonCloudFront_WasScared.jpg" for clarifications
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://google.com",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

logging.basicConfig(level=logging.DEBUG) #configure logging to output messages that will serve us as DEBUG (there were a few to undertstand how to retrive those data)

# Overview
"""
1. Collect URLs of Michelin restaurants in Italy.
2. Download HTML pages for each restaurant
"""


def get_michelin_urls():
    """
    Collects URLs of Michelin restaurants in Italy and saves them in a .txt file.
    """
    base_url = "https://guide.michelin.com/en/it/restaurants/page/"
    restaurant_urls = []
    
    for page in range(1, 103): #102 pages
        logging.debug(f"Analyzing page {page}")
        try:
            response = requests.get(base_url + str(page)) #send get request to our url, for instance "https://guide.michelin.com/en/it/restaurants/page/102"
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch page {page}: {e}") #log error and skip to next page
            continue


        soup = BeautifulSoup(response.text, 'lxml') #parse HTML content
       
       # Here we need to introduce some basic HTML syntax 
        for restaurant in soup.find_all('a', class_='link'): #Finds all anchor (<a>) tags with the class link 
            url = "https://guide.michelin.com" + restaurant['href'] #construct url
            # does the url works? ex: "https://guide.michelin.com/en/veneto/cortina-d-ampezzo/restaurant/el-brite-di-larieto", going on Google, yes it does!
            # While first running the code it, it was saving also unrelated links like "https://guide.michelin.com/en/hotels"
            if "/restaurant/" in url: #valid link contain "/restaurant/" 
                restaurant_urls.append(url)
                #logging.debug(f"Found restaurant URL: {url}")
    
    # Save to .txt (it was requested like this but just returning URLs was easier)
    logging.info("Saving URLs to michelin_urls.txt")
    with open('DataCollection/michelin_urls.txt', 'w') as f:
        for url in restaurant_urls:
            f.write(f"{url}\n")

    logging.info("URL collection completed.") # everything ok

async def fetch_and_save_html(session, url, folder, filename, headers): #Asynchronous Downloading to handle multiple requests concurrently
    """
    Asynchronously fetches the HTML content of a URL and saves it to a file.
    
    Parameters:
        session (aiohttp.ClientSession): The HTTP session to reuse for requests.
        url (str): The URL to fetch.
        folder (str): The directory to save the HTML file in.
        filename (str): The name of the HTML file to save.
    """
    try:
        async with session.get(url, headers=headers) as response: # this allow to to keep the session open for multiple requests
            if response.status == 403: # we add dedicated debug to "AmazonCloudFront_WasScared.jpg" error
                logging.error(f"Access denied for {url}")
                return

            response.raise_for_status()  
            html_content = await response.text()

            html_content = f"<!-- URL: {url} -->\n" + html_content # we leave info regarding the url that will be usefull later

            # Save HTML content to the specified file
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            #logging.debug(f"Saved HTML to {filepath}")
    except Exception as e: # a single failed request doesn't stop the script
        logging.error(f"Failed to fetch {url}: {e}")


async def download_html_async(urls_file='DataCollection/michelin_urls.txt', batch_size=20):
    """
    Asynchronously downloads HTML content for each URL in the .txt file in batches.
    
    Parameters:
        urls_file (str): The path to the text file containing the URLs.
        batch_size (int): Number of URLs per folder, default is 20.
    """
    with open(urls_file, 'r') as file:
        restaurant_urls = [line.strip() for line in file]

    async with aiohttp.ClientSession() as session: # Manages all requests
        tasks = []
        for i, url in enumerate(restaurant_urls):
            folder = f"page_{(i // batch_size) + 1}"
            filename = f"restaurant_{i + 1}.html"

            headers = get_random_headers() # periodically getting new headers to not get caught by bot

            # appends tasks for each URL
            tasks.append(fetch_and_save_html(session, url, folder, filename,headers)) #tasks enable concurrent downloads within batches
            
            if (i + 1) % batch_size == 0 or (i + 1) == len(restaurant_urls): # for every batch_size URLs
                logging.info(f"Downloading batch {i // batch_size + 1}")
                await asyncio.gather(*tasks) # runs the batch concurrently
                tasks.clear()  # Clear completed tasks to manage memory

    logging.info("All HTML downloads completed.")

'''

def download_html(urls_file='michelin_urls.txt'):
    """
    Downloads the HTML content for each restaurant URL from the .txt
    """

    with open(urls_file, 'r') as file:
        urls = file.readlines()
    
    for i, url in enumerate(urls):
        url = url.strip() #clean url
        logging.debug(f"Downloading HTML for {url}")
        
        try:
            response = requests.get(url) #request to download
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download {url}: {e}") # to let us analyze if something goes wrong
            continue
        
        folder = f"page_{(i // 20) + 1}"  # a folder for each page for cleaness
        os.makedirs(folder, exist_ok=True)
        
        filepath = os.path.join(folder, f"restaurant_{i}.html")
        logging.debug(f"Saving HTML to {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as html_file:
            html_file.write(response.text)

    logging.info("HTML download completed.")

'''


if __name__ == "__main__":
    #get_michelin_urls()
    #download_html()  # synchronous download and slow option, it was taking forever
    
    start_time = time.time() #only for flexing :)
    asyncio.run(download_html_async())  # Async download with batch processing
    logging.info(f"Total download time: {time.time() - start_time} seconds") # <3
