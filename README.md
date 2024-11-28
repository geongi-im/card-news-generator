# Card News Generator

뉴스 기사를 자동으로 분석하고 카드뉴스 형태로 생성해주는 Python 기반 프로젝트입니다.

## 주요 기능

- 뉴스 기사 자동 수집 및 분석
- AI를 활용한 뉴스 내용 요약
- 카드뉴스 형태의 이미지 자동 생성

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd card_news_generator
```

2. 가상환경 생성 및 활성화
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env.example` 파일을 `.env`로 복사하고 필요한 API 키를 설정합니다:
- GOOGLE_API_KEY
- TAVILY_API_KEY

## 사용 방법

1. 메인 프로그램 실행
```bash
python main.py
```

## 프로젝트 구조

- `main.py`: 메인 실행 파일
- `news_analyzer.py`: 뉴스 분석 모듈
- `news_fetcher.py`: 뉴스 수집 모듈
- `image_coordinates.py`: 이미지 좌표 처리
- `fonts/`: 폰트 파일 디렉토리
- `output/`: 생성된 카드뉴스 저장 디렉토리

## 의존성

- python-dotenv==1.0.0
- tavily-python==0.5.0
- Pillow==10.1.0
- langchain==0.1.0
- langchain-google-genai==0.0.6
- google-generativeai==0.3.2

## 라이선스

MIT License
