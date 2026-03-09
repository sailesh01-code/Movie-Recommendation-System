import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Movie Recommender", layout="wide", page_icon="🎬")

# Custom CSS for a better UI
st.markdown("""
    <style>
    .movie-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    .movie-card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.5);
        transform: scale(1.02);
    }
    .movie-title {
        font-size: 1.1em;
        font-weight: bold;
        margin-top: 10px;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .movie-rating {
        color: #f5c518;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Recommendation System")

tab1, tab2 = st.tabs(["🏠 Home", "🔍 Search & Recommend"])

# Function to display movies in a grid
def display_movie_grid(movies, columns=4):
    cols = st.columns(columns)
    for idx, movie in enumerate(movies):
        with cols[idx % columns]:
            poster = movie.get('poster_url')
            if not poster:
                poster = "https://via.placeholder.com/500x750?text=No+Poster"
                
            title = movie.get('title', 'Unknown')
            rating = movie.get('vote_average', 'N/A')
            
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster}" width="100%" style="border-radius: 5px;">
                    <div class="movie-title" title="{title}">{title}</div>
                    <div class="movie-rating">⭐ {rating if rating else 'N/A'}</div>
                </div>
            """, unsafe_allow_html=True)

with tab1:
    st.header("Trending & Popular Movies")
    category = st.selectbox("Select Category", ["popular", "trending", "top_rated", "upcoming", "now_playing"])
    
    with st.spinner("Fetching movies..."):
        try:
            response = httpx.get(f"{API_URL}/home", params={"category": category, "limit": 20})
            if response.status_code == 200:
                movies = response.json()
                display_movie_grid(movies, columns=5)
            else:
                st.error("Failed to fetch movies from the backend.")
        except Exception as e:
            st.error(f"Cannot connect to the backend. Is uvicorn running? Error: {e}")

with tab2:
    st.header("Search for a Movie")
    search_query = st.text_input("Enter a movie title (e.g., Inception, The Matrix)")
    
    if st.button("Search & Get Recommendations") and search_query:
        with st.spinner(f"Searching for '{search_query}'..."):
            try:
                response = httpx.get(f"{API_URL}/movie/search", params={"query": search_query, "tfidf_top_n": 10, "genre_limit": 10})
                
                if response.status_code == 200:
                    data = response.json()
                    details = data.get("movie_details", {})
                    
                    # Display selected movie details
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if details.get("poster_url"):
                            st.image(details["poster_url"], use_column_width=True)
                    with col2:
                        st.subheader(details.get("title", ""))
                        if details.get("release_date"):
                            st.write(f"**Release Date:** {details['release_date']}")
                        if details.get("overview"):
                            st.write(f"**Overview:** {details['overview']}")
                        if details.get("genres"):
                            genres = ", ".join([g["name"] for g in details["genres"]])
                            st.write(f"**Genres:** {genres}")
                            
                    st.divider()
                    
                    # Display Content-Based Recommendations (TF-IDF)
                    st.subheader("💡 Similar Movies (Based on Content)")
                    tfidf_recs = data.get("tfidf_recommendations", [])
                    if tfidf_recs:
                        # Extract the TMDB card from the TFIDF item
                        movies_to_display = [rec["tmdb"] for rec in tfidf_recs if rec.get("tmdb")]
                        if movies_to_display:
                            display_movie_grid(movies_to_display, columns=5)
                        else:
                            st.info("No poster data available for these recommendations.")
                    else:
                        st.info("No content-based recommendations found.")
                        
                    st.divider()
                    
                    # Display Genre Recommendations
                    st.subheader("🍿 More Like This (Based on Genre)")
                    genre_recs = data.get("genre_recommendations", [])
                    if genre_recs:
                        display_movie_grid(genre_recs, columns=5)
                    else:
                        st.info("No genre-based recommendations found.")
                        
                elif response.status_code == 404:
                    st.warning(f"No movie found for '{search_query}'. Try a different title.")
                else:
                    st.error("Error fetching data from the backend.")
            except Exception as e:
                st.error(f"Cannot connect to the backend. Is uvicorn running? Error: {e}")