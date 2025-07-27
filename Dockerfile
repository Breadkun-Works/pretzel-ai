# VM 부하 최적화를 위해 경량화 이미지 사용
FROM python:3.12-slim

# 작업 디렉터리
WORKDIR /app

# 시스템 패키지(빌드툴) 설치 없이 바로 requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 버퍼링 제거
ENV PYTHONUNBUFFERED=1

# 컨테이너 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]