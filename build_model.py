import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import httpx
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY") or os.getenv("TMBD_API_KEY")

if not TMDB_API_KEY:
    print("Error: TMDB_API_KEY not found in .env")
    exit(1)

def fetch_popular_movies(pages=5):
    movies = []
    base_url = "https://api.themoviedb.org/3/movie/popular"
    for page in range(1, pages + 1):
        params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": page}
        try:
            response = httpx.get(base_url, params=params, verify=False, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for item in results:
                    movies.append({
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "overview": item.get("overview", "")
                    })
            else:
                print(f"Failed to fetch page {page}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
    return movies

def build_model():
    print("Fetching popular movies from TMDB to build the recommendation model...")
    # Fetch top 20 pages (approx 400 movies) to build a small local model
    movies = fetch_popular_movies(pages=20)
    
    if not movies:
        print("No movies fetched. Cannot build model.")
        return

    print(f"Fetched {len(movies)} movies. Building TF-IDF matrix...")
    df = pd.DataFrame(movies)
    
    # Fill empty overviews
    df['overview'] = df['overview'].fillna('')
    
    # Initialize TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the overviews
    tfidf_matrix = tfidf.fit_transform(df['overview'])
    
    # Create an indices series
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    
    # Save the files
    print("Saving model files...")
    with open('df.pkl', 'wb') as f:
        pickle.dump(df, f)
        
    with open('indices.pkl', 'wb') as f:
        pickle.dump(indices, f)
        
    with open('tfidf_matrix.pkl', 'wb') as f:
        pickle.dump(tfidf_matrix, f)
        
    with open('tfidf.pkl', 'wb') as f:
        pickle.dump(tfidf, f)
        
    print("Model files successfully created! You can now use the content-based recommendation feature.")

if __name__ == "__main__":
    build_model()
