import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 1. 데이터베이스 연결 및 모든 행 조회
conn = sqlite3.connect('b2b.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM b2b")
rows = cursor.fetchall()

# 2. 사용자 입력을 벡터화
model = SentenceTransformer('all-MiniLM-L6-v2')

user_text = input("특이사항을 입력하세요: ")

# 3. 각 행의 details 열을 벡터화하여 유사도 검사
matching_rows = []
threshold = 0.75

for row in rows:
    details = row[-1]  # details 열은 마지막 컬럼으로 가정

    user_embedding = model.encode(user_text)
    details_embedding = model.encode(details)

    sim = cosine_similarity([user_embedding], [details_embedding])[0][0]
    print(sim)
    if sim >= threshold:
        matching_rows.append((row, sim))

conn.close()

# 4. 유사도가 threshold 이상인 결과 출력
print(f"\n유사도 {threshold} 이상인 결과:")
for row, sim in matching_rows:
    print(f"유사도: {sim:.4f} - {row}")
