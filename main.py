import requests
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from news_fetcher import NewsFetcher
from news_analyzer import NewsAnalyzer
import hashlib
from datetime import datetime
from instagram_post import InstagramAPI

def get_text_width(text, font):
    """텍스트의 실제 픽셀 너비를 계산"""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]

def wrap_text(text, font, max_width):
    """텍스트를 주어진 너비에 맞게 줄바꿈"""
    words = text.split()
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        test_line = current_line + " " + word
        if get_text_width(test_line, font) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    return lines

def draw_rounded_rectangle(draw, coords, radius, fill):
    """둥근 모서리 사각형 그리기"""
    x1, y1, x2, y2 = coords
    diameter = radius * 2
    
    # 모서리 부분을 제외한 사각형 그리기
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)  # 중앙 세로 영역
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)  # 중앙 가로 영역
    
    # 네 모서리에 원 그리기
    draw.ellipse([x1, y1, x1 + diameter, y1 + diameter], fill=fill)  # 좌상단
    draw.ellipse([x2 - diameter, y1, x2, y1 + diameter], fill=fill)  # 우상단
    draw.ellipse([x1, y2 - diameter, x1 + diameter, y2], fill=fill)  # 좌하단
    draw.ellipse([x2 - diameter, y2 - diameter, x2, y2], fill=fill)  # 우하단

def get_optimal_font_size(text, max_width, max_height, font_path, start_size=70):
    """텍스트에 맞는 최적의 폰트 크기를 찾습니다."""
    font_size = start_size
    min_size = 40  # 최소 폰트 크기
    
    while font_size > min_size:
        font = ImageFont.truetype(font_path, font_size)
        lines = wrap_text(text, font, max_width)
        
        # 전체 텍스트 높이 계산
        total_height = len(lines) * (font_size + 10)  # 줄 간격 10
        
        # 텍스트가 최대 높이와 너비 내에 들어가는지 확인
        if total_height <= max_height:
            return font_size, lines, total_height
        
        font_size -= 5
    
    # 최소 폰트 크기로도 맞지 않으면 최소 크기 반환
    font = ImageFont.truetype(font_path, min_size)
    lines = wrap_text(text, font, max_width)
    total_height = len(lines) * (min_size + 10)
    return min_size, lines, total_height

def create_news_card_image(title, content, output_path):
    background_path = os.path.join('img', 'background_card_blank.png')
    korean_font_path = os.path.join('fonts', 'NanumBarunGothicBold.ttf')

    try:
        img = Image.open(background_path)
    except FileNotFoundError:
        print("배경 이미지를 찾을 수 없습니다.")
        return
    
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    try:
        title_font = ImageFont.truetype(korean_font_path, 70)
        content_font = ImageFont.truetype(korean_font_path, 43)
        source_font = ImageFont.truetype(korean_font_path, 20)
    except:
        print("기본 폰트를 사용합니다.")
        title_font = ImageFont.load_default()
        content_font = ImageFont.load_default()
        source_font = ImageFont.load_default()

    # 여백 설정
    margin_x = 130
    content_max_width = width - (margin_x * 2)
    
    # 제목 줄역 설정
    title_max_width = width - (margin_x * 2)
    title_max_height = 200  # 제목 영역 최대 높이
    
    # 최적의 제목 폰트 크기 찾기
    title_font_size, title_lines, title_total_height = get_optimal_font_size(
        title,
        title_max_width,
        title_max_height,
        korean_font_path
    )
    
    title_font = ImageFont.truetype(korean_font_path, title_font_size)
    
    # 제목 시작 y좌표 (120으로 고정)
    title_y = 120
    
    # 내용 영역 시작 y좌표 동적 조정
    content_y = max(360, title_y + title_total_height + 40)  # 최소 360px, 제목 아래 40px 여백
    
    # 내용 폰트 및 줄바꿈 처리
    content_font = ImageFont.truetype(korean_font_path, 43)
    
    # 내용 텍스트를 여러 줄로 나누기
    content_lines = []
    current_line = ""
    
    # 단어 단위로 분리
    words = content.split()
    
    for word in words:
        # 현재 줄에 단어를 추가했을 때의 너비 계산
        test_line = f"{current_line} {word}".strip()
        test_bbox = draw.textbbox((0, 0), test_line, font=content_font)
        test_width = test_bbox[2] - test_bbox[0]
        
        # 최대 너비(여백 고려)를 초과하지 않으면 현재 줄에 단어 추가
        if test_width <= width - (margin_x * 2):
            current_line = test_line
        else:
            # 현재 줄이 비어있지 않으면 줄 추가
            if current_line:
                content_lines.append(current_line)
            current_line = word
    
    # 마지막 줄 추가
    if current_line:
        content_lines.append(current_line)
    
    # 줄 간격 설정
    content_line_height = 60
    
    # 배경 박스의 패딩 설정
    padding_x = 40
    padding_y = 30
    
    # 내용 영역 배경 박스 그리기
    content_box_left = margin_x - padding_x
    content_box_top = content_y - padding_y
    content_box_right = width - margin_x + padding_x
    content_box_bottom = content_y + (len(content_lines) * content_line_height) + padding_y
    
    # 내용 영역 둥근 모서리 배경 박스 그리기
    draw_rounded_rectangle(
        draw,
        [content_box_left, content_box_top, content_box_right, content_box_bottom],
        radius=20,
        fill=(31, 73, 165)
    )

    # 제목 그리기
    current_title_y = title_y
    for line in title_lines:
        line_width = get_text_width(line, title_font)
        title_x = (width - line_width) // 2
        draw.text((title_x, current_title_y), line, font=title_font, fill='black')
        current_title_y += title_font_size + 10

    # 내용 그리기
    current_y = content_y
    for line in content_lines:
        draw.text((margin_x, current_y), line, font=content_font, fill='white')
        current_y += content_line_height

    # 출처 텍스트 추가 (고정 위치)
    source_text = "※ 출처 : MQ(Money Quotient)"
    draw.text((600, 858), source_text, font=source_font, fill=(100, 100, 100))

    # 이미지 저장
    img.save(output_path)

def create_card_news(news_results):
    """뉴스 결과를 기반으로 카드 뉴스 이미지 생성"""
    generated_images = []
    
    for idx, news in enumerate(news_results, 1):
        try:
            print(f"=== 뉴스 {idx} 처리 중 ===")
            
            # 뉴스 분석
            analyzer = NewsAnalyzer()
            analysis_result = analyzer.analyze_news(news['title'], news['content'])
            
            if not analysis_result:
                print(f"뉴스 {idx} 분석 실패")
                continue
                
            # 이미지 생성
            today = datetime.now().strftime('%Y%m%d')
            base_output_path = f"output/{today}_{idx}.png"
            os.makedirs("output", exist_ok=True)
            
            output_path = base_output_path
            counter = 1
            while os.path.exists(output_path):
                output_path = f"output/{today}_{idx}({counter}).png"
                counter += 1
            
            create_news_card_image(
                title=analysis_result['title'],
                content=analysis_result['content'],
                output_path=output_path
            )
            
            # 생성된 이미지 경로 저장
            generated_images.append(output_path)
            print(f"뉴스 카드 {idx} 생성 완료: {output_path}")
            
        except Exception as e:
            print(f"뉴스 {idx} 처리 중 오류 발생: {str(e)}")
            continue
    
    return generated_images

def main():
    try:
        # 뉴스 검색
        print("=== 뉴스 검색 시작 ===")
        fetcher = NewsFetcher()
        news_results = fetcher.get_formatted_news("증권가 빅뉴스 핫이슈", 5)
        
        if not news_results:
            print("뉴스를 찾을 수 없습니다.")
            return
            
        print(f"총 {len(news_results)}개의 뉴스를 찾았습니다.")
        print("=== 검색된 뉴스 목록 ===")
        for idx, news in enumerate(news_results, 1):
            print(f"\n[뉴스 {idx}]")
            print(f"제목: {news['title']}")
            print(f"URL: {news['source_url']}")
        
        # 중복 URL 제거
        unique_news = []
        seen_urls = set()
        
        print("=== 중복 제거 처리 ===")
        for news in news_results:
            if news['source_url'] not in seen_urls:
                unique_news.append(news)
                seen_urls.add(news['source_url'])
            else:
                print(f"중복 제거된 뉴스: {news['title']} ({news['source_url']})")
        
        print(f"중복 제거 후 {len(unique_news)}개의 뉴스가 남았습니다.")
        
        # 카드 뉴스 이미지 생성
        print("=== 이미지 생성 시작 ===")
        generated_images = create_card_news(unique_news)
        
        if not generated_images:
            print("생성된 이미지가 없습니다.")
            return
        
        print(f"총 {len(generated_images)}개의 카드 뉴스가 생성되었습니다.")
        
        # Instagram 업로드
        print("Instagram에 업로드를 시작합니다...")
        
        # 도메인 URL 가져오기
        domain_url = os.getenv("DOMAIN_URL")
        if not domain_url:
            raise ValueError("DOMAIN_URL이 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # 이미지 URL 리스트 생성
        image_urls = [f"{domain_url}/card-news-generator/{path}" for path in generated_images]

        # 캡션 생성
        weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        now = datetime.now()
        weekday = weekdays[now.weekday()]
        caption = f"{now.year}년 {now.month:02d}월 {now.day:02d}일 {weekday} MQ 글로벌 증권가 뉴스"
        
        # Instagram API 초기화 및 업로드
        instagram = InstagramAPI()
        result = instagram.post_image(image_urls, caption)
        
        if result["success"]:
            print(f"Instagram 업로드 성공! 게시물 ID: {result['post_id']}")
            print(result["status"])
            print("\n모든 처리가 완료되었습니다!")
        else:
            print(f"Instagram 업로드 실패: {result['error']}")
            print("\n이미지 생성은 완료되었으나 Instagram 업로드에 실패했습니다.")
        
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
