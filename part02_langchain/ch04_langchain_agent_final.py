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

"""
  실제 ChatOpenAI를 사용하는 CCTV 분석 Agent입니다.
  이 Agent는 다음 작업을 수행합니다.
  1. 사용자 질문을 받습니다.
  2. LLM에게 질문과 분석 데이터를 전달합니다.
  3. LLM이 Tool 사용 여부를 판단합니다.        (Thought)
  4. Tool이 필요하면 실제 Tool을 실행합니다.    (Action)
  5. Tool 결과를 다시 LLM에게 전달합니다.       (Observation)
  6. LLM이 최종 자연어 답변을 생성합니다.

  Mock Agent와 비교:
      Mock Agent:
          개발자가 if문으로 Tool을 선택합니다.
      LLM Agent:
          LLM이 자연어 질문을 읽고 Tool을 선택합니다.
"""
  
# LLM에게 알려줄 역할과 Tool 선택 기준입니다.
SYSTEM_PROMPT = """당신은 CCTV 보안 분석 AI 어시스턴트입니다.
운영자의 질문에 답변하기 위해 제공된 Tool을 적절히 활용하세요.
데이터 구분:
- results_json: risk_level, reason, action 등 위험도 분석 결과
- frames_json : location, detections, bbox 등 원본 탐지 결과

Tool 선택 기준:
- 전체 요약, 위험 건수 질문 → get_risk_summary
- 특정 구역 탐지 현황 질문 → count_objects_in_zone
- 위험 프레임 목록 질문   → filter_danger_frames

중요:
- 위험도, 위험 프레임, risk_level 관련 질문에는 results_json을 사용하세요.
- 구역, 위치, detections, bbox 관련 질문에는 frames_json을 사용하세요.
답변은 한국어로, 핵심 수치를 포함해 명확하게 작성하세요."""


class CCTVLLMAgent :
  
  def __init__(self, results_json, frames_json) :
    """
    Agent 생성자입니다.

    Args:
      results_json:
        위험도 분석 결과 JSON 문자열입니다.
        risk_level, reason, action 등이 들어 있습니다.

      frames_json:
        원본 탐지 결과 JSON 문자열입니다.
        location, detections, bbox 등이 들어 있습니다.
    """
    self.results_json = results_json
    self.frames_json = frames_json
    
    # Agent의 실행 이력을 저장하는 공간 (디버깅 용도)
    # 각 질문마다 (qeury, tool_calls, answer) 등의 정보를 기록
    self.scratchpad = []
    
    

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
  
  agent = CCTVLLMAgent(results_json=results_json, frames_json=frames_json)
  
  

