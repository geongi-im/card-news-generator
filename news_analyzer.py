from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

class NewsAnalyzer:
    def __init__(self):
        """Initialize the NewsAnalyzer with Gemini Pro model"""
        
        # API 키 확인
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("환경 변수 GOOGLE_API_KEY가 설정되지 않았습니다.")

        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Define the analysis prompt template
        self.prompt = PromptTemplate.from_template(
"""너는 마케팅에 뛰어난 세계적인 주식 전문 기자야.
현재 인스타그램용 카드뉴스를 제작하고 있어.
뉴스 제목과 본문을 확인하여 카드뉴스를 만들어 줘

<뉴스 제목>
{news_title}
</뉴스 제목>

<뉴스 본문>
{news_content}
</뉴스 본문>

1. 카드 뉴스 제목은 독자들의 주목을 한눈에 끌수 있게 자극적으로 만들어 줘.
2. 반드시 카드 뉴스 제목은 **15자 이내**로 만들어 줘.
3. 카드 뉴스 내용은 주어진 본문 내용에 핵심만 요약해서 **130자 이내**로 만들어 줘.
4. 카드 뉴스 내용과 어울리는 hashtag를 3개 만들어 줘.
5. hashtag 하나당 글자수는 7자 이내로 만들어 줘.
6. "친절"하고 "재미"있으며 "전문적인" 톤과 매너의 대화체를 사용해줘
7. 이모지는 사용하지 않고 기자가 뉴스를 전달하는 말투를 사용해줘.
8. 카드 뉴스 제목과 본문의 생동감 있는 표현과 강조된 문장으로 느낌을 살려 줘.
9. 최종 결과는 출력형식에 맞게 JSON 형태로 만들어 줘.
10. 카드 뉴스 제목,내용,hastag는 한국어로 해줘.
11. 뉴스 기사를 확인하라는 말은 넣지마. 가능한 카드 뉴스 내용에 요약해서 넣어줘.

다음과 같은 JSON 형식으로 출력해줘:

{{
    "title": "여기에 15자 이내의 제목",
    "content": "여기에 130자 이내의 내용 요약",
    "hashtag": "#태그1 #태그2 #태그3"
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
                print(f"JSON 파싱 오류: {e}")
                print(f"응답 텍스트: {response_text}")
                return {"error": "JSON 파싱 오류"}
            
            # Ensure all required fields are present
            required_fields = ['title', 'content', 'hashtag']
            for field in required_fields:
                if field not in parsed_result:
                    print(f"필수 필드 누락: {field}")
                    print(f"파싱된 결과: {parsed_result}")
                    return {"error": f"필수 필드 누락: {field}"}
            
            return parsed_result
            
        except Exception as e:
            print(f"분석 중 오류 발생: {str(e)}")
            return {"error": f"분석 중 오류 발생: {str(e)}"}

# Usage example
if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    
    # Test with sample news
    sample_title = "An under-the-radar indicator shows global growth is stalling, research firm says - Markets Insider"
    sample_content = "Global Growth Is Stalling and Investors Need to Get Defensive: BCA - Markets Insider Markets Stocks Indices Commodities Cryptocurrencies Currencies ETFs News Stocks Advertising Policies An under-the-radar indicator that's historically served as a bellwether for global economic growth is pointing to a slowdown, BCA Research said. Both European and emerging markets stocks sold off immediately after Trump's win and continue to trade below their pre-election levels, while a gauge of non-US stocks saw its steepest daily decline since August the week after Election Day. Those dynamics, plus stretched equity valuations, make for a higher risk of volatility in the coming months, so investors should rotate into defensive positions, the analysts say. Stock Indices Stocks Stock Market News Advertising Policies"
    
    result = analyzer.analyze_news(sample_title, sample_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))
