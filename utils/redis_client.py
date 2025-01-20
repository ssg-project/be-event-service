import redis, os
from dotenv import load_dotenv

# Redis 클라이언트 생성
load_dotenv()
redis_client = redis.Redis(
    host=os.environ['REDIS_HOST'],
    port=6379,
    db=os.environ['REDIS_DB_NAME'],
    username=os.environ['REDIS_USER'],
    password=os.environ['REDIS_PASS'],
    decode_responses=True # 응답을 문자열로 디코딩 (기본적으로 바이트로 반환됨)
)

# 연결 테스트
# try:
#     redis_client.ping()
#     print("Redis에 성공적으로 연결되었습니다!")
# except redis.AuthenticationError:
#     print("인증 실패: 사용자 이름 또는 비밀번호를 확인하세요.")
# except Exception as e:
#     print(f"오류 발생: {e}")