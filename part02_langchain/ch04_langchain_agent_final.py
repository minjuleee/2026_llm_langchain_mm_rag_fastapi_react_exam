# ─────────────────────────────────────────────────────────────
# 예제 4 (실제 LLM 버전): ChatOpenAI + bind_tools Agent
# ─────────────────────────────────────────────────────────────
#
# 이 예제의 목표:
#   Mock Agent처럼 개발자가 직접 if문으로 Tool을 고르는 것이 아니라,
#   실제 LLM이 사용자의 자연어 질문을 읽고
#   어떤 Tool을 사용할지 스스로 판단하게 만드는 것입니다.


# 핵심 흐름:
#   1. 사용자가 질문한다.
#   2. LLM이 질문을 읽고 Tool 사용 여부를 판단한다.
#   3. Tool이 필요하면 AIMessage.tool_calls에 호출 정보가 담긴다.
#   4. 파이썬 코드가 실제 Tool 함수를 실행한다.\
#   5. Tool 실행 결과를 ToolMessage로 다시 LLM에게 전달한다.
#   6. LLM이 Tool 결과를 읽고 최종 자연어 답변을 만든다.

# 실행 전 준비:
#   pip install langchain-openai langchain-core python-dotenv
#


import json

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
    SystemMessage,
)

load_dotenv()

# 1. LLM 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

if __name__ == "__main__" :

  import random
  random.seed(42)

  # CCTV 위치 목록
  LOCATIONS = [
    "주차장 A",
    "창고 출입구",
    "로비",
    "비상구 복도",
    "옥상",
  ]     
  
  results = [
    {
      "frame_id": i,
      "risk_level": "위험" if i % 4 == 0 else ("주의" if i % 3 == 0 else "정상"),
      "person_count": random.randint(0, 4),
      "reason": "심야 다인 탐지" if i % 4 == 0 else "일반",
      "action": "경비팀 출동" if i % 4 == 0 else "이상 없음",
    }
    for i in range(1, 11)
  ]

  # 원본 탐지 프레임 데이터 생성
  frames = [
    {
      "frame_id": i,
      "timestamp": f"0{2 if i % 3 == 0 else 1}:{i % 60:02d}",
      "location": LOCATIONS[i % len(LOCATIONS)],
      "detections": [
        {
          "class": "person",
          "bbox": [10, 10, 100, 100],
          "confidence": 0.91,
        }
        for _ in range(random.randint(0, 3))
      ],
    }
    for i in range(1, 11)
  ]
  
  results_json = json.dumps(results, ensure_ascii=False)
  frames_json = json.dumps(frames, ensure_ascii=False)
  
  

