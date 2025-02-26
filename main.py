from fastapi import FastAPI
from api.concert_api import router as concert_router
from api.reservation_api import router as reservation_router
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging

app = FastAPI()

# router 설정
app.include_router(concert_router, prefix="/api/v1", tags=["concert"])
app.include_router(reservation_router, prefix="/api/v1", tags=["reservation"])

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - event-service - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8003, reload=True)