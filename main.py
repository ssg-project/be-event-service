from fastapi import FastAPI
from api.concert_api import router as concert_router
from api.reservation_api import router as reservation_router
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging
import os

# Kubernetes 환경에서 파드 및 노드 정보 가져오기
pod_name = os.environ.get("POD_NAME", "unknown-pod")
node_name = os.environ.get("NODE_NAME", "unknown-node")

# "event-service" 전용 로거 생성
logger = logging.getLogger("event-service")
logger.setLevel(logging.INFO)

# 중복 핸들러 방지
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        f"{{pod: {pod_name}, node: {node_name}}}"  # pod_name, node_name 직접 추가
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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

Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8003, reload=True)