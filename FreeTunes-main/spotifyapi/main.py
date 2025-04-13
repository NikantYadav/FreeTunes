from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Spotify API with client credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "0a2fff742fae4e80840bce0667700458")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "a30b2644fcb2404f9443eab6ff05d6da")

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# Function to get song details
def songdetails(search_query: str):
    try:
        result = sp.search(search_query, type='track', limit=1)
        if result['tracks']['items']:
            track = result['tracks']['items'][0]
            artist = track['artists'][0]['name']
            song = track['name']
            print(f"song details server: artist : {artist}, song : {song}")
            return artist, song
        else:
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Define endpoint to search Spotify
@app.post("/spotify")
async def spotifyapi(request: Request, response: Response):
    try:
        query_params = dict(request.query_params)
        search_query = query_params.get("query")
        
        if not search_query:
            raise HTTPException(status_code=400, detail="Missing 'query' parameter")

        artist, song = songdetails(search_query)

        if not artist or not song:
            raise HTTPException(status_code=404, detail="Song not found")

        print(f"app.post : {artist} {song}")
        return {
            "artist": artist,
            "song": song
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


