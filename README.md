# Instagram Card News Generator

AI 기반의 자동 증권 뉴스 카드 생성 및 Instagram 포스팅 시스템

## 주요 기능

1. **뉴스 수집 및 분석**
   - 증권가 핫이슈 뉴스 자동 수집
   - Google Gemini AI를 활용한 뉴스 내용 분석
   - 핵심 내용 추출 및 요약

2. **카드 뉴스 생성**
   - 자동화된 이미지 카드 생성
   - 날짜별 자동 파일명 생성 (YYYYMMDD_N.png)
   - 최적화된 텍스트 레이아웃

3. **Instagram 자동 포스팅**
   - 단일/다중 이미지 업로드 지원
   - 자동 캡션 생성 (날짜 포함)
   - 해시태그 자동 생성

## 시스템 요구사항

- Python 3.8 이상
- 필요한 Python 패키지 (requirements.txt 참조)
- Instagram Business 계정
- Google API 키 (Gemini AI용)

## 설치 방법

1. 저장소 클론
   ```bash
   git clone [repository-url]
   cd card_news_generator
   ```

2. 가상환경 생성 및 활성화
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   .\venv\Scripts\activate  # Windows
   ```

3. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 설정
   ```bash
   cp .env.example .env
   # .env 파일을 열어 필요한 API 키와 설정값 입력
   ```

## 환경 변수 설정

`.env` 파일에 다음 환경 변수들을 설정해야 합니다:

- `GOOGLE_API_KEY`: Google Gemini AI API 키
- `INSTAGRAM_ACCESS_TOKEN`: Instagram API 액세스 토큰
- `INSTAGRAM_ACCOUNT_ID`: Instagram 비즈니스 계정 ID
- `DOMAIN_URL`: 이미지 호스팅 도메인 URL

## 사용 방법

1. 프로그램 실행
   ```bash
   python main.py
   ```

2. 실행 과정
   - 최신 증권 뉴스 수집
   - AI 기반 뉴스 분석 및 요약
   - 카드 뉴스 이미지 생성
   - Instagram 자동 업로드

## 프로젝트 구조

```
card_news_generator/
├── main.py              # 메인 실행 파일
├── news_fetcher.py      # 뉴스 수집 모듈
├── news_analyzer.py     # 뉴스 분석 모듈
├── post_instagram.py    # Instagram 포스팅 모듈
├── requirements.txt     # 패키지 의존성
├── .env.example        # 환경 변수 템플릿
├── img/                # 이미지 리소스
└── fonts/             # 폰트 파일
```

## 주의사항

- Instagram API 사용을 위해 비즈니스 계정이 필요합니다
- API 키와 토큰은 절대 공개하지 마세요
- 이미지 호스팅을 위한 웹 서버가 필요합니다

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.
