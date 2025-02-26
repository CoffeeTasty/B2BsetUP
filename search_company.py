import sqlite3

# b2b.db가 test.py와 같은 디렉토리에 있다고 가정
conn = sqlite3.connect('b2b.db')
cursor = conn.cursor()

# 사용자에게 회사명 입력받음.
company_name = input("회사명을 입력하세요: ")

# 사용자 입력값을 대문자로 변환하고 공백 제거
company_name_processed = company_name.upper().replace(" ", "")

# DB에 저장된 client_name은 이미 대문자이며 공백없이 저장되어 있다고 가정
query = """
SELECT * FROM b2b
WHERE client_name LIKE ?
ORDER BY support_type DESC
"""
cursor.execute(query, ('%' + company_name_processed + '%',))
rows = cursor.fetchall()
print("검색결과 : ", rows, end='\n\n')

if rows:
    print(f"고객사 : {rows[0][5]}")
    for i in range(len(rows)):
        print(f"{rows[i][-2]} - {rows[i][-1]}")
else:
    print("검색 결과가 없습니다.")

conn.close()
