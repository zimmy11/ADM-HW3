import math
from sklearn.feature_extraction.text import CountVectorizer
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def compute_smallest_path(list):
    """
    Returns the best path to collect all the packages located
    or prints "NO" if its not possible

    Args:
        list (nd.array): The list containing the coordinates ordered based on the distance from the starting position
    
    Returns:
        Null: Prints "YES" or "NO", and if "YES" it prints the smallest path to collect all the packages ordered lexicographically 
    
    
    """

    # Init the starting coordinates
    current_coordinate = (0, 0)
    # Init the list that will contain the Path
    result = []

    # Iterate over the number of packages
    for target_x, target_y in list:
        # Stop the iteration when next package cannot be reached with "U" and "R"
        if (target_x < current_coordinate[0]) or (target_y < current_coordinate[1]):
            print("NO")
            return
        # Compute the number of Steps we have to make to reach the next package in the list 
        # summing the absolute value of the differences between the current coordinates and 
        # the target coordinates 
        distance_from_next = target_x - current_coordinate[0] + target_y - current_coordinate[1]

        # Loop over this distance
        for _ in range(distance_from_next):

            # We give to return the best path ordered lexigraphically so 
            # we prefer appending the "R" to the result if they match the condition
            if current_coordinate[0] < target_x:
                # We update our coordinates because we have moved right
                current_coordinate = (current_coordinate[0] + 1, current_coordinate[1])
                result.append("R")
                continue
            # Otherwise we move upper if our Y coordinate is lower than the target one
            if current_coordinate[1] < target_y:
                # We update the current coordinates after the step and we append to the result "U"
                current_coordinate = (current_coordinate[0] , current_coordinate[1] + 1)
                result.append("U")

    # After the loop we print "YES", bacause if the loop ended without 
    # entering if the first if we are able to collect all the packages 
    print("YES")
    # In the end we print all the elements in the 'result' list
    # representing the best path to collect all the packages
    print("".join(result))



def extended_compute_smallest_path(list):
    """
    Returns the best path to collect all the packages located

    Args:
        list (nd.array): The list containing the coordinates ordered based on the distance from the starting position
    
    Returns:
        Null: Prints "YES" and prints the smallest path to collect all the packages ordered lexicographically 
    
    """

    # Init the starting coordinates
    current_coordinate = (0, 0)
    # Init the list that will contain the Path
    result = []

    # Iterate over the number of packages
    for target_x, target_y in list:
        # Compute the number of Steps we have to make to reach the next package in the list 
        # summing the absolute value of the differences between the current coordinates and 
        # the target coordinates 
        distance_from_next = abs(target_x - current_coordinate[0]) + abs(target_y - current_coordinate[1])

        # Loop over this distance
        for _ in range(distance_from_next):

            # Checks if the Y coordinate of our target package is under our current position 
            if current_coordinate[1] > target_y:
                # We update the current coordinates after the step and we append to the result "D"
                current_coordinate = (current_coordinate[0] , current_coordinate[1] - 1)
                result.append("D")

            # Checks if the X coordinate of our target package is on the left of our current position 
            if current_coordinate[0] > target_x:
                # We update the current coordinates after the step and we append to the result "L"
                current_coordinate = (current_coordinate[0] - 1, current_coordinate[1])
                result.append("L")                            

            # We give to return the best path ordered lexigraphically so 
            # we prefer appending the "R" to the result if they match the condition
            if current_coordinate[0] < target_x:
                # We update our coordinates because we have moved right
                current_coordinate = (current_coordinate[0] + 1, current_coordinate[1])
                result.append("R")
                continue
            # Otherwise we move upper if our Y coordinate is lower than the target one
            if current_coordinate[1] < target_y:
                # We update the current coordinates after the step and we append to the result "U"
                current_coordinate = (current_coordinate[0] , current_coordinate[1] + 1)
                result.append("U")

    # After the loop we print "YES", bacause if the loop ended without 
    # entering if the first if we are able to collect all the packages 
    print("YES")
    # In the end we print all the elements in the 'result' list
    # representing the best path to collect all the packages
    print("".join(result))



def update_inverted_index(df, inverted_index, vocabulary):
    """
    Computes the updated version of the inverted index returning a dictionary that assigns to each term_id 
    the list of tuples (doc_id, tf-idf_score) 

    Args:
        df (DataFrame): The DataFrame containing the document text.
        inverted_index (dict): The previous inverted index mapping terms to documents.
        vocabulary (DataFrame): A DataFrame mapping term IDs to their corresponding words.

    
    Returns:
       dict: The updated inverted index with TF-IDF scores. 
    
    """
    # Total number of documents in the DataFrame.   
    total_documents = df.shape[0]

    # Iterate over each term in the inverted index to calculate IDF scores.
    for term_id, documents in inverted_index.items():
        # Calculate the inverse document frequency (IDF) for the term.
        documents_frequency = math.log(total_documents / (1 + len(documents)))

        # Get the word corresponding to the term ID from the vocabulary DataFrame.
        word = str(vocabulary.loc[vocabulary["term_id"] == int(term_id), "word"].iloc[0])
        idf_scores = []

        # Iterate over each document containing the term to compute TF-IDF.
        for i in range(len(documents)):

            # Get the document ID.
            doc_id = documents[i]

            # We get the description of that document 
            doc = df.iloc[int(doc_id)]["cleaned_text"]
            
            # We compute the Tf score
            tf_score = doc.count(word) / (len(doc.split()))

            # We compute the Idf score mutiplying the idf_score and the tf score
            idf_score = documents_frequency * tf_score

            # We append the tuple to the list we will assign to that term
            idf_scores.append((doc_id, idf_score))

        inverted_index[term_id] = idf_scores

    return inverted_index


def cosine_similarity(query, document):
    """
    Calculates the cosine similarity between a query vector and a document vector.

    Args:
        query (list of tuples): The TF-IDF vector for the query, with (term_id, tf-idf score).
        document (list of tuples): The TF-IDF vector for the document, with (term_id, tf-idf score).

    Returns:
        float: The cosine similarity score between the query and document.
    """

    product = 0

    # Calculate the dot product of the query and document vectors.
    for score in query:
        for index in document:

            # We wanna compute the product only of the tf-idf scores (score[1])
            # Where the term_id (score[0]) matches
            if score[0] == index[0]:  
                product += score[1] * index[1]

    # We compute the Norms 
    norm1 = math.sqrt(sum(val[1] ** 2 for val in query))
    norm2 = math.sqrt(sum(val[1] ** 2 for val in document))
    
    # We check that the norms are not 0 (if that we return 0)
    if norm1 == 0 or norm2 == 0:
        return 0  
    
    return product / (norm1 * norm2)


def compute_tfidf_query(query, inverted_index, df, vocabulary):
    """
    Computes the TF-IDF scores for a given query.

    Args:
        query (str): The query string containing words.

        inverted_index (dict): The inverted index mapping terms to document IDs and their TF-IDF scores.

        df (DataFrame): The DataFrame containing the documents.

        vocabulary (DataFrame): A DataFrame mapping term IDs to words.
    
    Returns:

        list: A list of tuples where each tuple contains a term_id and its corresponding TF-IDF score.
    """

    # Shape of the DataFrame used to determine the IDF score
    total_documents = df.shape[0]

    tfidf_scores = []

    # Iterate through each word in the query and calculate the TF-IDF score for each term.
    for word in query.split():

        # We get the term_id through the vocabulary df
        term_id = str(vocabulary[vocabulary["word"] == word]["term_id"].iloc[0])

        # Compute the term frequency score
        tf = query.count(word) / len(query.split())
        
        # Compute the Inverted Document Frequency Score
        idf = math.log(total_documents / 1 + len(inverted_index[term_id]))

        tf_idf = tf * idf

        # We append the tuple (term_id,TF_IDF) to the list
        tfidf_scores.append((term_id,tf_idf))

    return tfidf_scores


def rank_documents(query, inverted_index, df, vocabulary, k):

    """
    Ranks documents based on cosine similarity to a given query.

    Args:
        query (str): The query string.
        inverted_index (dict): The inverted index mapping terms to document IDs and their TF-IDF scores.
        df (DataFrame): The DataFrame containing the documents.
        vocabulary (DataFrame): A DataFrame mapping term IDs to words.
        k (int): The number of top-ranked documents to return.

    Returns:
        DataFrame: A DataFrame containing the top-k ranked documents with similarity scores.
    """   

    # Compute TF-IDF scores for the query.
    query_tfidf_scores = compute_tfidf_query(query, inverted_index, df, vocabulary)

    # Init the dictionary
    document_tfidf = {}

    # Get the term_ids from the query's TF-IDF scores
    term_ids = [x[0] for x in query_tfidf_scores]

    # Iterate through the terms in the query to populate the document TF-IDF vectors
    for word in term_ids:
        
        # Iterate over the list of tuples of the updated inverted index
        for entry in inverted_index[word]:
            # We extract doc_id and tf_idf scores
            doc_id = entry[0]
            tf_idf = entry[1]

            if doc_id not in document_tfidf:
                document_tfidf[doc_id] = []

            # We append to the new dictionary the tuple where 
            # the key is the doc_id and the values is represented by a list
            # of tuples with (term_id, tfidf_score) of the terms in the query that appear in the document
            document_tfidf[doc_id].append((word, tf_idf))
    
    # Calculate the cosine similarity between the query and each document.
    similarities = []
    for doc_id, doc_vector in document_tfidf.items():
        sim = cosine_similarity(query_tfidf_scores, doc_vector)
        similarities.append((doc_id, sim))

    # Rank documents based on their similarity score.
    ranked_documents = sorted(similarities, key=lambda x: x[1], reverse=True)

    # Select the top-k ranked documents.
    top_k_values = ranked_documents[:k]
    
    # We create a copy of the DataFrame with only the K indices that have the highest cosine similarity
    documents_best_k = df.iloc[[top_k_index[0] for top_k_index in top_k_values]].copy()
    
    # Add a column for similarity scores.
    documents_best_k["similarity_score"] = [values[1] for values in top_k_values]
    
    
    return documents_best_k[["restaurant_name", "address", "description", "url", "similarity_score"]]
        

def visualize_frequency(df):
    """
    Plots the bar plot of the most frequent bi-grams of the text before and after preprocessing
    
    Args (DataFrame): Input DataFrame

    """
    # Initialize the CountVectorizer for bi-grams (ngram_range=(2, 2))
    vectorizer_bigrams = CountVectorizer(ngram_range=(2, 2))
    X_bigrams = vectorizer_bigrams.fit_transform(df['description'].dropna())

    # Sum the occurrences of each bi-gram
    sum_bigrams = X_bigrams.sum(axis=0)
    bigrams_freq = [(word, sum_bigrams[0, idx]) for word, idx in vectorizer_bigrams.vocabulary_.items()]
    bigrams_freq = sorted(bigrams_freq, key=lambda x: x[1], reverse=True)[:20]

    # Get the bi-grams and their counts
    bigrams, bigram_counts = zip(*bigrams_freq)

    # Initialize the CountVectorizer for bigrams of the preprocessed text
    vectorizer_preprocessed = CountVectorizer(ngram_range=(2, 2), stop_words = "english")
    X_bigrams_preprocessed = vectorizer_preprocessed.fit_transform(df['cleaned_text'].dropna())

    # Sum the occurrences of each bi-gram
    sum_unigrams = X_bigrams_preprocessed.sum(axis=0)
    bigrams_freq_preprocessed = [(word, sum_unigrams[0, idx]) for word, idx in vectorizer_preprocessed.vocabulary_.items()]
    bigrams_freq_preprocessed = sorted(bigrams_freq_preprocessed, key=lambda x: x[1], reverse=True)[:20]

    # Get the bigrams preprocessed and their counts
    bigrams_preprocessed, bigram_preprocessed_counts = zip(*bigrams_freq_preprocessed)

    # Create a palette through seaborn
    palette = sns.color_palette("coolwarm", as_cmap=True)


    # Create subplots (1 row, 2 columns)
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    # Plot the bi-grams
    axes[0].bar(bigrams, bigram_counts, color=palette(np.linspace(0, 1, len(bigrams))))
    axes[0].set_xticklabels(bigrams, rotation=90)
    axes[0].set_title('Before Preprocessing')



    # Plot the unigrams
    axes[1].bar(bigrams_preprocessed, bigram_preprocessed_counts, color="lightgreen")
    axes[1].set_xticklabels(bigrams_preprocessed, rotation=90)
    axes[1].set_title('After Preprocessing')

    fig.suptitle('Top Bi-grams', fontsize=16)



    # Show the plots
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    plt.show();