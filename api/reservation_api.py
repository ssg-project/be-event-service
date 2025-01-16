from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.model import Reservation  # Reservation 모델 가져오기
from utils.database import get_db

router = APIRouter(prefix='/reservation', tags=['reservation'])

# 임시 구현: user_id로 조회
@router.get('/user/{user_id}', description='특정 사용자(user_id)의 모든 예약 내역 조회')
def get_reservations_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자의 모든 예약 내역을 조회합니다.
    """
    try:
        # user_id를 기준으로 예약 데이터를 필터링
        reservations = db.query(Reservation).filter(Reservation.user_id == user_id).all()

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

        return {"user_id": user_id, "reservations": result}

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