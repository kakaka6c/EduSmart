from flask import Flask, jsonify, request,render_template,redirect,url_for
import sqlite3
from databaseHelper import *
import hashlib
import latex2mathjax

app = Flask(__name__)
DATABASE = 'EduSmart.db'

def execute_query(query, params=()):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(query, params)
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
        conn.close()
        return result
    except sqlite3.Error as e:
        print("Lỗi trong quá trình thực thi truy vấn:", e)
        return None

def encrypt_password(password): # Hàm mã hóa mật khẩu
    password = hashlib.md5(password.encode()).hexdigest()
    return password

@app.route('/users', methods=['GET'])
def get_users():
    query = "SELECT * FROM User"
    users = execute_query(query)
    if users:
        return jsonify(users)
    else:
        return jsonify([])

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')  # Cần mã hóa mật khẩu trước khi lưu vào cơ sở dữ liệu
    email = data.get('email')
    phone = data.get('phone')
    class_id = data.get('class_id')

    query = "INSERT INTO User (Username, PasswordHash, Email, Phone, ClassID) VALUES (?, ?, ?, ?, ?)"
    execute_query(query, (username, password, email, phone, class_id))
    return jsonify({"message": "User added successfully"})

# create a new route to create database
@app.route('/database', methods=['GET'])
def create_database():
    # use the DatabaseHelper class to create the database
    helper = CreateDatabase("EduSmart.db")
    helper.create_database()
    # create tables in the database
    helper.create_tables()
    return jsonify({"message": "Database created successfully"})

# create a new route to login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    username = username.lower()
    password = data.get('password')
    password = encrypt_password(password)
    query = "SELECT * FROM User WHERE Username = ? AND PasswordHash = ?"
    user = execute_query(query, (username, password))
    if user:
        return jsonify({"message": "True"})
    else:
        return jsonify({"message": "False"})

# create a new route to register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = str(data.get('username'))
    # change to lowercase
    username = username.lower()
    password = data.get('password')
    password = encrypt_password(password)
    email = data.get('email')
    phone = data.get('phone')
    class_id = data.get('class_id')
    dob = data.get('dob')

    query = "INSERT INTO User (Username, PasswordHash, Email, Phone, ClassID) VALUES (?, ?, ?, ?, ?)"
    
    status=execute_query(query, (username, password, email, phone, class_id))
    if status:
        return jsonify({"message": "User added successfully"})
    else:
        return jsonify({"message": "User already exists"})
    
# create a new route to add class
@app.route('/class', methods=['POST','GET'])
def class_db():
    if request.method == 'POST' and request.form.get('whoami') == 'admin':
        # get request post data
        class_name = request.form.get('class_name')
        query = "INSERT INTO Class (ClassName) VALUES (?)"
        execute_query(query, (class_name,))
        return render_template('add_info.html')
    elif request.method == 'POST' and request.form.get('whoami') != 'admin':
        return jsonify({"message": "You are not admin"})
    else:
        query = "SELECT * FROM Class"
        classes = execute_query(query)
        if classes:
            return jsonify(classes)
        else:
            return jsonify([])
# create docs for method
# create a new route to add topic
@app.route('/topic', methods=['POST','GET'])
def topic_db():
    if request.method == 'POST' and request.form.get('whoami') == 'admin':
        # get request post data
        topic_name = request.form.get('topic_name')
        chapter_id = request.form.get('chapter_id')
        query = "INSERT INTO Topic (TopicName, ChapterID) VALUES (?, ?)"
        class_id="SELECT ClassID FROM Chapter WHERE ChapterID = ?"
        class_id=execute_query(class_id,(chapter_id,))
        execute_query(query, (topic_name, chapter_id))
        return render_template('add_info.html',class_id=class_id[0][0],chapter_id=chapter_id,notify="Topic "+topic_name+" was add successfully")
    elif request.method == 'POST' and request.form.get('whoami') != 'admin':
        return jsonify({"message": "You are not admin"})
    else:
        chapter_id = request.args.get('chapter_id')
        query = "SELECT TopicID,TopicName FROM Topic WHERE ChapterID = ?"
        topics = execute_query(query, (chapter_id,))
        if topics:
            return jsonify(topics)
        else:
            return jsonify([])

# create a new route to add chapter
@app.route('/chapter', methods=['POST','GET']) # chapter_name and class_id are required
def chapter_db():
    if request.method == 'POST' and request.form.get('whoami') == 'admin':
        # get request post data
        chapter_name = request.form.get('chapter_name')
        class_id = request.form.get('class_id')
        query = "INSERT INTO Chapter (ChapterName, ClassID) VALUES (?, ?)"
        execute_query(query, (chapter_name,class_id))
        return render_template('add_info.html',class_id=class_id,notify="Chapter "+chapter_name+" was add successfully")
    elif request.method == 'POST' and request.form.get('whoami') != 'admin':
        return jsonify({"message": "You are not admin"})
    else:
        query = "SELECT ChapterID,ChapterName FROM Chapter WHERE ClassID = ?"
        class_id = request.args.get('class_id')
        chapters = execute_query(query, (class_id,))
        if chapters:
            return jsonify(chapters)
        else:
            return jsonify([])

# delete database and create new database
@app.route('/delete_db', methods=['GET'])
def delete_database():
    query = "DROP DATABASE EduSmart"
    execute_query(query)
    return jsonify({"message": "Database deleted successfully"})

# create a new route to show add_info template
@app.route('/add_info', methods=['GET'])
def add_info():
    return render_template('add_info.html',class_id=1)

# create a new route to add question and answer
@app.route('/question_manager', methods=['GET'])
def question_manager():
    classes=execute_query("SELECT * FROM Class")
    #  get all question and answer from database
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        topic_id = request.form.get('topic_id')
        chapter_id = request.form.get('chapter_id')
        query = "SELECT QuestionID, QuestionContent FROM Question WHERE ClassID = ? AND TopicID = ? AND ChapterID = ?"
        questions = execute_query(query, (class_id, topic_id, chapter_id))
        if questions:
            return jsonify(questions)
        else:
            return jsonify([])
        
        
        
    # return render_template('question_manager.html',classes=classes)

@app.route('/question', methods=['GET'])
def question_db():
    classes=execute_query("SELECT * FROM Class")
    return render_template('add_question.html',classes=classes)

@app.route('/add_question', methods=['POST'])
def add_question():
    # add question and answer to database
    data = request.form

    class_id = data.get('class_id')
    chapter_id = data.get('chapter_id')
    topic_id = data.get('topic_id')
    question=data.get('question')
    question = latex2mathjax.convert_latex_to_mathjax(question)
    answer = data.get('ans')
    answer = latex2mathjax.convert_latex_to_mathjax(answer)
    correct_answer = data.get('correct')
    explain = data.get('explaination')
    explain = latex2mathjax.convert_latex_to_mathjax(explain)
    query = "INSERT INTO Question (ClassID, TopicID, ChapterID, QuestionContent) VALUES (?, ?, ?, ?)"
    execute_query(query, (class_id, topic_id, chapter_id, question)) # add question to database
    question_id = execute_query("SELECT QuestionID FROM Question WHERE QuestionContent = ?",(question,))[0][0]
    query = "INSERT INTO Answers (QuestionID, AnswerOptions, CorrectAnswer, Explaination) VALUES (?, ?, ?, ?)"
    execute_query(query, (question_id, answer, correct_answer, explain)) # add answer to database
    return redirect("/question_manager")
    

if __name__ == '__main__':
    app.run(debug=True)
