from fastapi import FastAPI
import uvicorn
from routers import users, vehicles
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.include_router(users.user_router, prefix="/user")
app.include_router(vehicles.vehicle_router, prefix="/vehicle")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
    

if __name__== "__main__":
    uvicorn.run("main:app", host ="0.0.0.0",port=8000, reload=True)
    