from fastapi import APIRouter, HTTPException,WebSocket, WebSocketDisconnect
from controller.controller import search2hls
from controller.controller import search2hls_rapidapi
from controller.controller import streaming  
from controller.controller import songdetails
from controller.controller import get_id
from controller.controller import get_id_googleapi
from routes.model import verify_access_token
from dbconfig import db
import json

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

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        auth_message = await websocket.receive_text()
        data = json.loads(auth_message)

        token = data["token"]

        search_query = await websocket.receive_text()
        updated_query = search_query[:-4]
        
        artist, song = await songdetails(updated_query)
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
            await search2hls_rapidapi(search_query, websocket)
            hls_file_url = await streaming(id)
            print(hls_file_url)

            if hls_file_url:
                if liked_status:
                    await websocket.send_json({
                    "hls": True,
                    "file": hls_file_url,
                    "liked" : True
                    }) 
                else:
                    await websocket.send_json({
                    "hls": True,
                    "file": hls_file_url
                    })
                
        else:
            await websocket.send_text("No valid video ID found, aborting.")

    except Exception as e:
        # Handle any exceptions during the process
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()


@router.get("/home")
async def home():    
    return{"message": "hello home"}



