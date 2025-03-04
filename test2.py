import os
import sqlite3
import pandas as pd
import openai
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 현재 작업 디렉토리에 있는 경우)
load_dotenv()
# 실제 API 키를 직접 입력하거나 환경 변수로 불러옵니다.



openai.api_key = os.getenv("OPENAI_API_KEY")


def get_historical_records(client_keyword):
    """
    b2b.db에서 client_name에 client_keyword가 포함된 기록을 조회하여
    지원일과 details 정보를 DataFrame으로 반환합니다.
    """
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "b2b.db")
    conn = sqlite3.connect(db_path)
    query = """
        SELECT support_date, details, client_name
        FROM b2b 
        WHERE client_name LIKE ?
        ORDER BY support_date
    """
    df = pd.read_sql_query(query, conn, params=[f"%{client_keyword}%"])
    conn.close()
    return df

def generate_resolution_answer(question, historical_df):
    """
    조회된 과거 사례를 바탕으로, 질문에 대해 DB에 기록된 사건만을 사용하여
    해결방안과 함께, 자주 발생한 문제, 사건 발생 날짜, 향후 대비 및 준비해야 할 사항을
    체계적으로 정리한 인사이트를 생성하는 함수입니다.
    """
    # 과거 사례 정리 (지원일과 details)
    if historical_df.empty:
        historical_text = "관련된 과거 사례가 없습니다."
    else:
        historical_lines = []
        for idx, row in historical_df.iterrows():
            historical_lines.append(f"{row['support_date']}: {row['details']}")
        historical_text = "\n".join(historical_lines)

    # 프롬프트 구성:
    # 반드시 아래 제공된 '과거 사례'에 기록된 사건만 사용하도록 명시합니다.
    prompt = (
        "아래는 고객사의 과거 네트워크 관련 사건 기록입니다. "
        "이 목록 외의 어떠한 추가적인 사건도 언급하지 말고, "
        "오직 아래 제공된 기록에 나타난 사건들만을 바탕으로 질문에 대한 답변을 작성해줘. "
        "답변에는 해결방안, 문제 분석, 사건 발생 날짜, 동종업계 사례 분석 그리고 향후 대비 및 준비 사항이 포함되어야 하며, "
        "제공된 DB 자료에 없는 모든 정보는 배제해야 해. 답변은 각 항목별로 명확하게 구분해서 작성해줘.\n\n"
        "과거 사례:\n"
        f"{historical_text}\n\n"
        "질문: " + question + "\n"
        "답변:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # 사용 모델; 실제 지원 여부 확인 필요
        messages=[
            {"role": "system", "content": (
                "너는 네트워크 이슈 해결방안과 인사이트를 제시하는 도우미야. "
                "너의 답변은 반드시 아래 제공된 '과거 사례'에 기록된 사건만을 참조해야 하며, "
                "외부에서 학습된 정보를 절대 포함하면 안 된다."
            )},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    answer = response["choices"][0]["message"]["content"]
    return answer




if __name__ == "__main__":
    # 사용자로부터 질문과 관련 회사명(클라이언트 키워드) 입력받기
    question = input("질문을 입력하세요 (예: '신한은행 네트워크 장애 발생했을 때 해결했던 방법들을 정리해서 사건 날짜와 함께 알려줘.'): ")
    client_keyword = input("검색할 회사명을 입력하세요 (예: '신한은행'): ")

    # DB에서 해당 회사의 과거 기록 조회
    historical_df = get_historical_records(client_keyword)

    # GPT를 이용하여 해결방안 생성
    answer = generate_resolution_answer(question, historical_df)

    print("\n생성된 해결방안:")
    print(answer)