from fastapi import FastAPI
import json
from moviepy.editor import *
import subprocess
from youtubesearchpython import VideosSearch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv, dotenv_values 
from pathlib import Path
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response


dotenv_path = Path('./client.env')
load_dotenv(dotenv_path=dotenv_path)

SPOTIFY_CLIENT_ID = str(os.getenv('Client_ID'))
SPOTIFY_CLIENT_SECRET = str(os.getenv('Client_Secret'))
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id= SPOTIFY_CLIENT_ID,client_secret= SPOTIFY_CLIENT_SECRET))

app = FastAPI()

@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL(s) in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


global searchquery
global link
global url
global songname
songnamelist = []
songidlist = []
idlist = []

with open('songid.json','r') as f:
    data = json.load(f)

async def errorcheck():
	print('upper code is running successfully')
	return 'upper code is running properly'

async def yt_search(item_id: str):
	videosSearch = VideosSearch(item_id, limit = 2)
	url = videosSearch.result()['result'][0]['link']
	return url

async def execute_server_js():
    try:
        subprocess.run(['node', 'server.js'], check=True)
        print('Node.js server executed successfully')
        return 'js server ran successfully'
    except subprocess.CalledProcessError as e:
        print(f"Error executing server.js: {e}")
        return f"Error executing server.js: {e}"

async def convertomp3():
	inputfile = 'downloaded/video.mp4'
	outputfile = 'mp3/audio.mp3'
	AudioFileClip(inputfile).write_audiofile(outputfile, bitrate='3000k')
	return 'Mp4 converted to Mp3 successfully'


@app.get("/")

async def read_link(item_id: str):

	#storing input song name in json
	songnamelist.append(item_id)
	json_songname = json.dumps(songnamelist, indent=1)
	with open("songs.json","w") as outsongfile:
		outsongfile.write(json_songname)

	#getting song id/artist/genre from spotify and saving it
	track_results = sp.search(q='track:'+str(item_id), type='track',limit = '1')
	song_id = track_results['tracks']['items'][0]['id']
	artist_id = track_results['tracks']['items'][0]['album']['artists'][0]['id']
	idlist.append({"song_id": song_id, "artist_id": artist_id})

	with open("songid.json", "r") as infile:
		existing_ids = json.load(infile)

	existing_ids.extend(idlist)

	with open("songid.json", "w") as outfile:
		json.dump(existing_ids, outfile, indent=1)

	#searching youtube video appropriate with input song name	
	url = await yt_search(item_id)
	list_json = [url]
	json_object = json.dumps(list_json, indent=1)
	with open("sample.json", "w") as outfile:
		outfile.write(json_object)
	await execute_server_js()           #downloading song
	await convertomp3()                 #converting to 
	return [url]


@app.get("/recommendations")

async def recommendations():
	# reccomendations

	rec_artist = []
	rec_song_id = []
	
	#getting song/artist id for reccomendations

	jsonsize = len(data)

	if jsonsize < 2:
		rangestart = 0
		rangeend = jsonsize -1
	else:
		rangestart = jsonsize-2
		rangeend = jsonsize -1
	

	for x in range(rangestart, rangeend+1):
		rec_artist.append(data[x]['artist_id'])


	if jsonsize<2:	
		for x in range(rangestart, rangeend+1):
			rec_song_id.append(data[x]['song_id']) 

	else:
		for x in range(rangestart-1,rangeend+1):
			rec_song_id.append(data[x]['song_id']) 
                
	recommend = sp.recommendations(seed_artists=rec_artist,seed_tracks=rec_song_id,limit=5,country='IN')

	recommended_tracks = []

	for x in range(0,5):
		recommended_tracks.append(recommend['tracks'][x]['name'])

	await errorcheck()
	return recommended_tracks



	
    




        
        


