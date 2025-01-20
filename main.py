from fastapi import FastAPI
from api.concert_api import router as concert_router
from api.reservation_api import router as reservation_router
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# router 설정
app.include_router(concert_router, prefix="/api/v1", tags=["concert"])
app.include_router(reservation_router, prefix="/api/v1", tags=["reservation"])

@app.get("/")
async def read_root():
    return {"message": "Hello World"}
