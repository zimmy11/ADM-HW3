from DataCollection.crawler import get_michelin_urls, download_html_async
from DataCollection.parser import parse_all_restaurants
from DataCollection.organize_folders import organize_folders
import time
import logging
import asyncio
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import math

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

def update_inverted_index(df, inverted_index, vocabulary):
    total_documents = df.shape[0]

    for term_id, documents in inverted_index.items():
        documents_frequency = math.log(total_documents / (1 + len(documents)))
        word = str(vocabulary.loc[vocabulary["term_id"] == int(term_id), "word"].iloc[0])
        idf_scores = []

        for i in range(len(documents)):
            doc_id = documents[i]
            doc = df.iloc[int(doc_id)]["cleaned_text"]
            
            tf_score = doc.count(word) / (len(doc.split()))
            idf_score = documents_frequency * tf_score
            idf_scores.append((doc_id, idf_score))

        inverted_index[term_id] = idf_scores
    return inverted_index

def cosine_similarity(query, document):
    product = 0
    for score in query:
        for index in document:
            if score[0] == index[0]:  
                product += score[1] * index[1]
        
    norm1 = math.sqrt(sum(val[1] ** 2 for val in query))
    norm2 = math.sqrt(sum(val[1] ** 2 for val in document))
    
    if norm1 == 0 or norm2 == 0:
        return 0  
    return product / (norm1 * norm2)


def compute_tfidf_query(query, inverted_index, df, vocabulary):
    total_documents = df.shape[0]
    tfidf_scores = []

    for word in query.split():
        term_id = str(vocabulary[vocabulary["word"] == word]["term_id"].iloc[0])
        tf = query.count(word) / len(query.split())
        idf = math.log(total_documents / 1 + len(inverted_index[term_id]))
        tf_idf = tf * idf
        tfidf_scores.append((term_id,tf_idf))

    return tfidf_scores

def rank_documents(query, inverted_index, df, vocabulary):
    query_tfidf_scores = compute_tfidf_query(query, inverted_index, df, vocabulary)


    document_tfidf = {}
    term_ids = [x[0] for x in query_tfidf_scores]
    for word in term_ids:

        for entry in inverted_index[word]:
            doc_id = entry[0]
            tf_idf = entry[1]

            if doc_id not in document_tfidf:
                document_tfidf[doc_id] = []
            document_tfidf[doc_id].append((word, tf_idf))
    similarities = []
    for doc_id, doc_vector in document_tfidf.items():
        sim = cosine_similarity(query_tfidf_scores, doc_vector)
        similarities.append((doc_id, sim))


    ranked_documents = sorted(similarities, key=lambda x: x[1], reverse=True)
    
    return ranked_documents
   






    


