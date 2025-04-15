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
from concurrent.futures import ThreadPoolExecutor


dotenv_path = Path('./client.env')
load_dotenv(dotenv_path=dotenv_path)

SPOTIFY_CLIENT_ID = str(os.getenv('Client_ID'))
SPOTIFY_CLIENT_SECRET = str(os.getenv('Client_Secret'))
YOUTUBE_API_KEY =str(os.getenv('API_KEY_YOUTUBE_GOOGLE'))
RAPID_API_KEY = str(os.getenv('RAPID_API_KEY'))


sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id= SPOTIFY_CLIENT_ID, client_secret= SPOTIFY_CLIENT_SECRET))

COOKIES_DIR = 'controller/cookies.txt'

def fetch_initial_link(video_id, api_key):

    api_list = [
        {   
            "name" : "YT-Media Downloader",
            "url" : "https://youtube-media-downloader.p.rapidapi.com/v2/video/details",
            "headers" : {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"
            },
            "querystring" : {"videoId": video_id, "videos": "false", "audios": "true", "subtitles": "false", "related": "false"}
        },

        {
            "name" : "YTStream Download",
            "url" : "https://ytstream-download-youtube-videos.p.rapidapi.com/dl",
            "headers": {
                "x-rapidapi-key" : RAPID_API_KEY,
                "x-rapidapi-host" : "ytstream-download-youtube-videos.p.rapidapi.com"
            },
            "querystring" : {"id" : video_id}
        },

        {
            "name" : "YOUTUBE MP4/MP3/M4A CDN",
            "url" : "https://youtube-mp4-mp3-m4a-cdn.p.rapidapi.com/stream",
            "headers" : {
                "x-rapidapi-key": RAPID_API_KEY,
	            "x-rapidapi-host": "youtube-mp4-mp3-m4a-cdn.p.rapidapi.com"
            },
            "querystring" : {"id" : video_id}
        },

        {
         "name" : "Youtube Downloader API",
         "url" : "https://youtube-downloader-api-fast-reliable-and-easy.p.rapidapi.com/fetch_audio",
         "headers" : {
                "x-rapidapi-key": RAPID_API_KEY,
	            "x-rapidapi-host": "youtube-downloader-api-fast-reliable-and-easy.p.rapidapi.com"
            },
        "querystring" : {"url" : f"https://www.youtube.com/watch?v={video_id}"}
        }
    ]

    for api in api_list:
        try:
            print(f"Sending GET Request to API: {api['name']}")

            response = requests.get(api["url"], headers=api["headers"], params=api["querystring"])
            response.raise_for_status()
            print(f"Received response with status code: {response.status_code}")
            
            data = response.json()
            if api["name"] == "YTStream Download" : 
                if "adaptiveFormats" in data:
                    adapformat = data["adaptiveFormats"]
                    for format in adapformat:
                        if "audio" in format["mimeType"]:
                            link = format["url"]
                            print(f"Found audio link: {link}")
                            return link
                print("Audio URL not found in response from YTStream Download")
            
            elif api["name"] == "YOUTUBE MP4/MP3/M4A CDN":
                if "formats" in data:
                    for format in data["formats"]:
                        if "audio" in format["type"]:
                            link = format["url"]
                            print(f"Found audio link: {link}")
                            return link
                print("Audio URL not found in response from YOUTUBE MP4/MP3/M4A CDN")

            elif api["name"] == "Youtube Downloader API":
                if "audio_formats" in data:
                    for format in data["audio_formats"]:
                        if "m4a" in format["ext"]:
                            link = format["url"]
                            print(f"Found audio link: {link}")
                            return link
                print("Audio URL not found in response from Youtube Downloader API")

            elif api["name"] == "YT-Media Downloader":
                if "audios" in data and "items" in data["audios"]: 
                    link = data['audios']['items'][0]['url']
                    if link:
                        print(link)
                        return link
                    else:
                        print("Audio URL not found in response")
                else:
                    print("Audio URL not found in response from YT-Media Downloader")
                
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching initial link from {api['name']}: {e}")
            continue

    print("All API attempts failed.")
    return None

# async def songdetails(search_query):
#     try:
#         result = sp.search(search_query, type='track', limit=1)

#         if result['tracks']['items']:
#             track = result['tracks']['items'][0]
#             artist = track['artists'][0]['name']
#             song = track['name']
#             print(f"Found track: Artist: {artist}, Song: {song}")
#             return artist, song
#         else:
#             print("No tracks found for this search query.")
#             return None, None
#     except Exception as e:
#         print(f"Error occurred while searching for the song: {e}")
#         return None, None

async def songdetails(search_query: str):
    try:
        # Wrap synchronous Spotify call in thread executor
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: sp.search(search_query, type='track', limit=1)
            )

        if not result['tracks']['items']:
            print("No tracks found for:", search_query)
            return None, None

        track = result['tracks']['items'][0]
        return (
            track['artists'][0]['name'].strip(),
            track['name'].strip()
        )

    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e.code} - {e.msg}")
        return None, None
    except KeyError as e:
        print(f"Missing expected data in API response: {str(e)}")
        return None, None
    except Exception as e:
        print(f"Unexpected error in songdetails: {str(e)}")
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
        "key": YOUTUBE_API_KEY
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

# async def search2hls_rapidapi(search_query: str, websocket: WebSocket):
 
#     async def yt_search_googleapi(search_query):
#         url = "https://www.googleapis.com/youtube/v3/search"
#         params = {
#             "part": "snippet",
#             "q": search_query,
#             "key": YOUTUBE_API_KEY
#         }

#         try:
#             response = requests.get(url, params=params)
#             response.raise_for_status()
#             data = response.json()

#             if 'items' not in data or not data['items']:
#                 print(f"No results found for search query: {search_query}")
#                 return None
            
#             video_id = data['items'][0]['id'].get('videoId')
#             if video_id:
#                 print(f"Found video ID: {video_id}")
#                 return video_id
#             else:
#                 print(f"Video ID not found in response: {data}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Error occurred while searching for the song: {e}")
#             return None   

#     async def download_audio(video_id, api_key):

#         output_dir = "./mp3"
#         os.makedirs(output_dir, exist_ok=True)
#         mp3_file = os.path.join(output_dir, f"{video_id}.mp3")

#         try:
#             print(f"Fetching initial link for video ID: {video_id}")
#             initial_link = fetch_initial_link(video_id, api_key)
            
#             if not initial_link:
#                 print("Failed to get initial link.")
#                 return None

#             print(f"Downloading MP3 for video ID: {video_id}...")
#             response = requests.get(initial_link, stream=True)
#             response.raise_for_status()

#             with open(mp3_file, "wb") as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)

#             print(f"MP3 downloaded successfully: {mp3_file}")
#             return mp3_file

#         except requests.exceptions.RequestException as e:
#             print(f"Error: {e}")
#             return None
        
#     async def convert_hls(video_id, mp3_file):
#         output_dir = "./hls"
#         hls_dir = os.path.join(output_dir, video_id)

#         os.makedirs(hls_dir, exist_ok=True)
#         hls_file = os.path.join(hls_dir, f"{video_id}.m3u8")

#         print(f"Converting MP3 to HLS format: {hls_file}")
#         command = [
#             "ffmpeg",
#             "-i", mp3_file,
#             "-acodec", "aac",
#             "-b:a", "320k",
#             "-hls_time", "10",
#             "-hls_list_size", "0",
#             "-f", "hls",
#             hls_file
#         ]

#         try:
#             subprocess.run(command, check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"Error during HLS conversion: {e}")
#             print(f"Exit status: {e.returncode}")
#             print(f"stdeerr: {e.stderr}")

#         print(f"HLS files are saved in: {hls_dir}")

#         if os.path.exists(mp3_file):
#             os.remove(mp3_file)
#             print(f"Deleted the MP3 file: {mp3_file}")

#         asyncio.create_task(deletefolder(hls_dir))

#     id = await yt_search_googleapi(search_query)
#     if not id:
#         await websocket.send_text("video id not found, aborting")
#         return

#     mp3 = await download_audio(id, RAPID_API_KEY)

#     if not mp3:
#         await websocket.send_text("MP3 download failed, aborting.")
#         print("MP3 download failed, aborting.")
#         return
    
#     await convert_hls(id, mp3)    
#     return id


async def search2hls_rapidapi_noHLS(search_query: str, websocket: WebSocket):
 
    async def yt_search_googleapi(search_query):
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": search_query,
            "key": YOUTUBE_API_KEY
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


    async def get_streamlink(video_id, api_key):
        try:
            print(f"Fetching streamable link for video ID: {video_id}")
            streamable_link = fetch_initial_link(video_id, api_key)
            
            if not streamable_link:
                print("Failed to get initial link.")
                return None

            return streamable_link

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
            
    id = await yt_search_googleapi(search_query)
    if not id:
        await websocket.send_text("video id not found, aborting")
        return

    link = await get_streamlink(id, RAPID_API_KEY)

    if not link:
        await websocket.send_text("Streamable link not fouund, aborting.")
        print("Streamable link not found, aborting.")
        return

    return link
