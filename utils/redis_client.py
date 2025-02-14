import redis, os

# Redis 클라이언트 생성
# redis_client = redis.Redis(
#     host=os.environ['REDIS_HOST'],
#     port=os.environ['REDIS_PORT'],
#     db=os.environ['REDIS_DB'],
#     username=os.environ['REDIS_USER'],
#     password=os.environ['REDIS_PASS'],
#     decode_responses=True # 응답을 문자열로 디코딩 (기본적으로 바이트로 반환됨)
# )
redis_client = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], decode_responses=True)

# 연결 테스트
# try:
#     redis_client.ping()
#     print("Redis에 성공적으로 연결되었습니다!")
# except redis.AuthenticationError:
#     print("인증 실패: 사용자 이름 또는 비밀번호를 확인하세요.")
# except Exception as e:
#     print(f"오류 발생: {e}")