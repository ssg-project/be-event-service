from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, case
from models.model import Concert, Reservation, User
from utils.database import get_db
from datetime import date, datetime
from utils.redis_client import redis_client
from dto.dto import CreateConcert
import json

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

async def get_current_user(request: Request):
    scope_data = request.headers.get("X-Scope")

    if not scope_data:
        raise HTTPException(status_code=401, detail="인증되지 않은 요청입니다.")
    try:
        scope = json.loads(scope_data)
        user = scope.get("user")
        if not user or not user.get('is_authenticated'):
            raise HTTPException(status_code=401, detail="인증되지 않은 요청입니다.")
        return user
    except:
        raise HTTPException(status_code=401, detail="인증되지 않은 요청입니다.")

@router.get('/{concert_id}', description='특정 콘서트 상세 조회')
async def get_concert_detail(
    concert_id: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    특정 콘서트의 상세 정보를 조회합니다.
    """
    try:
        print(request)
        print(1)
        current_user = await get_current_user(request)
        print(current_user)

        concert = db.query(
            Concert.concert_id,
            Concert.name,
            Concert.image,
            Concert.description,
            Concert.seat_count,
            Concert.date,
            Concert.place,
            Concert.created_at,
            Concert.updated_at,
            case(
                (func.count(Reservation.concert_id) >= Concert.seat_count, True),
                else_=False
            ).label('is_full')
        ).outerjoin(Reservation, Concert.concert_id == Reservation.concert_id)\
         .filter(Concert.concert_id == concert_id)\
         .group_by(Concert.concert_id)\
         .first()

        if not concert:
            raise HTTPException(status_code=404, detail="콘서트를 찾을 수 없습니다.")

        # 로그인한 사용자의 경우에만 예약 여부 확인
        is_reserved = db.query(Reservation).filter(
            Reservation.concert_id == concert_id,
            Reservation.user_id == current_user['user_id']
        ).first() is not None
        
        return {
            "concert": {
                "concert_id": concert.concert_id,
                "name": concert.name,
                "image": concert.image,
                "description": concert.description,
                "seat_count": concert.seat_count,
                "date": concert.date,
                "place": concert.place,
                "created_at": concert.created_at,
                "is_full": concert.is_full,
                "is_reserved": is_reserved
            }
        }
    except Exception as e:
        print(f"Error in get_concert_detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"콘서트 상세 조회 실패: {str(e)}")

# @router.get('/{concert_id}', description='특정 콘서트 상세 조회')
# def get_concert_detail(
#     concert_id: str, 
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     """
#     특정 콘서트의 상세 정보를 조회합니다.
#     """
#     try:
#         # 사용자 인증 정보 확인 (선택적)
#         current_user_id = None
#         if "user" in request.scope:
#             user_data = request.scope["user"]
#             current_user_id = user_data.get("user_id")

#         concert = db.query(
#             Concert.concert_id,
#             Concert.name,
#             Concert.image,
#             Concert.description,
#             Concert.seat_count,
#             Concert.date,
#             Concert.place,
#             Concert.created_at,
#             Concert.updated_at,
#             case(
#                 (func.count(Reservation.concert_id) >= Concert.seat_count, True),
#                 else_=False
#             ).label('is_full')
#         ).outerjoin(Reservation, Concert.concert_id == Reservation.concert_id)\
#          .filter(Concert.concert_id == concert_id)\
#          .group_by(Concert.concert_id)\
#          .first()

#         if not concert:
#             raise HTTPException(status_code=404, detail="콘서트를 찾을 수 없습니다.")

#         # 로그인한 사용자의 경우에만 예약 여부 확인
#         # is_reserved = False
#         # if current_user_id:
#         is_reserved = db.query(Reservation).filter(
#             Reservation.concert_id == concert_id,
#             Reservation.user_id == current_user_id
#         ).first() is not None
        
#         return {
#             "concert": {
#                 "concert_id": concert.concert_id,
#                 "name": concert.name,
#                 "image": concert.image,
#                 "description": concert.description,
#                 "seat_count": concert.seat_count,
#                 "date": concert.date,
#                 "place": concert.place,
#                 "created_at": concert.created_at,
#                 "is_full": concert.is_full,
#                 "is_reserved": is_reserved
#             }
#         }
#     except Exception as e:
#         print(f"Error in get_concert_detail: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"콘서트 상세 조회 실패: {str(e)}")

@router.post('/create', description='콘서트 생성')
def create_concert(
    request_body: CreateConcert,
    db: Session = Depends(get_db),
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

        print("concert_id:", data.concert_id)
        print(redis_client)
        # redis_client.set("1","1")
        # redis_client.set(f"concert:{data.concert_id}:seat_reserved_count", "0")
        # redis_client.set(f"concert:{data.concert_id}:seat_all_count", "0")
        # redis_client.expireat(f"concert:{data.concert_id}:seat_reserved_count", int(timestamp))
        # redis_client.expireat(f"concert:{data.concert_id}:seat_all_count", int(timestamp))

        redis_client.set(f"concert:{data.concert_id}:seat_reserved_count", "0")
        redis_client.set(f"concert:{data.concert_id}:seat_all_count", data.seat_count)
        redis_client.expireat(f"concert:{data.concert_id}:seat_reserved_count", int(timestamp))
        redis_client.expireat(f"concert:{data.concert_id}:seat_all_count", int(timestamp))
                    
        return {
            "message": "성공"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"오류: {str(e)}")
    