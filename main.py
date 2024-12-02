import requests
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from news_fetcher import NewsFetcher
from news_analyzer import NewsAnalyzer
import hashlib
from datetime import datetime
from post_instagram import InstagramAPI

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

def create_news_card_image(title, content, hashtags, output_path):
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
            output_path = f"output/{today}_{idx}.png"
            os.makedirs("output", exist_ok=True)
            
            create_news_card_image(
                title=analysis_result['title'],
                content=analysis_result['content'],
                hashtags=analysis_result['hashtag'],
                output_path=output_path
            )
            
            # 생성된 이미지 경로 저장
            generated_images.append(output_path)
            print(f"뉴스 카드 {idx} 생성 완료: {output_path}")
            
        except Exception as e:
            print(f"뉴스 {idx} 처리 중 오류 발생: {str(e)}")
            continue
    
    return generated_images

def upload_to_instagram(image_paths):
    """생성된 이미지를 Instagram에 업로드"""
    try:
        # 도메인 URL 가져오기
        domain_url = os.getenv("DOMAIN_URL")
        if not domain_url:
            raise ValueError("DOMAIN_URL이 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # 이미지 URL 리스트 생성
        image_urls = [f"{domain_url}/card-news-generator/{path}" for path in image_paths]
        
        # Instagram API 초기화 및 업로드
        instagram = InstagramAPI()
        result = instagram.post_image(image_urls)
        
        if result["success"]:
            print(f"Instagram 업로드 성공! 게시물 ID: {result['post_id']}")
            print(result["status"])
            return True
        else:
            print(f"Instagram 업로드 실패: {result['error']}")
            return False
            
    except Exception as e:
        print(f"Instagram 업로드 중 오류 발생: {str(e)}")
        return False

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
        upload_success = upload_to_instagram(generated_images)
        
        if upload_success:
            print("\n모든 처리가 완료되었습니다!")
        else:
            print("\n이미지 생성은 완료되었으나 Instagram 업로드에 실패했습니다.")
        
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
