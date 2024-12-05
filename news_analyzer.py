from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import json
import logging

# Load environment variables
load_dotenv()

class NewsAnalyzer:
    def __init__(self):
        """Initialize the NewsAnalyzer with Gemini Pro model"""
        self.logger = logging.getLogger('NewsGenerator')
        
        # API 키 확인
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.logger.error("환경 변수 GOOGLE_API_KEY가 설정되지 않았습니다.")
            raise ValueError("환경 변수 GOOGLE_API_KEY가 설정되지 않았습니다.")

        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.8
        )
        
        # Define the analysis prompt template
        self.prompt = PromptTemplate.from_template(
"""당신은 글로벌 주식 전문 기자야.
현재 인스타그램용 카드 뉴스를 제작하고 있어.
주어진 뉴스 제목과 본문을 확인하여 독자들의 관심을 끌 수 있는 컨텐츠를 만들어줘.

<뉴스 제목>
{news_title}
</뉴스 제목>

<뉴스 본문>
{news_content}
</뉴스 본문>

1. 카드 뉴스 제목은 독자들의 주목을 한눈에 끌수 있게 자극적으로 작성해 줘.
2. 카드 뉴스 제목의 글자수는 **공백 포함 15자 이내**로 작성해 줘.
3. 카드 뉴스 내용은 주어진 본문 내용의 핵심만 뽑아 간결하게 작성해야 합니다.
4. 카드 뉴스 내용의 글자수는 **공백 포함 90자 이내**로 작성해 줘.
5. 제목과 내용의 길이 조건을 반드시 지켜주세요.
6. **전문적인** 톤과 **간결한 대화체**를 사용해줘.
7. 최종 결과는 출력형식에 맞게 JSON 형태로 만들어 줘.
8. 카드 뉴스 제목과 내용은 한국어로 만들어줘.
9. **"자세한 내용은 기사에서 확인하세요"**와 같은 문구는 포함하지 않도록 해 주세요. 카드 뉴스 내용은 핵심만 담고 있어야 합니다.


다음과 같은 JSON 형식으로 출력해줘:

{{
    "title": "글로벌 성장 급브레이크!",
    "content": "글로벌 성장 둔화가 지속되며 유럽과 신흥국 주식 시장 약세가 두드러지고 있습니다. 향후 주식 변동성을 높일수 있으며, 투자자들은 방어적 자세로 포트폴리오 점검을 서둘러야 합니다."
}}"""
        )
        
        # Create the chain using LCEL
        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def analyze_news(self, title, content):
        try:
            self.logger.info(f"뉴스 분석 시작 - 제목: {title[:30]}...")
            
            # LLM 체인 실행
            response_text = self.chain.invoke({
                "news_title": title,
                "news_content": content
            })
            
            # Clean the response text and ensure it's valid JSON
            response_text = response_text.strip()
            if not response_text.startswith('{'):
                response_text = response_text[response_text.find('{'):]
            if not response_text.endswith('}'):
                response_text = response_text[:response_text.rfind('}')+1]
            
            try:
                parsed_result = json.loads(response_text)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON 파싱 오류: {e}")
                self.logger.error(f"응답 텍스트: {response_text}")
                return {"error": "JSON 파싱 오류"}
            
            # Ensure all required fields are present
            required_fields = ['title', 'content']
            for field in required_fields:
                if field not in parsed_result:
                    self.logger.error(f"필수 필드 누락: {field}")
                    self.logger.error(f"파싱된 결과: {parsed_result}")
                    return {"error": f"필수 필드 누락: {field}"}
            
            self.logger.info("뉴스 분석 완료")
            return parsed_result
            
        except Exception as e:
            self.logger.error(f"분석 중 오류 발생: {str(e)}")
            return {"error": f"분석 중 오류 발생: {str(e)}"}

# Usage example
if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    
    # Test with sample news
    sample_title = "An under-the-radar indicator shows global growth is stalling, research firm says - Markets Insider"
    sample_content = "Global Growth Is Stalling and Investors Need to Get Defensive: BCA - Markets Insider Markets Stocks Indices Commodities Cryptocurrencies Currencies ETFs News Stocks Advertising Policies An under-the-radar indicator that's historically served as a bellwether for global economic growth is pointing to a slowdown, BCA Research said. Both European and emerging markets stocks sold off immediately after Trump's win and continue to trade below their pre-election levels, while a gauge of non-US stocks saw its steepest daily decline since August the week after Election Day. Those dynamics, plus stretched equity valuations, make for a higher risk of volatility in the coming months, so investors should rotate into defensive positions, the analysts say. Stock Indices Stocks Stock Market News Advertising Policies"
    
    result = analyzer.analyze_news(sample_title, sample_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))
