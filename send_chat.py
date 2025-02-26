import os
from dotenv import load_dotenv
import openai
import json
from openai import OpenAIError


# # 환경 변수 로드
# dotenv_path = path.join(path.dirname(path.dirname(__file__)), ".env")
# load_dotenv(dotenv_path=dotenv_path)



openai.api_key = "OPEN_API_KEY"
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_company_names_with_gpt(chat_message):
    """
    GPT를 사용하여 채팅 메시지에서 회사명으로 보이는 단어들을 추출하는 함수.

    - GPT에게 채팅 메시지와 함께 '회사명' 추출 요청 프롬프트를 전송
    - GPT가 JSON 배열 형태의 결과를 반환하면, 이를 파싱하여 리스트로 반환
    """

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수를 설정하세요.")

    prompt = (
        "다음 채팅 메시지에서 회사명으로 보이는 단어들만 순수하게 추출하여 "
        "JSON 배열 형태로 출력해줘. 예시: [\"회사A\", \"회사B\"]\n\n"
        f"채팅 메시지:\n{chat_message}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 회사명을 추출하는 도우미야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )

    content = response["choices"][0]["message"]["content"]
    try:
        company_names = json.loads(content)
    except json.JSONDecodeError:
        # JSON 형식이 아닐 경우, 간단하게 쉼표로 분리
        company_names = [name.strip() for name in content.strip("[]").split(",")]
    return company_names


if __name__ == "__main__":
    # 테스트용 채팅 메시지 예시
    chat_message = (
        "안녕하세요, 어제 저는 삼성전자와 현대자동차에서 진행한 미팅에 참석했습니다. "
        "또한 애플의 새로운 제품에 대한 소식도 들었습니다."
        "논산딸기 소식은 어떤가요 ?"
    )
    companies_found = extract_company_names_with_gpt(chat_message)
    print("추출된 회사명:", companies_found)
