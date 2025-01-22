from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.model import Concert
from utils.database import get_db
from datetime import date, datetime
from utils.redis_client import redis_client
from dto.dto import CreateConcert

router = APIRouter(prefix='/concert', tags=['concert'])

@router.get('/list', description='콘서트 목록 조회')
def get_concert_list(db: Session = Depends(get_db)):
    """
    콘서트 목록을 조회합니다.
    """
    try:
        concerts = db.query(Concert).all()  # 모든 콘서트 데이터를 가져옵니다.
        return {"concerts": concerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"콘서트 조회 실패: {str(e)}")

@router.get('/{concert_id}', description='특정 콘서트 상세 조회')
def get_concert_detail(concert_id: str, db: Session = Depends(get_db)):
    """
    특정 콘서트의 상세 정보를 조회합니다.
    """
    try:
        concert = db.query(Concert).filter(Concert.concert_id == concert_id).first()
        if not concert:
            raise HTTPException(status_code=404, detail="콘서트를 찾을 수 없습니다.")
        return {"concert": concert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"콘서트 상세 조회 실패: {str(e)}")

@router.post('/create', description='콘서트 생성')
def create_concert(
    request_body: CreateConcert,
    db: Session = Depends(get_db)
):
    try:
        data = Concert(
            name=request_body.name,
            description=request_body.description,
            seat_count=request_body.seat_count,
            date=request_body.date,
            place=request_body.place,
            price=request_body.price,
            image=request_body.image
        )
        datetime_obj = datetime.combine(request_body.date, datetime.min.time())
        timestamp = datetime_obj.timestamp()
        
        db.add(data)
        db.commit()
        db.refresh(data)
        redis_client.set(f"concert:{data.concert_id}:seat_reserved_count", "0")
        redis_client.set(f"concert:{data.concert_id}:seat_all_count", "0")
        redis_client.expireat(f"concert:{data.concert_id}:seat_reserved_count", int(timestamp))
        redis_client.expireat(f"concert:{data.concert_id}:seat_all_count", int(timestamp))
        
        return {
            "message": "성공"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"오류: {str(e)}")
    