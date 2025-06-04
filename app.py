import streamlit as sl
import pandas as pd
import requests
import pickle
from requests.exceptions import RequestException

# Load Data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit Page Configuration
sl.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling
sl.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);
        color: #FFD700;
    }

    /* Button Style - force it to stay black with golden text always */
    div.stButton > button:first-child {
        background-color: black !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        border-radius: 8px;
        padding: 0.5em 1.2em;
        transition: 0.3s ease;
        font-weight: bold;
    }

    div.stButton > button:first-child:hover {
        background-color: black !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
    }

    /* Button focus & active state (on click) */
    div.stButton > button:focus,
    div.stButton > button:active {
        background-color: black !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        box-shadow: none !important;
    }

    /* White Text for Movie Titles */
    .stImage + div {
        color: white !important;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# TMDb API Key
API_KEY = "d21f6782344f0eebe6c847fa8a727834"

# Poster Fetching Function
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=d21f6782344f0eebe6c847fa8a727834&language=en-US',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"http://image.tmdb.org/t/p/w500/{poster_path}"
    except requests.exceptions.RequestException as e:
        print(f"Poster fetch failed for movie ID {movie_id}: {e}")
    return None


# Trailer Fetching Function
def fetch_trailer(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=d21f6782344f0eebe6c847fa8a727834&language=en-US'
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raise HTTPError if status != 200
        data = response.json()
        for video in data.get("results", []):
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
    except requests.exceptions.RequestException as e:
        print(f"Trailer fetch failed for movie ID {movie_id}: {e}")
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_titles = []
    posters = []
    trailers = []

    for i in movie_list:
        movie_row = movies.iloc[i[0]]  # this is a Series
        movie_id = movie_row['id']  # access value correctly
        title = movie_row['title']
        poster = fetch_poster(movie_id)
        trailer = fetch_trailer(movie_id)

        recommended_titles.append(title)
        posters.append(poster)
        trailers.append(trailer)

    return recommended_titles, posters, trailers


# App Title
sl.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 Cine Match</h1>", unsafe_allow_html=True)

# Movie Dropdown
sl.markdown("<h3 style='color: #ADBCA5;'>🎥 Choose your favourite Movie:</h3>", unsafe_allow_html=True)
selected_movie = sl.selectbox("", movies["title"].values)

# On Button Click
if sl.button("Show Recommendations"):
    names, posters, trailers = recommend(selected_movie)

    sl.subheader("🎬 Recommended Movies for You:")

    cols = sl.columns(5)
    for i in range(5):
        with cols[i]:
            if posters[i]:
                sl.image(posters[i], use_container_width=True)
            else:
                sl.markdown("🚫 Poster not available")
            sl.write(f"**{names[i]}**")
            if trailers[i]:
                sl.markdown(f"[▶️ Watch Trailer]({trailers[i]})", unsafe_allow_html=True)
            else:
                sl.markdown("🚫 Trailer not found")

    cols = sl.columns(5)
    for i in range(5, 10):
        with cols[i - 5]:
            if posters[i]:
                sl.image(posters[i], use_container_width=True)
            else:
                sl.markdown("🚫 Poster not available")
            sl.write(f"**{names[i]}**")
            if trailers[i]:
                sl.markdown(f"[▶️ Watch Trailer]({trailers[i]})", unsafe_allow_html=True)
            else:
                sl.markdown("🚫 Trailer not found")


