import logging
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

def load_data():
    logging.debug("Loading data...")
    # Implement your data loading logic here
    # For example, reading from a CSV file
    return pd.read_csv("../model/data/movies.csv")

def preprocess_data(movies: pd.DataFrame):
    logging.debug("Preprocessing data...")
    def parse_genres(genre_str):
        try:
            if isinstance(genre_str, str):
                return " ".join(genre_str.split("|"))
            else:
                return ""
        except Exception as e:
            logging.error(f"Error parsing genres: {e}")
            return "" 

    movies["genres"] = movies["genres"].apply(parse_genres)
    movies["movie_title"] = movies["movie_title"].fillna("").astype(str)
    movies["year_released"] = movies["year_released"].fillna("").astype(str)
    movies["combined_features"] = (
        movies["genres"] + " " + movies["movie_title"] + " " + movies["year_released"]
    )
    logging.debug("Data preprocessing complete.")
    return movies

def get_recommendations(title, movies, cosine_sim):
    logging.debug(f"Getting recommendations for movie: {title}")
    idx = movies[movies["movie_title"].str.lower() == title.lower()].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # Skip the self match
    movie_indices = [i[0] for i in sim_scores]
    recommendations = movies["movie_title"].iloc[movie_indices].tolist()
    logging.debug(f"Recommendations: {recommendations}")
    return recommendations

@app.post("/movie_info/{movie_title}")
async def movie_info(movie_title: str):
    logging.debug(f"Received request for movie info: {movie_title}")
    # Load and preprocess the movie data
    movies = preprocess_data(load_data())

    # Create TF-IDF matrix
    logging.debug("Creating TF-IDF matrix...")
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["combined_features"])
    logging.debug("TF-IDF matrix created.")

    # Compute cosine similarity
    logging.debug("Computing cosine similarity...")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    logging.debug("Cosine similarity computed.")

    # Get movie recommendations based on the provided movie title
    recommendations = get_recommendations(movie_title, movies, cosine_sim)

    # Return recommendations as JSON response
    logging.debug(f"Returning recommendations: {recommendations}")
    return {"recommended_movies": recommendations}

# EXAMPLE TO TEST:
# Run uvicorn fastAPI_content_model:app --reload
# Then run the following curl command in a separate terminal:

'''

curl -X POST http://127.0.0.1:8000/movie_info/joker -H "Content-Type: application/json" -d '{
    "movie_title": "Joker",
    "year_released": 2019,
    "genres": ["Crime", "Drama", "Thriller"],
'''