import streamlit as st
import pandas as pd

# Load dataset from GitHub
url = "https://raw.githubusercontent.com/zimmy11/ADM-HW3/refs/heads/main/michelin_restaurants_data.csv"
dataset_bonus = pd.read_csv(url)

# Data preprocessing
dataset_bonus['region'] = dataset_bonus['url_micheline'].str.extract(r'https://guide\.michelin\.com/en/([^/]+)/')
dataset_bonus['restaurant_name'] = dataset_bonus['restaurant_name'].str.split(' -').str[0]
dataset_bonus['credit_cards'] = dataset_bonus['credit_cards'].apply(lambda x: set(str(x).split(',')) if pd.notna(x) else set())
dataset_bonus['facilities_services'] = dataset_bonus['facilities_services'].apply(lambda x: set(str(x).split(',')) if pd.notna(x) else set())
dataset_bonus['city'] = dataset_bonus['city'].fillna('').astype(str).str.lower()
dataset_bonus['restaurant_name'] = dataset_bonus['restaurant_name'].fillna('').astype(str).str.lower()
dataset_bonus['cuisine_type'] = dataset_bonus['cuisine_type'].fillna('').astype(str).str.lower()
dataset_bonus['price_range'] = dataset_bonus['price_range'].fillna('')

# Unique options for dropdowns and multiselects
unique_cities = sorted(dataset_bonus['city'].unique())
unique_cuisines = sorted(dataset_bonus['cuisine_type'].unique())
unique_price_ranges = ['', '€', '€€', '€€€', '€€€€']
unique_regions = sorted(dataset_bonus['region'].dropna().unique())
unique_credit_cards = sorted({card.strip() for cards in dataset_bonus['credit_cards'] for card in cards})
unique_services = sorted({service.strip() for services in dataset_bonus['facilities_services'] for service in services})

# Streamlit UI for search filters
st.title("Michelin Restaurant Search")

restaurant_name = st.text_input("Enter restaurant name (optional):").strip().lower()
city = st.selectbox("Select city (optional):", [""] + unique_cities)
cuisine_type = st.selectbox("Select cuisine type (optional):", [""] + unique_cuisines)
price_range = st.selectbox("Select price range (optional):", unique_price_ranges)
regions = st.multiselect("Select regions (optional):", unique_regions)
accepted_cards = set(st.multiselect("Select accepted cards (optional):", unique_credit_cards))
services = set(st.multiselect("Select services (optional):", unique_services))

# Search function
results = []
for _, restaurant in dataset_bonus.iterrows():
    if restaurant_name and restaurant_name not in restaurant.get("restaurant_name", ""):
        continue

    if city and city != restaurant.get("city", ""):
        continue

    if cuisine_type and cuisine_type not in restaurant.get("cuisine_type", ""):
        continue

    if price_range and price_range != restaurant.get("price_range", ""):
        continue

    if regions and restaurant.get("region", "").lower() not in regions:
        continue

    if accepted_cards and not accepted_cards.intersection(restaurant["credit_cards"]):
        continue

    if services and not services.issubset(restaurant["facilities_services"]):
        continue

    results.append({
        "restaurant_name": restaurant["restaurant_name"].title(),
        "address": restaurant["address"],
        "cuisine_type": restaurant["cuisine_type"].title(),
        "price_range": restaurant["price_range"],
        "website": restaurant["url_micheline"]
    })

# Display search results
if st.button("Search"):
    if results:
        st.write("### Search Results:")
        for result in results:
            st.write(f"**Name**: {result['restaurant_name']}")
            st.write(f"**Address**: {result['address']}")
            st.write(f"**Cuisine**: {result['cuisine_type']}")
            st.write(f"**Price**: {result['price_range']}")
            st.write(f"**Website**: [Link]({result['website']})")
            st.write("---")
    else:
        st.write("No restaurants found matching the criteria.")
