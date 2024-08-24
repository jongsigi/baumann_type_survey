import os
from flask import Flask, session, render_template, request, redirect, url_for
from flask_cors import CORS
from config import Config
from models import db, User, UserAnswer
from calculate import calculate_baumann_survey
import uuid
import sqlite3

def db_connection(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(f"{path}/{db_filename}")
    conn.row_factory = sqlite3.Row    
    return conn

def initialize_app(app):
    # One-time setup code here
    print("Application initialized")
    with app.app_context():
        db.create_all()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

initialize_app(app)  # Moved the initialization here

@app.before_request
def before_request():
    if 'user_id' not in session:
        session.clear()

@app.route('/user_info', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        gender = request.form['gender']
        age_decade = request.form['age_decade']
        age_part = request.form['age_part']
        
        age_group = f"{age_decade}-{age_part}"
        user_key = str(uuid.uuid4())
        
        new_user = User(gender=gender, age_group=age_group, user_key=user_key)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['user_key'] = new_user.user_key
        session['current_question'] = 0
        session['answers'] = []
        
        return redirect(url_for('index'))
    
    return render_template('user_info.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('user_info'))

    if request.method == 'POST':
        selected_answer = request.form.get('answer')
        
        try:
            selected_answer = int(selected_answer)
        except ValueError:
            return 'Invalid answer format. Please try again.'

        session['answers'].append(selected_answer)
        session['current_question'] += 1

        if session['current_question'] >= 20:
            user_key = session['user_key']
            answer_data = {f'answer_{i}': session['answers'][i] for i in range(20)}
            new_answer = UserAnswer(user_key=user_key, **answer_data)
            db.session.add(new_answer)
            db.session.commit()

            # Store Baumann survey result
            baumann_percent = calculate_baumann_survey(user_key=user_key)
            session['baumann_percent'] = baumann_percent
            
            return redirect(url_for('survey_complete'))

    question_filename = './survey_question_to_db/qa_and_weight.db'
    conn = db_connection(question_filename)
    qa = conn.execute(
        'SELECT question, answer_0, answer_1, answer_2, answer_3 FROM question_and_answer LIMIT 1 OFFSET ?',
        (session['current_question'],)
    ).fetchone()
    conn.close()

    if qa is None:
        session['current_question'] = 0
        return render_template('user_info.html')

    return render_template('index.html', question=qa['question'], answers=[qa['answer_0'], qa['answer_1'], qa['answer_2'], qa['answer_3']], user_id=session['user_id'], question_count=session['current_question'])

@app.route('/survey_complete')
def survey_complete():
    user_key = session['user_key']
    baumann_percent = session['baumann_percent']
    
    user_filename = 'UserAnswer.db'
    conn = db_connection(user_filename)
    qa = conn.execute('SELECT baumann_type, meta_baumann_type FROM user WHERE user_key =?', (user_key, )).fetchone()
    conn.close()
    return render_template('survey_complete.html', baumann_type=qa['baumann_type'], meta_baumann_type=qa['meta_baumann_type'], baumann_percent=baumann_percent)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('user_info'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
