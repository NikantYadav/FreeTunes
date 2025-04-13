from fastapi import APIRouter, HTTPException,WebSocket, WebSocketDisconnect
from controller.controller import search2hls
from controller.controller import search2hls_rapidapi_noHLS
from controller.controller import streaming  
from controller.controller import songdetails
from controller.controller import get_id
from controller.controller import get_id_googleapi
from routes.model import verify_access_token
from dbconfig import db
import json
from connection_manager import active_connection
import asyncio
from dotenv import load_dotenv
from pathlib import Path
import os 
from pydantic import BaseModel
import requests

dotenv_path = Path('./client.env')
load_dotenv(dotenv_path=dotenv_path)

SPOTIFY_SERVER_URL = str(os.getenv('SPOTIFY_SERVER_URL'))

async def heartbeat(websocket: WebSocket):
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type":"ping"})
    except Exception as e:
        print(f"Heartbeat error or client disconnected: {e}")

async def check_if_liked(artist: str, song: str, token: str) -> bool:
    try:
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")

        user_id = payload.get("user_id")
        print(user_id)
        liked_playlist = await db["playlist"].find_one({"userID": user_id, "liked": True})
        if not liked_playlist:
            return False

        for item in liked_playlist["songs"]:
            if item["songName"] == song and item["artistName"] == artist:
                return True
        return False
    except Exception as e:
        print(f"Error in checking liked song status: {e}")
        return False

async def spotify_server(query: str, server_url: str):
    try:
        url = f"{server_url}/spotify"
        response = requests.post(url, params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            print(f"Artist: {data['artist']}, Song: {data['song']}")
            return data
        else:
            print(f"Error {response.status_code}: {response.json().get('detail')}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

router = APIRouter()

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     print('New websocket connection attempting to connect')
#     await websocket.accept()
#     print('Websocket accepted')
#     active_connection.add(websocket)

#     heartbeat_task = asyncio.create_task(heartbeat(WebSocket))

#     try:
#         print('waiting for auth message')
#         auth_message = await websocket.receive_text()
#         print(f"Auth message received: {auth_message}")
#         if not auth_message:
#             await websocket.close(code=1008)
#             return
#         data = json.loads(auth_message)

#         token = data["token"]
#         if not token:
#             await websocket.close(code=1008)
#             return
        
#         await websocket.send_json({"status": "auth_ok"})
#         print("Auth OK sent, waiting for search query...")
#         search_query = await websocket.receive_text()
#         print(f"Search query received: {search_query}")
#         updated_query = search_query[:-4]
#         print("Looking for search details")
#         artist, song = await songdetails(updated_query)
#         print("Search Details found")
#         print(updated_query)

#         id = await get_id_googleapi(search_query)

#         liked_status = await check_if_liked(artist, song, token)

#         await websocket.send_json({
#             "artist": artist,
#             "song": song,
#             "id" : id,
#             "hls": False,
#             "liked" : liked_status 
#         })
        
#         if id:
#             await search2hls_rapidapi(search_query, websocket)
#             hls_file_url = await streaming(id)
#             print(hls_file_url)

#             if hls_file_url:
#                 if liked_status:
#                     await websocket.send_json({
#                     "hls": True,
#                     "file": hls_file_url,
#                     "liked" : True
#                     }) 
#                 else:
#                     await websocket.send_json({
#                     "hls": True,
#                     "file": hls_file_url
#                     })
                
#         else:
#             await websocket.send_text("No valid video ID found, aborting.")

#     except WebSocketDisconnect:
#         print("Clinet Disconnected")
#     except Exception as e:
#         # Handle any exceptions during the process
#         await websocket.send_text(f"Error: {str(e)}")
#     finally:
#         heartbeat_task.cancel()
#         active_connection.remove(websocket)
#         await websocket.close()

@router.websocket("/ws")
async def websocket_endpoint_noHLS(websocket: WebSocket):
    print('New websocket connection attempting to connect')
    await websocket.accept()
    print('Websocket accepted')
    active_connection.add(websocket)

    heartbeat_task = asyncio.create_task(heartbeat(websocket))

    try:
        print('waiting for auth message')
        auth_message = await websocket.receive_text()
        print(f"Auth message received: {auth_message}")
        if not auth_message:
            await websocket.close(code=1008)
            return
        data = json.loads(auth_message)

        token = data["token"]
        if not token:
            await websocket.close(code=1008)
            return
        
        await websocket.send_json({"status": "auth_ok"})
        print("Auth OK sent, waiting for search query...")
        search_query = await websocket.receive_text()
        print(f"Search query received: {search_query}")
        updated_query = search_query[:-4]
        print("Looking for search details")
        #artist, song = await songdetails(updated_query)
        data = await spotify_server(updated_query, SPOTIFY_SERVER_URL)
        artist = data['artist']
        song = data['song']
        print("Search Details found")
        print(updated_query)
        
        id = await get_id_googleapi(search_query)
        
        liked_status = await check_if_liked(artist, song, token)

        await websocket.send_json({
            "artist": artist,
            "song": song,
            "id" : id,
            "hls": False,
            "liked" : liked_status 
        })
        
        if id:
            print('enter')
            streamLink = await search2hls_rapidapi_noHLS(search_query, websocket)
            print("Stream Link found")

            if streamLink:
                if liked_status:
                    await websocket.send_json({
                    "hls": True,
                    "file": streamLink,
                    "liked" : True
                    }) 
                else:
                    await websocket.send_json({
                    "hls": True,
                    "file": streamLink
                    })
        else:
            await websocket.send_text("No valid video ID found, aborting.")

    except WebSocketDisconnect:
        print("Clinet Disconnected")
    except Exception as e:
        # Handle any exceptions during the process
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        heartbeat_task.cancel()
        active_connection.remove(websocket)
        await websocket.close()


class SearchRequest(BaseModel):
    token: str
    search_query: str

@router.post("/mp3")
async def mp3_noHLS(request: SearchRequest):
    try:
        token = request.token
        search_query = request.search_query

        if not token or not search_query:
            raise HTTPException(status_code=400, detail="Missing token or search query")

        updated_query = search_query[:-4]

        print(f"Processing search for: {updated_query}")

        data = await spotify_server(updated_query, SPOTIFY_SERVER_URL)
        artist = data['artist']
        song = data['song']

        video_id = await get_id_googleapi(search_query)

  
        liked_status = await check_if_liked(artist, song, token)

        # Prepare the initial response
        response = {
            "artist": artist,
            "song": song,
            "id": video_id,
            "hls": False,
            "liked": liked_status
        }

        if video_id:
            stream_link = await search2hls_rapidapi_noHLS(search_query, None)
            if stream_link:
                response["hls"] = True
                response["file"] = stream_link

        else:
            response["error"] = "No valid video ID found"

        return response

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/home")
async def home():    
    return{"message": "hello home"}



    