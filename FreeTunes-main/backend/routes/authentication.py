from fastapi import APIRouter, HTTPException, Depends, Response, Request, BackgroundTasks
from models.model import user, playlist, PlaylistItem
from dbconfig import db
from pymongo.errors import PyMongoError
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from routes.model import model_router
import urllib.request
import json
from pathlib import Path
from datetime import datetime, timedelta
from bson import ObjectId
from jose import jwt, JWTError
import os

dotenv_path = Path('./client.env')

SECRET_KEY = os.getenv('SECRET_COOKIE_KEY')
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))



class VerifyEmail(BaseModel):
    jsonURL: str

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


@model_router.post("/verify/email")
async def verify_email(request: VerifyEmail, response: Response):
    try:
        jsonURL = request.jsonURL
        try:
            with urllib.request.urlopen(jsonURL) as url:
                data = json.loads(url.read().decode())
                email = data["user_email_id"]
        except Exception as e:
                raise HTTPException(status_code=400, detail={"email":email,"verified":False,"message":"User email ID not found in the response."})

        user = await db["users"].find_one({"email": email})
        
        if not user:
            raise HTTPException(status_code=404, detail={"email":email,"verified":False, "message":"User not found"})

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"user_id": str(user["_id"]), "email": email}
        token = create_access_token(data=token_data, expires_delta=access_token_expires)

        return {
            "verified" : True,
            "message": "Verified successfully.",
            "access_token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "playlist": user.get("playlist", []),
                "history": user.get("history", []),
            }
        }
    
    except Exception as e:
        print(f"Error while verifying OTP: {e}")
        raise HTTPException(status_code=500, detail={"email":email,"verified":False, "message":"Internal Server Error"})



@model_router.post("/verify/email/new")
async def verify_email_new(request: VerifyEmail, response: Response):
    try:
        jsonURL = request.jsonURL

        try:
            with urllib.request.urlopen(jsonURL) as url:
                data = json.loads(url.read().decode())
                email = data["user_email_id"]
        except Exception as e:
                raise HTTPException(status_code=400, detail={"email":email,"verified":False,"message":"User email ID not found in the response."})

        user = await db["users"].find_one({"email": email})

        if user:
            raise HTTPException(status_code=404, detail={"email":email,"verified":False, "message":"User already exists"})

        return{
            "email" : email, "verified" : True, "message" : "Email Verified"
        }

    except Exception as e:
        print(f"Error while verifying OTP: {e}")
        raise HTTPException(status_code=500, detail={"verified":False, "message":"Internal Server Error"})
 