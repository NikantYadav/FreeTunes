import yt_dlp
import os 
import subprocess
from pathlib import Path
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import shutil
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import requests

dotenv_path = Path('./client.env')
load_dotenv(dotenv_path=dotenv_path)

SPOTIFY_CLIENT_ID = str(os.getenv('Client_ID'))
SPOTIFY_CLIENT_SECRET = str(os.getenv('Client_Secret'))
API_KEY =str(os.getenv('API_KEY_YOUTUBE_GOOGLE'))
rapid_username = str(os.getenv('RAPID_USERNAME'))

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id= SPOTIFY_CLIENT_ID, client_secret= SPOTIFY_CLIENT_SECRET))

COOKIES_DIR = 'controller/cookies.txt'

def fetch_initial_link(video_id, api_key):

    url = "https://youtube-mp36.p.rapidapi.com/dl"
    querystring = {"id": video_id}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "youtube-mp36.p.rapidapi.com",
        "User-Agent": f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 ${rapid_username}' 
    }

    try:
        print("Sending GET request to the API...")

        response = requests.get(url, headers=headers, params=querystring)
        
        print(f"Received response with status code: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        print(f"Extracted link: {link}")
        return data.get('link')
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching initial link: {e}")
        return None

async def songdetails(search_query):
    try:
        result = sp.search(search_query, type='track', limit=1)

        if result['tracks']['items']:
            track = result['tracks']['items'][0]
            artist = track['artists'][0]['name']
            song = track['name']
            print(f"Found track: Artist: {artist}, Song: {song}")
            return artist, song
        else:
            print("No tracks found for this search query.")
            return None, None
    except Exception as e:
        print(f"Error occurred while searching for the song: {e}")
        return None, None

async def deletefolder(folder_path:str):
    await asyncio.sleep(360)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder {folder_path} not found, could not delete")

async def get_id(search_query):
    command = [
        'yt-dlp', 
        '--quiet',  
        '--cookies', COOKIES_DIR,  
        '--print', 'id', 
        f"ytsearch1:{search_query}"
    ]

    try:
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        
        print(f"YT-DLP Output: {result.stdout}")  
        
        
        video_id = result.stdout.strip()  
        
        if video_id:
            print(f"Video ID: {video_id}")
            return video_id
        else:
            print("No results found")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error during yt-dlp execution: {e}")
        print(f"Exit status: {e.returncode}")
        print(f"stdeerr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def search2hls(search_query: str, websocket: WebSocket):
    async def yt_search(search_query):
        command = [
            'yt-dlp', 
            '--quiet', 
            '--cookies', COOKIES_DIR, 
            '--print', 'id',
            f"ytsearch1:{search_query}"
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            video_id = result.stdout.strip()  
        
            if video_id:
                print(f"Video ID: {video_id}")
                return video_id
            else:
                print("No results found")
                return None
        except subprocess.CalledProcessError as e:
            print(f"Error during yt-dlp execution: {e}")
            print(f"Exit status: {e.returncode}")
            print(f"stdeerr: {e.stderr}")
            return None

    async def download_audio(video_id):
        output_dir = "./mp3"
        os.makedirs(output_dir, exist_ok=True)
        mp3_file = os.path.join(output_dir, f"{video_id}.mp3")

        command = [
            'yt-dlp',
            '--format', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--output', mp3_file,
            '--audio-quality', '0',
            '--quiet', 
            '--cookies', COOKIES_DIR, 
            f"https://www.youtube.com/watch?v={video_id}"
        ]
        
        print(f"Downloading MP3 for video ID: {video_id}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during MP3 download: {e}")
            print(f"Exit status: {e.returncode}")
            print(f"stdeerr: {e.stderr}")
            return None

        if not os.path.exists(mp3_file):
            print("Failed to download MP3.")
            return None
        
        return mp3_file

    async def convert_hls(video_id, mp3_file):
        output_dir = "./hls"
        hls_dir = os.path.join(output_dir, video_id)

        os.makedirs(hls_dir, exist_ok=True)
        hls_file = os.path.join(hls_dir, f"{video_id}.m3u8")

        print(f"Converting MP3 to HLS format: {hls_file}")
        command = [
            "ffmpeg",
            "-i", mp3_file,
            "-acodec", "aac",
            "-b:a", "320k",
            "-hls_time", "10",
            "-hls_list_size", "0",
            "-f", "hls",
            hls_file
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during HLS conversion: {e}")
            print(f"Exit status: {e.returncode}")
            print(f"stdeerr: {e.stderr}")

        print(f"HLS files are saved in: {hls_dir}")

        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            print(f"Deleted the MP3 file: {mp3_file}")

        asyncio.create_task(deletefolder(hls_dir))

    id = await yt_search(search_query)
    if not id:
        await websocket.send_text("video id not found, aborting")
        return

    mp3 = await download_audio(id)

    if not mp3:
        await websocket.send_text("MP3 download failed, aborting.")
        print("MP3 download failed, aborting.")
        return
    
    await convert_hls(id, mp3)    
    return id

async def streaming(id:str):
    base_dir = "./hls"
    subfolder_path = Path(base_dir) / id

    if not subfolder_path.is_dir():
        return None
    
    m3u8_file = list(subfolder_path.glob("*.m3u8"))
    if m3u8_file:
        file = m3u8_file[0]
        desired_url = str(file)[4:]
        print(desired_url)
        return desired_url
    else:
        print("HLS file not found.")
        return None



async def get_id_googleapi(search_query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search_query,
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'items' not in data or not data['items']:
            print(f"No results found for search query: {search_query}")
            return None
        
        video_id = data['items'][0]['id'].get('videoId')
        if video_id:
            print(f"Found video ID: {video_id}")
            return video_id 
        
        else:
            print(f"Video ID not found in response: {data}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while searching for the song: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def search2hls_rapidapi(search_query: str, websocket: WebSocket):
 
    async def yt_search_googleapi(search_query):
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": search_query,
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data or not data['items']:
                print(f"No results found for search query: {search_query}")
                return None
            
            video_id = data['items'][0]['id'].get('videoId')
            if video_id:
                print(f"Found video ID: {video_id}")
                return video_id
            else:
                print(f"Video ID not found in response: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while searching for the song: {e}")
            return None   

    async def download_audio(video_id, api_key):

        output_dir = "./mp3"
        os.makedirs(output_dir, exist_ok=True)
        mp3_file = os.path.join(output_dir, f"{video_id}.mp3")

        try:
            print(f"Fetching initial link for video ID: {video_id}")
            initial_link = fetch_initial_link(video_id, api_key)
            
            if not initial_link:
                print("Failed to get initial link.")
                return None

            print(f"Downloading MP3 for video ID: {video_id}...")
            response = requests.get(initial_link, stream=True)
            response.raise_for_status()

            with open(mp3_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"MP3 downloaded successfully: {mp3_file}")
            return mp3_file

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
        
    async def convert_hls(video_id, mp3_file):
        output_dir = "./hls"
        hls_dir = os.path.join(output_dir, video_id)

        os.makedirs(hls_dir, exist_ok=True)
        hls_file = os.path.join(hls_dir, f"{video_id}.m3u8")

        print(f"Converting MP3 to HLS format: {hls_file}")
        command = [
            "ffmpeg",
            "-i", mp3_file,
            "-acodec", "aac",
            "-b:a", "320k",
            "-hls_time", "10",
            "-hls_list_size", "0",
            "-f", "hls",
            hls_file
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during HLS conversion: {e}")
            print(f"Exit status: {e.returncode}")
            print(f"stdeerr: {e.stderr}")

        print(f"HLS files are saved in: {hls_dir}")

        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            print(f"Deleted the MP3 file: {mp3_file}")

        asyncio.create_task(deletefolder(hls_dir))

    id = await yt_search_googleapi(search_query)
    if not id:
        await websocket.send_text("video id not found, aborting")
        return

    mp3 = await download_audio(id, API_KEY)

    if not mp3:
        await websocket.send_text("MP3 download failed, aborting.")
        print("MP3 download failed, aborting.")
        return
    
    await convert_hls(id, mp3)    
    return id