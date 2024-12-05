import os
from dotenv import load_dotenv
from tavily import TavilyClient
from datetime import datetime, timedelta
import requests
import logging

# .env 파일에서 환경 변수 로드
load_dotenv()

class NewsFetcher:
    def __init__(self):
        self.logger = logging.getLogger('NewsGenerator')
        self.api_key = os.getenv('TAVILY_API_KEY')
        if not self.api_key:
            self.logger.error("TAVILY_API_KEY가 .env 파일에 설정되지 않았습니다.")
            raise ValueError("TAVILY_API_KEY가 .env 파일에 설정되지 않았습니다.")
        self.client = TavilyClient(api_key=self.api_key)

    def fetch_news(self, query, max_results=5):
        """주어진 쿼리로 뉴스를 검색합니다."""
        try:
            self.logger.info(f"뉴스 검색 시작: {query}")
            
            # Tavily API 호출
            response = self.client.search(
                query=f"{query}",
                topic="news",
                days=1,
                search_depth="advanced",
                include_images=False,
                include_raw_content=False,
                max_results=max_results
            )

            # 결과 처리
            news_articles = []
            for result in response.get('results', []):
                article = {
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'published_date': result.get('published_date', ''),
                }
                news_articles.append(article)

            self.logger.info(f"검색된 뉴스 개수: {len(news_articles)}")
            return news_articles

        except Exception as e:
            self.logger.error(f"뉴스 검색 중 오류 발생: {str(e)}")
            return []

    def get_formatted_news(self, query, max_results=5):
        """뉴스를 검색하고 포맷팅된 결과를 반환합니다."""
        self.logger.info(f"포맷팅된 뉴스 검색 시작: {query}")
        news_list = self.fetch_news(query, max_results)
        if not news_list:
            self.logger.warning("검색된 뉴스가 없습니다.")
            return None
        
        formatted_news = []
        for news in news_list:
            formatted_news.append({
                'title': news.get('title', '제목 없음'),
                'content': news.get('content', '내용 없음'),
                'source_url': news.get('url', '')
            })
        
        self.logger.info(f"포맷팅된 뉴스 개수: {len(formatted_news)}")
        return formatted_news

def main():
    # 사용 예시
    fetcher = NewsFetcher()
    news_list = fetcher.get_formatted_news("증시 이슈", 3)
    
    if news_list:
        for i, news in enumerate(news_list, 1):
            print(f"\n=== 뉴스 {i} ===")
            print("제목:", news['title'])
            print("내용:", news['content'])
            print("출처:", news['source_url'])
    else:
        print("뉴스를 가져오는데 실패했습니다.")

if __name__ == "__main__":
    main()
