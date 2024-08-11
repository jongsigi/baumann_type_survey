import pandas as pd
import sqlite3
import os

# Question과 Answer Column 만들기
def column_setting(col_list, num_answer):
    for i in range(num_answer):
        num_answer = f"answer_{str(i)}"
        col_list.append(num_answer)
    return col_list

def excel_to_sqlite(excel_file, sqlite_db, table_name):
    # 엑셀 파일 읽기
    df = pd.read_excel(excel_file, engine='openpyxl')
    
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(sqlite_db)
    
    # 데이터프레임을 SQLite로 저장
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # 연결 종료
    conn.close()

local_repo = os.path.dirname(os.path.abspath(__file__))
file_name = 'question_list.xlsx'
read_filename = f"{local_repo}/{file_name}"

num_answer = 4
columns = ['no','question']
columns = column_setting(columns, num_answer)

df = pd.read_excel(read_filename, engine='openpyxl', index_col=11)
question_and_answer = pd.DataFrame(columns=columns)
# No./질문/답변 이후 3번째 Column 부터 MBTI 가중치
answer_weight = pd.DataFrame(columns=list(df.columns)[3:])
num_question = 0


for i in range(len(df)):
    question_list = []
    answer_weight.loc[i] = df.iloc[i,3:]
    if i%num_answer == 0:
        question_list = df.iloc[i,0:2].to_list()
        for j in range(num_answer):
            each_answer = df.iloc[i+j, 2]
            question_list.append(each_answer)
        question_and_answer.loc[num_question] = question_list
        num_question += 1        

# 저장하는 파일명에 폴더 위치 고려
file_names = ['question_and_answer.xlsx', 'answer_weight.xlsx']
save_filenames = []
for file_name in file_names:
    local_save_filename = f"{local_repo}/{file_name}"
    save_filenames.append(local_save_filename)

question_and_answer.to_excel(excel_writer=save_filenames[0], engine='openpyxl', index=False)
answer_weight.to_excel(excel_writer=save_filenames[1], engine='openpyxl')

# 여기까지가 Question List를 받으면 질문/답변과 답변의 가중치를 분리하는 과정

# 여기부터 분리된 질문/답변 File과 답변의 가중치를 DB 파일로 저장하는 과정
sqlite_db = f"{local_repo}/qa_and_weight.db"
table_names = ['question_and_answer', 'answer_weight']

for i in range(2):
    excel_to_sqlite(save_filenames[i], sqlite_db, table_names[i])
