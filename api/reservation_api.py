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

# @router.post('/create', description='공연 예약 생성')
# def create_reservation(user_id: int, concert_id: int, db: Session = Depends(get_db)):
#     """
#     특정 사용자(user_id)가 특정 콘서트(concert_id)를 예약합니다.
#     """
#     try:
#         # 사용자와 콘서트가 존재하는지 확인
#         user = db.query(User).filter(User.user_id == user_id).first()
#         concert = db.query(Concert).filter(Concert.concert_id == concert_id).first()

#         if not user:
#             raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
#         if not concert:
#             raise HTTPException(status_code=404, detail="콘서트를 찾을 수 없습니다.")

#         # 중복 예약 확인
#         existing_reservation = db.query(Reservation).filter(
#             Reservation.user_id == user_id,
#             Reservation.concert_id == concert_id
#         ).first()

#         if existing_reservation:
#             raise HTTPException(status_code=400, detail="이미 해당 콘서트에 대한 예약이 존재합니다.")

#         # 콘서트 좌석이 남아있는지 확인
#         reserved_seats = db.query(Reservation).filter(Reservation.concert_id == concert_id).count()
#         if reserved_seats >= concert.seat_count:
#             raise HTTPException(status_code=400, detail="해당 콘서트의 예약 가능한 좌석이 없습니다.")

#         # 예약 생성
#         reservation = Reservation(user_id=user_id, concert_id=concert_id)
#         db.add(reservation)
#         db.commit()
#         db.refresh(reservation)

#         return {
#             "message": "예약이 성공적으로 생성되었습니다.",
#             "reservation": {
#                 "reservation_id": reservation.reservation_id,
#                 "user_id": reservation.user_id,
#                 "concert_id": reservation.concert_id,
#                 "reservation_date": reservation.reservation_date,
#             }
#         }

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"예약 생성 중 오류 발생: {str(e)}")

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