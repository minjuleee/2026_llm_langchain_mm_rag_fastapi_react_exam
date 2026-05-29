import json, os, re, base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 한번의 api호출로 이미지 여러장을 분석 시키기
from ch04_01_visionModel_basic import image_to_base64
from ch04_02_vision_api_call import json_parse

# ── 실행 ──────────────────────────────────────────────────────
image_files = ["./vision_sample/blue_parrot.jpeg", 
               "./vision_sample/cat.jpeg", 
               "./vision_sample/hamster.jpeg"]

prompt = """위 이미지들을 순서대로 분석해서 아래 JSON 형식으로만 응답하세요.
{
  "images": [
    {"index": 1, "subject": "피사체", "description": "설명"},
    {"index": 2, "subject": "피사체", "description": "설명"},
    {"index": 3, "subject": "피사체", "description": "설명"}
  ],
  "common_theme": "세 이미지의 공통 주제"
}"""

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_multiple_images(image_files:list[str], prompt:str) -> dict :
  """
  이미지 여러 장을 Vision API로 분석하고 결과를 dict로 반환한다.

  Args:
      image_files : 분석할 이미지 파일 경로 리스트
      prompt     : 분석 지시 (예: "이 이미지의 주제를 JSON으로 알려주세요.")
  Returns:
      LLM이 반환한 JSON을 파싱한 dict
  """
  # 이미지 블럭들을 리스트로 조합
  content_blocks = []

  for image_path in image_files:
    b64, mt = image_to_base64(image_path=image_path)
    content_blocks.append({
      "type": "image_url",
      "image_url": {
        "url": f"data:{mt};base64,{b64}",
        "detail": "high",
      }
    })

  content_blocks.append({"type": "text", "text": prompt})

  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": content_blocks
      }
    ],
    max_tokens=1000
  )
  
  content = response.choices[0].message.content
  return json_parse(content)
  

print("이미지 로딩 중...")
result = analyze_multiple_images(image_files, prompt)
print("\n=== 분석 결과 ===")
print(json.dumps(result, ensure_ascii=False, indent=2))
