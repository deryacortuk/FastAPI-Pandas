from fastapi import FastAPI, APIRouter
from pydantic import BaseModel,json
from api.settings import payload, headers, base_url
import pandas as pd
import requests
import json
from typing import List, Dict, Any
from io import StringIO


user_router = APIRouter(tags=["User"])

@user_router.post("/")
def user_login():
    url = f'{base_url}/index.php/login'
    response = requests.request("POST", url, json=payload, headers=headers)
    access_token = response.json()["oauth"]["access_token"]
    return access_token

