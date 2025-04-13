import random
import smtplib
from mailjet_rest import Client
from fastapi import APIRouter, HTTPException, Depends, Response, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from bson import ObjectId
from jose import jwt, JWTError
from dotenv import load_dotenv
from pathlib import Path
import os
from models.model import user, playlist, PlaylistItem
from dbconfig import db
from pymongo.errors import PyMongoError
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

dotenv_path = Path('./client.env')
load_dotenv(dotenv_path=dotenv_path)

SECRET_KEY = os.getenv('SECRET_COOKIE_KEY')
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

class PlaylistUpdateRequest(BaseModel):
    action: str  
    song: PlaylistItem  
    name: str
    userID: str
    liked: Optional[bool]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PlaylistUpdateResponse(BaseModel):
    name: str
    userID: str
    songs: List[PlaylistItem]  
    liked: Optional[bool]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

model_router = APIRouter()

# Pydantic Models
# class OtpRequest(BaseModel):
#     email: EmailStr

# class VerifyOtpRequest(BaseModel):
#     email: EmailStr
#     otp: str

class TokenRequest(BaseModel):
    access_token: str


# def send_email(email: str, otp: str):
#     data = {
#         'Messages': [
#             {
#                 "From": {
#                     "Email": "nfreetunes@gmail.com", 
#                     "Name": "FreeTunes"
#                 },
#                 "To": [
#                     {
#                         "Email": email,
#                     }
#                 ],
#                 "Subject": "Your OTP Code",
#                 "TextPart": f"Your OTP code is: {otp}. It is valid for 10 minutes.",
#                 "HTMLPart": f"<h3>Your OTP code is: <strong>{otp}</strong></h3><p>It is valid for 10 minutes.</p>"
#             }
#         ]
#     }

#     try:
#         result = mailjet.send.create(data=data)

#         if result.status_code == 200:
#             print("OTP email sent successfully!")
#         else:
#             print(f"Failed to send OTP email. Status: {result.status_code}")
#             print(result.json())
    
#     except Exception as e:
#         print(f"Error while sending email: {e}")
        
#     except Exception as e:
#         print(f"Failed to send email: {e}")
#         raise HTTPException(status_code=500, detail="Failed to send OTP email.")


# @model_router.post("/generate/otp")
# async def generate_otp(request: OtpRequest, background_tasks: BackgroundTasks):
#     try:
#         email = request.email
        
        
#         otp = str(random.randint(100000, 999999))
#         time = datetime.utcnow() + timedelta(minutes=10)  
#         expiry_time = time.replace(microsecond=0)

#         try:
#             result = await db["otps"].update_one(
#                 {"email": email}, 
#                 {"$set": {"otp": otp, "expiry": expiry_time}}, 
#                 upsert=True
#             )
#         except PyMongoError as e:
#             print(f"MongoDB error while updating OTP for {email}: {str(e)}")
#             raise HTTPException(status_code=500, detail={"generated":False})        
        

#         updated_document = await db["otps"].find_one({"email": email})

#         if updated_document["otp"] != otp or updated_document["expiry"] != expiry_time:
#             print(f"Failed to update or insert OTP entry for {email}.")
#             raise HTTPException(status_code=500, detail={"generated":False})

#         send_email(email, otp)
#         return {"generated": True}

#     except Exception as e:
#         print(f"Error while generating OTP: {e}")
#         raise HTTPException(status_code=500, detail={"generated":False})

# @model_router.post("/verify/otp")
# async def verify_otp(request: VerifyOtpRequest, response: Response):
#     try:
#         email = request.email
#         otp = request.otp
        
#         otp_entry = await db["otps"].find_one({"email": email})
#         if not otp_entry:
#             raise HTTPException(status_code=404, detail={"verified":False, "message":"OTP not found for the provided email."})
        
#         if otp_entry["otp"] != otp:
#             raise HTTPException(status_code=400, detail={"verified":False, "message":"Invalid OTP."})
        
#         if otp_entry["expiry"] < datetime.utcnow():
#             raise HTTPException(status_code=400, detail={"verified":False, "message": "OTP has expired."})
        
#         user = await db["users"].find_one({"email": email})
#         if not user:
#             raise HTTPException(status_code=404, detail={"verified":False, "message":"User not found"})

#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         token_data = {"user_id": str(user["_id"]), "email": email}
#         token = create_access_token(data=token_data, expires_delta=access_token_expires)

#         await db["otps"].delete_one({"email": email})

#         return {
#             "verified" : True,
#             "message": "OTP verified successfully.",
#             "access_token": token,
#             "user": {
#                 "id": str(user["_id"]),
#                 "name": user["name"],
#                 "email": user["email"],
#                 "playlist": user.get("playlist", []),
#                 "history": user.get("history", []),
#             }
#         }
    
#     except Exception as e:
#         print(f"Error while verifying OTP: {e}")
#         raise HTTPException(status_code=500, detail={"verified":False, "message":"Internal Server Error"})

#verify otp for new user
# @model_router.post("/verify/otp-new")
# async def verify_otp_new(request: VerifyOtpRequest, response: Response):
#     try:
#         email = request.email
#         otp = request.otp
#         print(email)
#         print(otp)
#         otp_entry = await db["otps"].find_one({"email": email})

#         if not otp_entry:
#             print('check 1')
#             raise HTTPException(status_code=404, detail={"verified":False, "message":"OTP not found for the provided email."})
        
#         if otp_entry["otp"] != otp:
#             print('check 2')
#             raise HTTPException(status_code=400, detail={"verified":False, "message":"Invalid OTP."})
        
#         if otp_entry["expiry"] < datetime.utcnow():
#             print('check 3')
#             raise HTTPException(status_code=400, detail={"verified":False, "message": "OTP has expired."})
        
#         await db["otps"].delete_one({"email": email})

#         return {
#             "verified" : True,
#             "message": "OTP verified successfully."
#         }
    

#     except Exception as e:
#         print(f"Error while verifying OTP: {e}")
#         raise HTTPException(status_code=500, detail={"verified":False, "message":"Internal Server Error"})

@model_router.post("/create/user")
async def create_user(item: user, request: Request):
    try:
        print('Attempting to create a new item...')

        print(item.name)
        print(item.email)
        existing_user = await db["users"].find_one({"email": item.email})
        if existing_user:
            print(f"User with email {item.email} already exists.")
            raise HTTPException(status_code=400, detail={"status": False, "message": "A user with this email already exists."})
        
        
        item_dict = item.dict(by_alias=True)
        item_dict["history"] = []
        result = await db["users"].insert_one(item_dict)
        print(f"Item inserted with ID: {result.inserted_id}")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"user_id": str(result.inserted_id), "email": item.email}
        token = create_access_token(data=token_data, expires_delta=access_token_expires)
        
        default_playlist = playlist(
            name="Liked",
            userID=str(result.inserted_id),
            songs=[],
            liked=True
        )

        playlist_dict = default_playlist.dict(by_alias=True)
        playlist_result = await db["playlist"].insert_one(playlist_dict)
        print(f"Liked playllist inserted with ID : {playlist_result.inserted_id}")

        await db["users"].update_one(
            {"_id": result.inserted_id},
            {"$set": {"playlist": [str(playlist_result.inserted_id)]}}
        )

        created_item = await db["users"].find_one({"_id": result.inserted_id})
        
        if created_item:
            created_item["_id"] = str(created_item["_id"])
        
        if not created_item:
            raise HTTPException(status_code=404, detail={"status": False, "message": "Failed to retrieve the created item from the database"})
        
        return {
            "status": True,
            "user": {
                "id": str(created_item["_id"]),
                "name": item.name,  # Ensure name is returned
                "email": item.email,  # Ensure email is returned
                "playlist": created_item.get("playlist", []),
                "history": created_item.get("history", []),
            },
            "access_token": token
        }

    except Exception as e:
        print(f"Error while creating user: {e}")
        raise HTTPException(status_code=500, detail={"status": False, "message": "An unexpected error occurred while creating the user."})

@model_router.post("/verify/token")
async def verify_token(request: TokenRequest):    
    try:
        token = request.access_token
        if not token:
            raise HTTPException(status_code=401, detail={"auth" : False, "message": "Unauthorized: Token not found."})
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail={"auth" : False, "message": "Unauthorized: Invalid or expired token."})
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail={"auth" : False, "message": ""})
        
        user_data = await db["users"].find_one({"_id": ObjectId(user_id)})

        if user_data:
            user_data["_id"] = str(user_data["_id"])

        if not user_data:
            raise HTTPException(status_code=401, detail={"auth" : False, "message": "Unauthorized: User not found."})
        
        return {
            "auth" : True,
            "message": "Token is valid", 
                "user": {
                "id": str(user_data["_id"]),
                "name": user_data["name"],  # Ensure name is returned
                "email": user_data["email"],  # Ensure email is returned
                "playlist": user_data.get("playlist", []),
                "history": user_data.get("history", []),
            }}

    except Exception as e:
        print(f"Error while verifying token: {e}")
        raise HTTPException(status_code=500, detail={"auth" : False, "message": "An unexpected error occurred while verifying the token."})

@model_router.post("/create/playlist", response_model=playlist)
async def create_playlist(item: playlist, request: Request):
    try:
        print('Verifying user for creating a playlist...')
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID missing in token.")
        
        print('Attempting to create a new playlist...')
        playlist_dict = item.dict(by_alias=True)
        
        result = await db["playlist"].insert_one(playlist_dict)
        print(f"Playlist inserted with ID: {result.inserted_id}")
        
        created_playlist = await db["playlist"].find_one({"_id": result.inserted_id})
        if created_playlist:
            created_playlist["_id"] = str(created_playlist["_id"])
        if not created_playlist:
            raise HTTPException(status_code=404, detail="Failed to retrieve the created playlist from the database.")
        
        update_result = await db["users"].update_one(
            {"_id": ObjectId(user_id)}, 
            {"$push": {"playlist": str(result.inserted_id)}}
        )

        print(update_result)

        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found while updating playlists.")
        
        return created_playlist

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error while creating playlist: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the playlist.")
    
@model_router.put("/update/user/{user_id}", response_model=user)
async def update_user(user_id: str, updated_data: user, request: Request):
    try:
        print('Verifying user for updating user data...')
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        token_user_id = payload.get("user_id")
        if not token_user_id or token_user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only update your own data.")
        
        print(f"Attempting to update user with ID: {user_id}")
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format.")
        
        updated_data_dict = updated_data.dict(exclude_unset=True, by_alias=True)
        
        result = await db["users"].update_one(
            {"_id": ObjectId(user_id)}, {"$set": updated_data_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found.")
        
        updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if updated_user:
            updated_user["_id"] = str(updated_user["_id"])

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found after update.")
        
        return updated_user

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error while updating user: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the user.")

@model_router.put("/update/playlist/{playlist_id}", response_model=PlaylistUpdateResponse)
async def update_playlist(playlist_id: str, updated_data: PlaylistUpdateRequest, request: Request):
    try:
        print('Verifying user for updating playlist...')
        
        # Authorization logic
        authorization_header = request.headers.get("authorization")
        if not authorization_header:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found")
        
        payload = verify_access_token(authorization_header)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID missing in token.")
        
        # Validate playlist ID
        print(f"Attempting to update playlist with ID: {playlist_id}")
        if not ObjectId.is_valid(playlist_id):
            raise HTTPException(status_code=400, detail="Invalid playlist ID format.")
        
        playlist = await db["playlist"].find_one({"_id": ObjectId(playlist_id)})
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found.")
        
        if playlist.get("userID") != user_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only update your own playlists.")
        
        # Handle the action and song update
        action = updated_data.action
        song = updated_data.song

        if not song or not song.songName or not song.artistName:
            raise HTTPException(status_code=400, detail="Song information missing or invalid.")

        # Get the existing songs from the playlist
        existing_songs = playlist.get("songs", [])

        # Convert existing songs to dictionaries (in case they're objects)
        existing_songs = [
            song.dict() if isinstance(song, PlaylistItem) else song
            for song in existing_songs
        ]

        # Add or remove the song based on the action
        if action == "add":
            if any(existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName for existing_song in existing_songs):
                raise HTTPException(status_code=400, detail="Song already exists in the playlist.")
            existing_songs.append(song.dict())
        elif action == "remove":
            existing_songs = [
                existing_song for existing_song in existing_songs
                if not (existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName)
            ]
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'.")

        # Update the playlist
        updated_data_dict = updated_data.dict(exclude_unset=True)
        updated_data_dict['songs'] = existing_songs  # Ensure songs are dictionaries
        updated_data_dict.pop('action', None) 

        result = await db["playlist"].update_one(
            {"_id": ObjectId(playlist_id)}, {"$set": updated_data_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Playlist not found.")
        
        # Fetch and return the updated playlist
        updated_playlist = await db["playlist"].find_one({"_id": ObjectId(playlist_id)})
        if updated_playlist:
            updated_playlist["_id"] = str(updated_playlist["_id"])
        
        if not updated_playlist:
            raise HTTPException(status_code=404, detail="Playlist not found after update.")
        
        return PlaylistUpdateResponse(**updated_playlist)

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error while updating playlist: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the playlist.")

@model_router.get("/playlist", response_model=List[playlist])
async def get_playlist(request : Request):

    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthoriized: User ID missing")
        
        user_data = await db["users"].find_one({"_id":ObjectId(user_id)})

        if not user_data:
            raise HTTPException(status_code=401, detail="user not found")
        
        playlist_ids = user_data.get("playlist", [])
        if not playlist_ids:
            return []
        
        playlists = await db["playlist"].find({"_id": {"$in": [ObjectId(pid) for pid in playlist_ids]}}).to_list(length=None)

        filtered_playlists = []

        for playlist in playlists:
            playlist["_id"] = str(playlist["_id"])
            # if playlist.get("liked") is not True:
            #     filtered_playlists.append(playlist)

        # return filtered_playlists
        return playlists
    
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        raise HTTPException(status_code=500, detail="Unexpected Error occured while fetching playlists")
    
@model_router.post("/playlist/id")
async def get_playlist_id(request: Request):
    try:
        body = await request.json()
        playlistName = body.get("playlistName")
        userID = body.get("userID")
        token = request.headers.get("authorization")

        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID missing in token.")
        
        if user_id != userID:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access your own playlists.")
        
        
        playlist = await db["playlist"].find_one({"name": playlistName, "userID": userID})
        
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found.")
        
        return str(playlist["_id"])
    
    except Exception as e:
        print(f"Error while fetching playlist ID: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the playlist ID.")

@model_router.get("/playlist/{playlist_id}", response_model=playlist)
async def get_playlist_by_id(playlist_id:str, request: Request):
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")

        print(playlist_id)
        playlist = await db["playlist"].find_one({"_id":ObjectId(playlist_id), "userID": user_id})

        if not playlist:
            print('1')
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        return playlist
    except Exception as e:
        print(f"Error while fetching playlist: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occured")

@model_router.put("/update/playlist/popup/{playlist_id}", response_model=PlaylistUpdateResponse)
async def update_playlist_popup(playlist_id :str, updated_data: PlaylistUpdateRequest, request: Request):
    try:
        print('Verifying user for updating playlist...')
        
        # Authorization logic
        authorization_header = request.headers.get("authorization")
        if not authorization_header:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found")
        
        payload = verify_access_token(authorization_header)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID missing in token.")
        
        # Validate playlist ID
        print(f"Attempting to update playlist with ID: {playlist_id}")
        if not ObjectId.is_valid(playlist_id):
            raise HTTPException(status_code=400, detail="Invalid playlist ID format.")
        
        playlist = await db["playlist"].find_one({"_id": ObjectId(playlist_id)})
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found.")
        
        if playlist.get("userID") != user_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only update your own playlists.")
        
        # Handle the action and song update
        action = updated_data.action
        song = updated_data.song

        if not song or not song.songName or not song.artistName:
            raise HTTPException(status_code=400, detail="Song information missing or invalid.")

        # Get the existing songs from the playlist
        existing_songs = playlist.get("songs", [])

        # Convert existing songs to dictionaries (in case they're objects)
        existing_songs = [
            song.dict() if isinstance(song, PlaylistItem) else song
            for song in existing_songs
        ]

        # Add or remove the song based on the action
        # if action == "add":
        #     if not any(existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName for existing_song in existing_songs):
        #         existing_songs.append(song.dict())
        # elif action == "remove":
        #     existing_songs = [
        #         existing_song for existing_song in existing_songs
        #         if not (existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName)
        #     ]
        # else:
        #     raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'.")

        if action == "add":
            if not any(existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName for existing_song in existing_songs):
                existing_songs.append(song.dict())
        elif action == "remove":
            if any(existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName for existing_song in existing_songs):
                existing_songs = [
                    existing_song for existing_song in existing_songs
                    if not (existing_song['songName'] == song.songName and existing_song['artistName'] == song.artistName)
                ]
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'.")

        # Update the playlist
        updated_data_dict = updated_data.dict(exclude_unset=True)
        updated_data_dict['songs'] = existing_songs  # Ensure songs are dictionaries
        updated_data_dict.pop('action', None) 

        result = await db["playlist"].update_one(
            {"_id": ObjectId(playlist_id)}, {"$set": updated_data_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Playlist not found.")
        
        # Fetch and return the updated playlist
        updated_playlist = await db["playlist"].find_one({"_id": ObjectId(playlist_id)})
        if updated_playlist:
            updated_playlist["_id"] = str(updated_playlist["_id"])
        
        if not updated_playlist:
            raise HTTPException(status_code=404, detail="Playlist not found after update.")
        
        return PlaylistUpdateResponse(**updated_playlist)

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error while updating playlist: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the playlist.")    

@model_router.put("/update/history", response_model=user)
async def update_song_history(song_data: dict, request: Request):
    print("Received request at the endpoint")  
    try:
        # Extract user ID from the request token
        print("Received song data:", song_data)
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")
        
        # Validate song data
        song = song_data.get('songName')
        artist = song_data.get('artistName')
        if not song or not artist:
            raise HTTPException(status_code=400, detail="Invalid song data.")

        # Find the user by ID
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        # Update the user's history
        history_entry = {"songName": song, "artistName": artist}
        result = await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"history": history_entry}}  # Push the song to the history array
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found.")

        updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])

        return updated_user

    except Exception as e:
        print(f"Error while updating song history: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating song history.")
    
@model_router.get("/get/history", response_model= List[PlaylistItem])
async def get_history(request: Request):
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID missing in token.")
        
        user = await db["users"].find_one({"_id":ObjectId(user_id)})

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        history = user.get("history", [])

        return [PlaylistItem(**entry) for entry in history]
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        print(f"Error while fetching song history: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching song history.")

@model_router.post("/gets/playlist", response_model=playlist)
async def get_single_playlist(request: Request) :
    print("Request received at /gets/playlist")
    try:
        body = await request.json()
        playlistName = body.get("playlistName")
        userID = body.get("userID")
        token = request.headers.get("authorization")

        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized: Token not found.")
        
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized: User ID missing in token.")
        
        if user_id != userID:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access your own playlists.")
        
        
        playlist = await db["playlist"].find_one({"name": playlistName, "userID": userID})
        
        if not playlist:
            print('1')
            raise HTTPException(status_code=404, detail="Playlist not found.")
        
        return playlist
    
    except Exception as e:
        print(f"Error while fetching playlist ID: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the playlist ID.")
