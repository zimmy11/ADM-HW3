import streamlit as st
import pandas as pd
import json
import re
from collections import defaultdict
from functions import (
    rank_documents,  
    remove_stopwords,
    apply_stemming,
    remove_punc,
    apply_lemmatization,
    update_inverted_index
)
import nltk
from nltk.corpus import stopwords

# Initial setup
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Load the dataset
df = pd.read_csv('michelin_restaurants_data.csv')  # Replace with your actual dataset file path

# Preprocess text columns in the dataset
df['no_stopwords'] = df['description'].apply(remove_stopwords)
df['no_stopwords_and_punct'] = df['no_stopwords'].apply(remove_punc)
df['no_stpwrd_punc_and_stemmed'] = df['no_stopwords_and_punct'].apply(apply_stemming)
df['lemmatized_text'] = df['no_stopwords_and_punct'].apply(apply_lemmatization)
df['cleaned_text'] = df['lemmatized_text'].str.replace(r'\s+', ' ', regex=True).str.strip()
df['cleaned_text'] = df['cleaned_text'].str.replace(r'http\S+|www\S+|https\S+', '', regex=True)
df['cleaned_text'] = df['cleaned_text'].str.replace(r'\S+@\S+', '', regex=True)
df['restaurant_name'] = df['restaurant_name'].str.split('–|-').str[0].str.strip()
df['document_id'] = df.index

# Vocabulary and inverted index
vocab = {}
current_term_id = 0
inverted_index = defaultdict(list)

# Create vocabulary and inverted index
for _, row in df.iterrows():
    doc_id = row['document_id']
    words = row['cleaned_text'].split()
    unique_words = set(words)
    for word in unique_words:
        if word not in vocab:
            vocab[word] = current_term_id
            current_term_id += 1
        term_id = vocab[word]
        inverted_index[term_id].append(doc_id)

# Save vocabulary and inverted index for query processing
vocab_df = pd.DataFrame(list(vocab.items()), columns=['word', 'term_id'])
vocab_df.to_csv('vocabulary.csv', index=False)
with open('inverted_index.json', 'w') as f:
    json.dump({str(k): v for k, v in inverted_index.items()}, f)

# Load the inverted index and vocabulary
with open("inverted_index.json", 'r', encoding='utf-8') as file:
    inverted_index = {int(k): v for k, v in json.load(file).items()}
vocab = dict(zip(vocab_df['word'], vocab_df['term_id']))
print("Vocabulary terms:", list(vocab.keys())[:20])  # Check if terms are as expected

def preprocess_query(query):
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)  
    query_terms = [word for word in query.split() if word not in stop_words] 
    term_ids = [vocab.get(word) for word in query_terms if word in vocab]
    print(f"Query Terms: {query_terms}")
    print(f"Term IDs: {term_ids}")
    return term_ids  

def search_restaurants(query):
    term_ids = preprocess_query(query)
    if not term_ids:
        print("No matching terms found in the vocabulary.")
        return pd.DataFrame()  

    # Check if each term ID has corresponding documents in the inverted index
    for term_id in term_ids:
        if term_id not in inverted_index:
            print(f"Term ID {term_id} not found in inverted index for term '{vocab_df[vocab_df['term_id'] == term_id]['word'].values[0]}'")
    
    matching_docs = set(inverted_index.get(term_ids[0], []))  
    for term_id in term_ids[1:]:
        matching_docs.intersection_update(inverted_index.get(term_id, [])) 

    if matching_docs:
        results = df[df['document_id'].isin(matching_docs)][['restaurant_name', 'address', 'description', 'url']]
        return results.head(5)
    else:
        print("No documents match all query terms.")
        return pd.DataFrame()  

# Test the search with debug information
query = "modern cuisine restaurant"
results = search_restaurants(query)
print(results)
# We create a copy of the dataframe because we dont want to change in place the original DataFrame
df_tfidf = df.copy()
# We store the words mapping in a DataFrame 
vocabulary = pd.read_csv("vocabulary.csv")

# We load in a Python dictionary the inverted_index creted previously
with open("inverted_index.json", 'r', encoding='utf-8') as file:
    inverted_index = json.load(file)
updated_inverted_index = update_inverted_index(df_tfidf, inverted_index, vocabulary)
with open("updated_inverted_index.json", "w") as file:
    json.dump(updated_inverted_index, file)

# Streamlit UI
st.title("Restaurant Search Engine")

# Input Query
query = st.text_input("Enter your query:", value="MODERN; Seasonal CUISINE. DISH")

# Select the number of top results to display (k value)
k = st.slider("Select the number of top results (k):", min_value=1, max_value=20, value=5)

# Search and display results
if st.button("Search"):
    # Query preprocessing
    query_series = pd.Series(query)
    query_series = query_series.apply(remove_stopwords).apply(apply_stemming).apply(remove_punc).apply(apply_lemmatization)
    query_preprocessed = query_series.iloc[0]

    # Convert query words to term IDs using the vocabulary
    query_term_ids = [vocab.get(word) for word in query_preprocessed.split() if word in vocab]
    
    # Check if valid terms were found
    if query_term_ids:
        # Convert term IDs back to words for compatibility with `rank_documents`
        reconstructed_query = " ".join([word for word, term_id in vocab.items() if term_id in query_term_ids])
        
        try:
            # Rank documents based on the processed query and selected top-k
            top_k_documents = rank_documents(reconstructed_query, inverted_index, df, vocabulary, k)
            
            # Display top-k results in Streamlit
            if not top_k_documents.empty:
                st.write(f"Top {k} Results:")
                st.write(top_k_documents)
            else:
                st.warning("No matching restaurants found.")
        except Exception as e:
            st.error(f"Error in ranking function: {e}")
    else:
        st.warning("No valid terms found in query based on vocabulary.")
