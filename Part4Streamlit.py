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
    update_inverted_index,
    rank_new_score
)
import nltk
from nltk.corpus import stopwords
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, MeasureControl, LocateControl
from streamlit_folium import st_folium

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
st.title("Restaurant Search Engine: Display on Map")

# Input Query
query = st.text_input("Enter your query:", value="MODERN; Seasonal CUISINE. DISH")

# Select the number of top results to display (k value)
k = st.slider("Select the number of top results (k):", min_value=1, max_value=20, value=5)

# Select facilities and cuisine type requirements
facilities_rq = st.multiselect(
    "Select Facilities:",
    options=[
        'Air conditioning', 'Terrace', 'Garden or park', 'Car park',
        'Great view', 'Wheelchair access', 'Interesting wine list',
        'Counter dining', 'Restaurant offering vegetarian menus', 'Brunch'
    ]
)

cuisine_type_rq = st.multiselect(
    "Select Cuisine Type:",
    options=[
        'Modern Cuisine', 'Italian Contemporary', 'Seafood', 'Creative',
        'Mediterranean Cuisine', 'Farm to table', 'Traditional Cuisine',
        'Seasonal Cuisine', 'Japanese', 'Fusion'
    ]
)

def create_restaurant_map(data, output_map="restaurants_map.html"):
    # Ensure latitude and longitude are numeric
    data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
    data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
    
    data = data.dropna(subset=['latitude', 'longitude'])  # Drop rows with missing coordinates

    # Center the map
    avg_lat = data['latitude'].mean()
    avg_lon = data['longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6, control_scale=True)

    # Add plugins
    marker_cluster = MarkerCluster().add_to(m)
    minimap = MiniMap().add_to(m)
    HeatMap([[row['latitude'], row['longitude']] for _, row in data.iterrows()]).add_to(m)
    m.add_child(MeasureControl())
    LocateControl().add_to(m)

    # Price range color mapping
    price_color_mapping = {
        "€": "green",
        "€€": "blue",
        "€€€": "orange",
        "€€€€": "red"
    }

    # Pop-up HTML creation
    def create_popup_html(row):
        info = f"""
        <strong>{row['restaurant_name']}</strong><br>
        <em>{row['cuisine_type']}</em><br>
        <br><strong>Address:</strong> {row['address']}, {row['city']}, {row['postal_code']}, {row['country']}<br>
        <strong>Price Range:</strong> {row['price_range']}<br>
        <strong>Phone:</strong> {row['phone_number']}<br>
        <strong>Website:</strong> <a href="{row['url']}" target="_blank">{row['url']}</a><br>
        <strong>Description:</strong> {row['description']}<br>
        <strong>Score:</strong> {row['score']}<br>
        <br><strong>Opening Hours:</strong><br>
        <table style="width:100%; border:1px solid black;">
            <tr><td><strong>Monday</strong></td><td>{row['monday_hours']}</td></tr>
            <tr><td><strong>Tuesday</strong></td><td>{row['tuesday_hours']}</td></tr>
            <tr><td><strong>Wednesday</strong></td><td>{row['wednesday_hours']}</td></tr>
            <tr><td><strong>Thursday</strong></td><td>{row['thursday_hours']}</td></tr>
            <tr><td><strong>Friday</strong></td><td>{row['friday_hours']}</td></tr>
            <tr><td><strong>Saturday</strong></td><td>{row['saturday_hours']}</td></tr>
            <tr><td><strong>Sunday</strong></td><td>{row['sunday_hours']}</td></tr>
        </table><br>
        <strong>Facilities:</strong> {row['facilities_services']}<br>
        <strong>Credit Cards:</strong> {row['credit_cards']}
        """
        return info

    # Add markers for each restaurant
    for _, row in data.iterrows():
        lat, lon = row['latitude'], row['longitude']
        price_range = row['price_range']
        marker_color = price_color_mapping.get(price_range, "gray")
        popup_html = create_popup_html(row)
        popup = folium.Popup(popup_html, max_width=300)
        
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=f"{row['restaurant_name']} - {row['price_range']} - {row['cuisine_type']}",
            icon=folium.Icon(color=marker_color, icon="cutlery", prefix="fa")
        ).add_to(marker_cluster)

    # Legend for price range
    legend_html = '''
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 150px; height: 140px; 
                 background-color: white; border:2px solid grey; z-index:9999; font-size:14px;">
     <strong>Price Range Legend</strong><br>
     <i style="color:green; font-size:15px;">&#9679;</i> €<br>
     <i style="color:blue; font-size:15px;">&#9679;</i> €€<br>
     <i style="color:orange; font-size:15px;">&#9679;</i> €€€<br>
     <i style="color:red; font-size:15px;">&#9679;</i> €€€€<br>
     </div>
     '''
    return m  # Return the map object

# Search and display results
if st.button("Search"):
    # Preprocess the query
    query_series = pd.Series(query)
    query_series = query_series.apply(remove_stopwords).apply(apply_stemming).apply(remove_punc).apply(apply_lemmatization)
    query_preprocessed = query_series.iloc[0]

    # Preprocess facilities and cuisine type requirements
    facilities_rq_processed = pd.Series(facilities_rq).apply(remove_stopwords).apply(apply_stemming).apply(remove_punc).apply(apply_lemmatization)
    facilities_rq_processed = list(facilities_rq_processed)
    cuisine_type_rq_processed = pd.Series(cuisine_type_rq).apply(remove_stopwords).apply(apply_stemming).apply(remove_punc).apply(apply_lemmatization)
    cuisine_type_rq_processed = list (cuisine_type_rq_processed)
    # Rank documents based on the preprocessed query, facilities, cuisine type, and selected k value
    try:
        top_k_documents = rank_new_score(query_preprocessed, inverted_index, df, vocab_df, facilities_rq_processed, cuisine_type_rq_processed, k)
        top_k_df = top_k_documents.merge(
    df[['restaurant_name', 'address', 'latitude', 'longitude', 'city', 'postal_code', 'country', 'phone_number', 
        'monday_hours', 'tuesday_hours', 'wednesday_hours', 'thursday_hours', 'friday_hours', 
        'saturday_hours', 'sunday_hours', 'facilities_services', 'credit_cards', 
        'cuisine_type', 'price_range', 'url']],
    on=['restaurant_name', 'address'], 
    how='left'
)
        # Display top-k results in Streamlit
        if not top_k_df.empty:
            m = create_restaurant_map(top_k_df)
            st_folium(m)  # Display the map with st_folium
        else:
            st.warning("No matching restaurants found.")
    except Exception as e:
        st.error(f"Error in ranking function: {e}")
