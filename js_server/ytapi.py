from fastapi import FastAPI
import json
from moviepy.editor import *
import subprocess
from youtubesearchpython import VideosSearch

app = FastAPI()

async def check():
	txt1 = 'upper function ran properly'
	print(txt1)
	return txt1

global searchquery
global link
global url

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
	url = await yt_search(item_id)
	list_json = [url]
	json_object = json.dumps(list_json, indent=1)
	with open("sample.json", "w") as outfile:
		outfile.write(json_object)
	await execute_server_js()
	await convertomp3()
	check_result = await check()
	return [url,check_result]
    




        
        


