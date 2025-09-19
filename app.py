import streamlit as st
import pandas as pd

# Load clustered data
df_clustered = pd.read_csv("clustered_data.csv")

# Recommendation Function
def recommend_by_cluster(restaurant_name, city=None, cuisines=None, cost_range=None, top_n=5):
    if restaurant_name not in df_clustered['name'].values:
        return pd.DataFrame(columns=['name', 'city', 'cuisine', 'rating', 'cost'])

    restaurant_index = df_clustered[df_clustered['name'] == restaurant_name].index[0]
    target_cluster = df_clustered.loc[restaurant_index, 'cluster']
    
    # Filter same cluster
    cluster_group = df_clustered[df_clustered['cluster'] == target_cluster]

    # Drop the restaurant itself
    cluster_group = cluster_group.drop(restaurant_index, errors='ignore')

    #  Apply Filters 
    if city and city != "All":
        cluster_group = cluster_group[cluster_group['city'].str.contains(city, case=False, na=False)]

    if cuisines and "All" not in cuisines:
        cluster_group = cluster_group[cluster_group['cuisine'].apply(
            lambda x: any(c in x for c in cuisines) if pd.notna(x) else False
        )]

    if cost_range and cost_range != "All":
        min_cost, max_cost = map(int, cost_range.split('-'))
        cluster_group = cluster_group[(cluster_group['cost'] >= min_cost) & (cluster_group['cost'] <= max_cost)]

    return cluster_group.head(top_n)[['name', 'city', 'cuisine', 'rating', 'cost']]

# Streamlit UI 
st.title("🍽️ Swiggy Restaurant Recommender")

# Dropdown for restaurant selection
restaurant_list = df_clustered['name'].dropna().unique()
restaurant_name = st.selectbox("Select a restaurant:", restaurant_list)

# Filters
st.sidebar.header("🔍 Filters")

# City filter
cities = ["All"] + sorted(df_clustered['city'].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("Select City:", cities)

# Cuisine filter (multiselect)
all_cuisines = sorted(set(
    c.strip() for cuisines in df_clustered['cuisine'].dropna().str.split(",") for c in cuisines
))
selected_cuisines = st.sidebar.multiselect("Select Cuisine(s):", ["All"] + all_cuisines, default="All")

# Cost filter
cost_ranges = ["All", "0-200", "201-500", "501-1000", "1001-5000"]
selected_cost = st.sidebar.selectbox("Select Cost Range:", cost_ranges)

# Number of recommendations
top_n = st.slider("How many recommendations?", 1, 10, 5)

if st.button("Get Recommendations"):
    results = recommend_by_cluster(
        restaurant_name, 
        city=selected_city, 
        cuisines=selected_cuisines, 
        cost_range=selected_cost, 
        top_n=top_n
    )
    
    if results.empty:
        st.warning("⚠️ No recommendations found with the selected filters.")
    else:
        st.success(f"✅ Here are {len(results)} similar restaurants to **{restaurant_name}**:")
        st.dataframe(results)





