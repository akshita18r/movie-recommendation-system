
import streamlit as sl
import pandas as pd
import requests

# Set Page Configuration
sl.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Background Gradient (Using Markdown)
sl.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to Fetch Movie Posters
def fetch_posters(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'
    )
    data = response.json()
    return 'http://image.tmdb.org/t/p/w500/' + data.get('poster_path', '')


# Recommendation Function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    recommended_movie_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_posters(movie_id))

    return recommended_movies, recommended_movie_posters


# Load Data
import pickle
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Title
sl.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 Cine Match</h1>", unsafe_allow_html=True)


# Movie Selection
def update_recommendations():
    sl.session_state.recommended_names, sl.session_state.recommended_posters = recommend(
        sl.session_state.selected_movie)

sl.markdown("<h3 style='color: #ADBCA5; margin-bottom:-45px;'>🎥 Select a Movie:</h3>", unsafe_allow_html=True)

selection_movie = sl.selectbox(
    '',
    movies['title'].values,
    key="selected_movie",
    on_change=update_recommendations
)

# Display Recommendations
if "recommended_names" in sl.session_state:
    names, posters = sl.session_state.recommended_names, sl.session_state.recommended_posters
    sl.subheader("🎬 Recommended Movies for You:")
    row1 = sl.columns(5)
    for i in range(5):
        with row1[i]:
            sl.write(f"**{names[i]}**")
            sl.image(posters[i], use_container_width=True)
    row2 = sl.columns(5)
    for i in range(5, 10):
        with row2[i - 5]:
            sl.write(f"**{names[i]}**")
            sl.image(posters[i], use_container_width=True)



