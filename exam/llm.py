# ## **문제 1. API 키 설정 및 클라이언트 준비**

# 다음 조건을 만족하도록 OpenAI API 호출 준비 코드를 작성하시오.

# ### **요구사항**

# 1. OpenAI API 키를 코드에 직접 노출하지 말 것.
# 2. 환경 변수 또는 Colab의 보안 입력 방식을 사용할 것.
# 3. OpenAI 클라이언트를 생성할 것.
# 4. API 키가 없을 경우 사용자에게 안내 메시지를 출력할 것.
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("Error: OpenAI API 키가 설정되지 않았습니다. 환경 변수 'OPENAI_API_KEY'를 확인하세요.")

client = OpenAI(api_key=api_key)


## **문제 2. 사용자 입력을 받아 LLM에게 요청 보내기**
# 사용자로부터 상품 리뷰 문장을 입력받고, OpenAI API를 호출하여 리뷰 분석 결과를 받아오시오.
# ### **입력 예시**
# 배송은 빨랐지만 제품 마감이 조금 아쉽고, 배터리는 오래가서 만족합니다.
# ### **LLM에게 요청할 작업**
# 입력된 리뷰를 분석하여 다음 정보를 추출하도록 요청한다.

# 1. 전체 감성: positive, neutral, negative 중 하나
# 2. 긍정 요인 목록
# 3. 부정 요인 목록
# 4. 한 줄 요약
# 5. 별점 예측: 1~5 사이 정수
user_review = input("상품 리뷰를 입력하세요: ")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "당신은 상품 리뷰 분석 전문가입니다. 리뷰에서 감성, 긍정 요인, 부정 요인, 요약, 별점을 추출합니다."},
        {"role": "user", "content": f"다음 리뷰를 분석해주세요: '{user_review}'"}
    ],
    max_tokens=300,
    temperature=0.5,
)
analysis_result = response.choices[0].message.content
print("\n=== 리뷰 분석 결과 ===")
print(analysis_result)

## **문제 3. JSON 형식으로 응답 받기**
# LLM 응답이 아래 JSON 구조를 따르도록 프롬프트 또는 Structured Output 방식을 사용하시오.
# ### 
# ### **목표 JSON 구조**
# {  "sentiment": "positive",  "positive_points": ["배송이 빠름", "배터리가 오래감"],  "negative_points": ["제품 마감이 아쉬움"],  "summary": "배송과 배터리는 만족스럽지만 마감 품질은 아쉬운 리뷰입니다.",  "rating": 4 }
# ### **요구사항**
# 1. sentiment는 반드시 "positive", "neutral", "negative" 중 하나여야 한다.
# 2. positive_points는 문자열 리스트여야 한다.
# 3. negative_points는 문자열 리스트여야 한다.
# 4. summary는 문자열이어야 한다.
# 5. rating은 1 이상 5 이하의 정수여야 한다.
# OpenAI 공식 문서에 따르면 Structured Outputs는 JSON Schema를 제공했을 때 모델 출력이 해당 스키마를 따르도록 설계된 기능이며, JSON mode와 달리 특정 스키마 준수를 목표로 한다.

import json
json_schema = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "neutral", "negative"],
        },
        "positive_points": {
            "type": "array",
            "items": {"type": "string"},
        },
        "negative_points": {
            "type": "array",
            "items": {"type": "string"},
        },
        "summary": {"type": "string"},
        "rating": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
        },
    },
    "required": [
        "sentiment",
        "positive_points",
        "negative_points",
        "summary",
        "rating",
    ],
    "additionalProperties": False,
}
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "당신은 상품 리뷰 분석 전문가입니다. 응답은 반드시 주어진 JSON Schema를 따라야 합니다.",
        },
        {
            "role": "user",
            "content": f"다음 리뷰를 분석해주세요: {user_review}",
        },
    ],
    max_tokens=300,
    temperature=0.5,
    response_format={
      "type": "json_schema",
      "json_schema": {
        "name": "review_analysis",
        "schema": json_schema,
        "strict": True
      }
    }
)
analysis_result = response.choices[0].message.content
print("\n=== 리뷰 분석 결과 (JSON) ===")
print(analysis_result)
try:
    analysis_dict = json.loads(analysis_result)
    
    
    print("\n JSON 파싱 성공!")
    print(f"감성: {analysis_dict['sentiment']}")
    print(f"긍정 요인: {analysis_dict['positive_points']}")
    print(f"부정 요인: {analysis_dict['negative_points']}")
    print(f"요약: {analysis_dict['summary']}")
    print(f"별점: {analysis_dict['rating']}")
except json.JSONDecodeError:
    print("JSON 파싱 실패: 응답이 유효한 JSON 형식이 아닙니다.") 
except KeyError as e:
    print(f"필수 키 누락: {e}")

except ValueError as e:
    print(f"값 오류: {e}")
    

## **문제 4. JSON 파싱 및 결과 출력**

# API 응답으로 받은 JSON 데이터를 Python 객체로 변환한 뒤, 다음 형식으로 출력하시오.

# ### **출력 예시**

# [리뷰 분석 결과] 전체 감성: positive 예상 별점: 4점 긍정 요인: - 배송이 빠름 - 배터리가 오래감 부정 요인: - 제품 마감이 아쉬움 요약: 배송과 배터리는 만족스럽지만 마감 품질은 아쉬운 리뷰입니다.

# ### **요구사항**

# 1. JSON 문자열을 Python dict 형태로 변환할 것.
# 2. 리스트 데이터는 반복문을 사용하여 출력할 것.
# 3. 키가 없거나 값의 자료형이 잘못된 경우를 고려할 것.
try:
    analysis_dict = json.loads(analysis_result)
    print("\n=== 리뷰 분석 결과 (파싱 후) ===")
    print(f"전체 감성: {analysis_dict.get('sentiment', 'N/A')}")
    print(f"예상 별점: {analysis_dict.get('rating', 'N/A')}점")
    
    positive_points = analysis_dict.get('positive_points', [])
    print("긍정 요인:")
    if isinstance(positive_points, list):
        for point in positive_points:
            print(f"- {point}")
    else:
        print("- N/A (긍정 요인 데이터 형식 오류)")
    
    negative_points = analysis_dict.get('negative_points', [])
    print("부정 요인:")
    if isinstance(negative_points, list):
        for point in negative_points:
            print(f"- {point}")
    else:
        print("- N/A (부정 요인 데이터 형식 오류)")
    
    summary = analysis_dict.get('summary', 'N/A')
    print(f"요약: {summary}")
except json.JSONDecodeError:
    print("❌ JSON 파싱 실패: 응답이 유효한 JSON 형식이 아닙니다.")

## **문제 5. 예외 처리 구현**

# 다음 상황을 고려하여 예외 처리를 구현하시오.

# ### 

# ### **처리해야 할 상황**

# 1. API 키가 없는 경우
# 2. API 호출에 실패한 경우
# 3. LLM 응답이 JSON 형식이 아닌 경우
# 4. JSON에는 존재하지만 필수 키가 누락된 경우
# 5. rating 값이 1~5 범위를 벗어난 경우

# JSON mode를 사용할 경우 유효한 JSON 생성에는 도움이 되지만, 특정 스키마 일치까지 보장하지는 않으므로 검증 로직 또는 Structured Outputs 사용이 필요하다.
## **문제 6. 추가 기능 구현**

# 아래 기능 중 하나 이상을 선택하여 구현하시오.

# ### 

# ### **선택 기능**

# 1. 여러 개의 리뷰를 리스트로 입력받아 반복 분석하기
# 2. 분석 결과를 pandas.DataFrame으로 변환하기
# 3. 분석 결과를 CSV 파일로 저장하기
# 4. 감성별 리뷰 개수 통계 출력하기
# 5. 별점 평균 계산하기
import pandas as pd

reviews = []

while True:
    review = input("상품 리뷰를 입력하세요 (종료하려면 exit 입력): ")

    if review.lower() == "exit":
        break

    reviews.append(review)

analysis_results = []

for review in reviews:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 상품 리뷰 분석 전문가입니다. 응답은 반드시 주어진 JSON Schema를 따라야 합니다.",
                },
                {
                    "role": "user",
                    "content": f"다음 리뷰를 분석해주세요: {review}",
                },
            ],
            max_tokens=300,
            temperature=0.5,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "review_analysis",
                    "schema": json_schema,
                    "strict": True
                }
            }
        )

        analysis_result = response.choices[0].message.content
        analysis_dict = json.loads(analysis_result)

        required_keys = ["sentiment", "positive_points", "negative_points", "summary", "rating"]

        for key in required_keys:
            if key not in analysis_dict:
                raise KeyError(f"필수 키가 누락되었습니다: {key}")

        if analysis_dict["rating"] < 1 or analysis_dict["rating"] > 5:
            raise ValueError("rating 값은 1 이상 5 이하이어야 합니다.")

        analysis_dict["review"] = review
        analysis_results.append(analysis_dict)

    except json.JSONDecodeError:
        print(f"JSON 파싱 실패: {review}")

    except KeyError as e:
        print(f"필수 키 누락: {e}")

    except ValueError as e:
        print(f"값 오류: {e}")

    except Exception as e:
        print(f"API 호출 실패: {e}")


if analysis_results:
    df = pd.DataFrame(analysis_results)

    print("\n=== 분석 결과 DataFrame ===")
    print(df)

    df.to_csv("review_analysis_results.csv", index=False, encoding="utf-8-sig")
    print("\nCSV 파일 저장 완료: review_analysis_results.csv")

    print("\n=== 감성별 리뷰 개수 ===")
    print(df["sentiment"].value_counts())

    print("\n=== 별점 평균 ===")
    print(f"{df['rating'].mean():.2f}점")

else:
    print("\n분석된 리뷰가 없습니다.")
