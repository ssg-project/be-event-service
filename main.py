from fastapi import FastAPI
from api.concert_api import router as concert_router
from api.reservation_api import router as reservation_router
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
# from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

app = FastAPI()

# router 설정
app.include_router(concert_router, prefix="/api/v1", tags=["concert"])
app.include_router(reservation_router, prefix="/api/v1", tags=["reservation"])

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8003, reload=True)