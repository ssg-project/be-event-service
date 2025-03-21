from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.model import Reservation, Concert, User  # Reservation 모델 가져오기
from utils.database import get_db
import json

router = APIRouter(prefix='/reservation', tags=['reservation'])

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

# 임시 구현: user_id로 조회
@router.get('/search', description='사용자(user_id)의 모든 예약 내역 조회')
async def get_reservations_by_user(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request)
    """
    특정 사용자의 모든 예약 내역을 조회합니다.
    """
    try:
        # user_id를 기준으로 예약 데이터를 필터링
        reservations = db.query(Reservation).filter(Reservation.user_id == current_user['user_id']).all()

        # 예약 데이터가 없을 경우 예외 처리
        if not reservations:
            raise HTTPException(status_code=404, detail="해당 사용자의 예약 내역이 없습니다.")

        # 결과 데이터를 가공하여 반환
        result = [
            {
                "reservation_id": reservation.reservation_id,
                "concert": {
                    "concert_id": reservation.concert.concert_id,
                    "name": reservation.concert.name,
                    "date": reservation.concert.date,
                    "place": reservation.concert.place,
                    "price": reservation.concert.price,
                },
                "reservation_date": reservation.reservation_date,
            }
            for reservation in reservations
        ]

        return {"user_id": current_user['user_id'], "reservations": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예약 조회 중 오류 발생: {str(e)}")

@router.get('/user/{user_id}/concert/{concert_id}', description='특정 사용자(user_id)가 특정 콘서트(concert_id)에 대해 예약한 내역 조회')
def get_reservation_by_user_and_concert(user_id: int, concert_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자가 특정 콘서트에 대해 예약한 내역을 조회합니다.
    """
    try:
        # user_id와 concert_id를 기준으로 예약 데이터를 필터링
        reservation = db.query(Reservation).filter(
            Reservation.user_id == user_id,
            Reservation.concert_id == concert_id
        ).first()

        # 예약 데이터가 없을 경우 예외 처리
        if not reservation:
            raise HTTPException(status_code=404, detail="해당 사용자와 콘서트에 대한 예약 내역이 없습니다.")

        # 결과 데이터를 가공하여 반환
        result = {
            "reservation_id": reservation.reservation_id,
            "concert": {
                "concert_id": reservation.concert.concert_id,
                "name": reservation.concert.name,
                "date": reservation.concert.date,
                "place": reservation.concert.place,
                "price": reservation.concert.price,
            },
            "reservation_date": reservation.reservation_date,
        }

        return {"user_id": user_id, "reservation": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예약 조회 중 오류 발생: {str(e)}")