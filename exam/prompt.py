import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = """
당신은 상품 리뷰를 분석하는 AI입니다.
반드시 올바른 JSON 형식으로만 응답하세요.
JSON 외의 설명 문장, 코드블록, 주석은 출력하지 마세요.
"""

user_prompt = """
다음 상품 리뷰를 분석하세요.

[리뷰]
배송은 빨랐지만 제품 마감이 조금 아쉬웠어요. 그래도 가격을 생각하면 나쁘지는 않습니다.

[출력 조건]
1. 상품 리뷰를 분석하세요.
2. JSON 형식으로만 출력하세요.
3. JSON 외 설명 문장은 출력하지 마세요.
4. sentiment 값은 positive, negative, neutral 중 하나만 사용하세요.
5. summary는 리뷰 내용을 한 문장으로 요약하세요.
6. keywords는 핵심 키워드를 배열 형태로 출력하세요.
7. score는 1~5 사이 숫자로 출력하세요.
8. reason에는 sentiment와 score를 판단한 이유를 작성하세요.
9. 올바른 JSON 문법을 사용하세요.

[JSON 출력 형식]
{
  "sentiment": "positive | negative | neutral",
  "summary": "리뷰 내용을 한 문장으로 요약",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "score": 1,
  "reason": "sentiment와 score를 판단한 이유"
}
"""

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
  ],
  temperature=0.7,
  max_tokens=700
)

print(response.choices[0].message.content)