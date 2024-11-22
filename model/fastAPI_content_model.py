from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

app = FastAPI()

class MovieInfo(BaseModel):
    title: str

def load_data(file_path="../model/data/movies.csv"):
    if file_path.split(".")[-1] == "gz":
        movies = pd.read_csv(file_path, compression="gzip")
    else:
        movies = pd.read_csv(file_path)
    return movies

def preprocess_data(movies: pd.DataFrame):
    def parse_genres(genre_str):
        try:
            if isinstance(genre_str, str):
                return " ".join(genre_str.split("|"))
            else:
                return ""
        except Exception as e:
            print(f"Error parsing genres: {e}")
            return "" 

    movies["genres"] = movies["genres"].apply(parse_genres)
    movies["movie_title"] = movies["movie_title"].fillna("").astype(str)
    movies["year_released"] = movies["year_released"].fillna("").astype(str)
    movies["combined_features"] = (
        movies["genres"] + " " + movies["movie_title"] + " " + movies["year_released"]
    )
    return movies

def get_recommendations(title, movies, cosine_sim):
    idx = movies[movies["movie_title"] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # Skip the self match
    movie_indices = [i[0] for i in sim_scores]
    return movies["movie_title"].iloc[movie_indices].tolist()

@app.post("/movie_info/{movie_title}")
async def movie_info(movie_title: str):
    # Load and preprocess the movie data
    movies = preprocess_data(load_data())

    # Create TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["combined_features"])

    # Compute cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get movie recommendations based on the provided movie title
    recommendations = get_recommendations(movie_title, movies, cosine_sim)

    # Return recommendations as JSON response
    return {"recommended_movies": recommendations}


# EXAMPLE TO TEST:
# Run uvicorn fastAPI_content_model:app --reload
# Then run the following curl command in a separate terminal:

'''

curl -X POST http://127.0.0.1:8000/movie_info/joker -H "Content-Type: application/json" -d '{
    "movie_title": "Joker",
    "year_released": 2019,
    "genres": ["Crime", "Drama", "Thriller"],
    "imdb_link": "https://www.imdb.com/title/tt7286456/",
    "rating_count": 1000000
}'

'''

# I was hoping that this would be faster, but I'll leave it here for fun