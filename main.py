import requests
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from news_fetcher import NewsFetcher
from news_analyzer import NewsAnalyzer
import hashlib
from datetime import datetime

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

def create_card_news(title, content, hashtags, image_number):
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
        title_font = ImageFont.truetype(korean_font_path, 65)
        content_font = ImageFont.truetype(korean_font_path, 30)
        source_font = ImageFont.truetype(korean_font_path, 20)
        hashtag_font = ImageFont.truetype(korean_font_path, 25)
    except:
        print("기본 폰트를 사용합니다.")
        title_font = ImageFont.load_default()
        content_font = ImageFont.load_default()
        source_font = ImageFont.load_default()
        hashtag_font = ImageFont.load_default()

    # 여백 설정
    margin_x = 130
    content_max_width = width - (margin_x * 2)
    
    # 제목 줄바꿈 처리 추가
    title_lines = wrap_text(title, title_font, content_max_width)
    
    # 내용 줄바꿈 처리
    content_lines = wrap_text(content, content_font, content_max_width)
    
    # 내용 텍스트의 전체 높이 계산
    content_line_height = content_font.size + 5  # 줄 간격 5px
    total_content_height = len(content_lines) * content_line_height
    
    # 내용 시작 y 좌표
    content_y = 530
    
    # 배경 박스의 패딩 설정
    padding_x = 40
    padding_y = 30
    
    # 해시태그 영역 계산
    hashtag_y = 405
    hashtag_font_size = 25
    hashtag_font = ImageFont.truetype(korean_font_path, hashtag_font_size)
    
    # 해시태그 텍스트 너비 계산
    hashtag_width = get_text_width(hashtags, hashtag_font)
    
    # 해시태그 배경 박스 크기 계산
    hashtag_padding_x = 30
    hashtag_padding_y = 15
    
    # 해시태그 중앙 정렬을 위한 x 좌표 계산
    hashtag_box_width = hashtag_width + (hashtag_padding_x * 2)
    hashtag_box_x = (width - hashtag_box_width) // 2
    
    # 해시태그 배경 박스 좌표
    hashtag_box_left = hashtag_box_x
    hashtag_box_right = hashtag_box_x + hashtag_box_width
    hashtag_box_top = hashtag_y - hashtag_padding_y
    hashtag_box_bottom = hashtag_y + hashtag_font_size + hashtag_padding_y
    
    # 해시태그 배경 박스 그리기
    draw_rounded_rectangle(
        draw,
        [hashtag_box_left, hashtag_box_top, hashtag_box_right, hashtag_box_bottom],
        radius=15,
        fill=(31, 73, 165)
    )
    
    # 해시태그 텍스트 중앙 정렬하여 그리기
    hashtag_text_x = hashtag_box_x + hashtag_padding_x
    draw.text((hashtag_text_x, hashtag_y), hashtags, font=hashtag_font, fill='white')

    # 내용 영역 배경 박스 그리기
    content_box_left = margin_x - padding_x
    content_box_top = content_y - padding_y
    content_box_right = width - margin_x + padding_x
    content_box_bottom = content_y + total_content_height + padding_y
    
    # 내용 영역 둥근 모서리 배경 박스 그리기
    draw_rounded_rectangle(
        draw,
        [content_box_left, content_box_top, content_box_right, content_box_bottom],
        radius=20,
        fill=(31, 73, 165)
    )

    # 제목 그리기
    title_y = 170
    for line in title_lines:
        line_width = get_text_width(line, title_font)
        title_x = (width - line_width) // 2
        draw.text((title_x, title_y), line, font=title_font, fill='black')
        title_y += title_font.size + 10

    # 내용 그리기
    current_y = content_y
    for line in content_lines:
        draw.text((margin_x, current_y), line, font=content_font, fill='white')
        current_y += content_line_height

    # 출처 텍스트 추가 (고정 위치)
    source_text = "※ 출처 : MQ(Money Quotient)"
    draw.text((600, 858), source_text, font=source_font, fill=(100, 100, 100))

    # 오늘 날짜와 순서를 포함한 파일명으로 저장
    os.makedirs('output', exist_ok=True)
    today = datetime.now().strftime('%Y%m%d')
    output_filename = f"{today}_{image_number}.png"
    output_path = os.path.join('output', output_filename)
    img.save(output_path)
    print(f"카드뉴스가 생성되었습니다: {output_path}")

def main():
    # 1. 뉴스 검색 (증시 이슈로 고정, 3개)
    fetcher = NewsFetcher()
    news_results = fetcher.get_formatted_news("증권가 빅뉴스 핫이슈", 2)
    
    if not news_results:
        print("검색 결과가 없습니다.")
        return
    
    # 중복 URL 제거
    unique_news = []
    seen_urls = set()
    for news in news_results:
        if news['source_url'] not in seen_urls:
            unique_news.append(news)
            seen_urls.add(news['source_url'])
    
    analyzer = NewsAnalyzer()
    
    print("\n=== 선택된 뉴스 ===")
    for i, news in enumerate(unique_news, 1):
        print(f"{i}. {news['title']}")
    
    # 각 뉴스에 대해 분석 및 이미지 생성
    for i, news in enumerate(unique_news, 1):
        print(f"\n[{i}/{len(unique_news)}] 뉴스 분석 및 이미지 생성 중...")
        
        # 뉴스 분석
        analysis_result = analyzer.analyze_news(
            title=news['title'],
            content=news['content']
        )
        
        if "error" in analysis_result:
            print(f"뉴스 분석 중 오류가 발생했습니다: {analysis_result['error']}")
            continue
        
        print(f"분석 결과:")
        print(f"제목: {analysis_result['title']}")
        print(f"내용: {analysis_result['content']}")
        print(f"해시태그: {analysis_result['hashtag']}")
        
        # 카드 뉴스 이미지 생성
        create_card_news(
            title=analysis_result['title'],
            content=analysis_result['content'],
            hashtags=analysis_result['hashtag'],
            image_number=i
        )
    
    print("\n모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()
