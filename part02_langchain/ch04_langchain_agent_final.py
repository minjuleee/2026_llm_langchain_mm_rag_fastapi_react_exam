# ─────────────────────────────────────────────────────────────
# 예제 4 (실제 LLM 버전): ChatOpenAI + bind_tools Agent
# ─────────────────────────────────────────────────────────────
#
# 이 예제의 목표:
#   Mock Agent처럼 개발자가 직접 if문으로 Tool을 고르는 것이 아니라,
#   실제 LLM이 사용자의 자연어 질문을 읽고
#   어떤 Tool을 사용할지 스스로 판단하게 만드는 것입니다.

#

# 핵심 흐름:
#   1. 사용자가 질문한다.
#   2. LLM이 질문을 읽고 Tool 사용 여부를 판단한다.
#   3. Tool이 필요하면 AIMessage.tool_calls에 호출 정보가 담긴다.
#   4. 파이썬 코드가 실제 Tool 함수를 실행한다.\
#   5. Tool 실행 결과를 ToolMessage로 다시 LLM에게 전달한다.
#   6. LLM이 Tool 결과를 읽고 최종 자연어 답변을 만든다.

#

# 실행 전 준비:
#   pip install langchain-openai langchain-core python-dotenv
#

# .env 파일 예:
#   OPENAI_API_KEY=sk-...
#

# Mock 버전과 비교했을 때 달라진 점:
#   - LLM의 tool_calls 판단으로 호출할 tool을 결정하는 부분
#   - LLM의 최종 답변 생성으로 대체
#   - Tool 함수 자체는 그대로 재사용 가능

# ─────────────────────────────────────────────────────────────

# json:
#   Python 객체(dict, list)를 JSON 문자열로 바꾸거나,
#   JSON 문자열을 다시 Python 객체로 바꿀 때 사용합니다.
#

# load_dotenv:
#   .env 파일에 적어둔 환경변수를 현재 Python 실행 환경으로 불러옵니다.

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