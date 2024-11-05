from DataCollection.crawler import get_michelin_urls, download_html_async
from DataCollection.parser import parse_all_restaurants
from DataCollection.organize_folders import organize_folders
import time
import logging
import asyncio


def run_pipeline():

    print("Collecting URls...")

    start_time = time.time()

    get_michelin_urls()

    logging.info(f"Time to collect urls: {time.time() - start_time} seconds") # <3

    print("Downloading HTML files...")

    start_time = time.time() #only for flexing :)

    asyncio.run(download_html_async())  # Async download with batch processing
    
    logging.info(f"Total download time: {time.time() - start_time} seconds") # <3


    print("Downloading HTML files part 2...")

    start_time = time.time() #only for flexing :)

    asyncio.run(download_html_async())  # Async download with batch processing
    
    logging.info(f"Total download time: {time.time() - start_time} seconds") # <3

    print("Organizing Folders")
    
    organize_folders() #Cause I am dumb I forgot to do it 

    print("Parsing HTML files...")

    start_time = time.time() #only for flexing :)

    parse_all_restaurants()

    logging.info(f"Total parsing time: {time.time() - start_time} seconds") # <3

#run_pipeline()