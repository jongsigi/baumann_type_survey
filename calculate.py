from models import db, User, UserAnswer
import pandas as pd
import sqlite3

num_answer = 4

def recon_answer_matrix(df, method):
    
    # 전체 답변 개수를 전달받은 df를 통해 len 함수로 가져오기
    num_question = df.shape[1]
    # 답변 = 1 / 답변X = 0으로 하기 위해 질문수*N지선다 길이의 Value = 0인 List 형성   
    answer_list = [0 for i in range(num_question*num_answer)]
    
    # Value은 0-3이기 때문에 4*N번째 질문 + Value인 인덱스를 1로 만들면 됨.
    # 결국 answer_list는 추후 가중치와 곱하기 위함
    # 가중치는 4개의 답변이 하나의 질문에서 나와있어서 현재의 경우 4*20 = 총 80행이기 때문
    if method == 'total':
        for q in range(num_question):
            index_answer = q * num_answer + int(df.iloc[0, q])
            answer_list[index_answer] = 1
        answer_list = pd.DataFrame(data=answer_list)

    elif method == 'think':
        for q in range(num_question):
            if q % 5 == 0:
                index_answer = q * num_answer + int(df.iloc[0, q])
                answer_list[index_answer] = 1
        answer_list = pd.DataFrame(data=answer_list)
    return answer_list

def baumann_list_to_str(list):
    baumann_type = ''
    first_type = ['O', 'D']
    second_type = ['S','R']
    third_type = ['P','N']
    fourth_type = ['W','T']
    baumann_type_list = [first_type, second_type, third_type, fourth_type]
    for i in range(len(list)):
        baumann_type += baumann_type_list[i][list[i]]
    return baumann_type

def db_connection(db_filename):
    conn = sqlite3.connect(db_filename)
    conn.row_factory = sqlite3.Row    
    return conn

def calculate_baumann_survey(user_key):
    survey_output_filename = 'UserAnswer.db'
    survey_input_filename = './survey_question_to_db/qa_and_weight.db'

    output_db = db_connection(survey_output_filename)
    input_db = db_connection(survey_input_filename)

    # output_db > user_answer에서 user_key에 해당하는 답변 가져오기
    user_answer_df = pd.read_sql("SELECT * FROM user_answer", output_db, index_col=None)
    t_user_answer = user_answer_df[user_answer_df['user_key'] == user_key].iloc[:, 2:]
    t_user_answer_list = recon_answer_matrix(t_user_answer, 'total').transpose()

    # input_db > answer_weight에서 답변에 대한 가중치 가져오기
    answer_weight = pd.read_sql("SELECT * FROM answer_weight", input_db, index_col=None).iloc[:, 1:].fillna(0)
    user_baumann_output = t_user_answer_list.dot(answer_weight)

    # user_baumann_output 값 MBTI 형식으로 전환
    num_category = int(user_baumann_output.shape[1]/2)
    baumann_type_list = []
    for cat in range(num_category):
        if user_baumann_output.iloc[0, 2*cat] > user_baumann_output.iloc[0, 2*cat+1]:
            baumann_type_list.append(0)
        else:
            baumann_type_list.append(1)

    personal_baumann_type = baumann_list_to_str(baumann_type_list)
    
    # 스스로 생각하는 나의피부 타입 연산 (0, 5, 10, 15번째 질문이 해당사항)
    meta_user_answer_list = recon_answer_matrix(t_user_answer, 'think').transpose()
    meta_user_baumann_output = meta_user_answer_list.dot(answer_weight)
    num_category = int(meta_user_baumann_output.shape[1]/2)
    meta_baumann_type_list = []
    for cat in range(num_category):
        if meta_user_baumann_output.iloc[0, 2*cat] > meta_user_baumann_output.iloc[0, 2*cat+1]:
            meta_baumann_type_list.append(0)
        else:
            meta_baumann_type_list.append(1)
    meta_personal_baumann_type = baumann_list_to_str(meta_baumann_type_list)

    # output_db > user table의 baumann_type 컬럼 업데이트
    output_db.execute("UPDATE user SET baumann_type = ? WHERE user_key = ?", (personal_baumann_type, user_key))
    output_db.execute("UPDATE user SET meta_baumann_type = ? WHERE user_key = ?", (meta_personal_baumann_type, user_key))
    output_db.commit()
    output_db.close()
    input_db.close()


