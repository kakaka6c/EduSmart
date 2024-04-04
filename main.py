from flask import Flask, jsonify, request, render_template, redirect, url_for
import random
import json
import sqlite3
from databaseHelper import *
import hashlib
import latex2mathjax
from datetime import datetime, timedelta
from flask_cors import CORS
from token_manage import generate_token
import utils

app = Flask(__name__)
CORS(app)

DATABASE = "EduSmart.db"
DB_HELPER = DatabaseHelper(DATABASE)
DB_CREATE = CreateDatabase(DATABASE)


def execute_query(query, params=()):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
        conn.close()
        return result
    except sqlite3.Error as e:
        print("Lỗi trong quá trình thực thi truy vấn:", e)
        return None

def encrypt_password(password):  # Hàm mã hóa mật khẩu
    password = hashlib.md5(password.encode()).hexdigest()
    return password

def token_to_uid(authorization_header):
    user_id = None
    token = None
    print(authorization_header)
    if authorization_header and authorization_header.startswith('Bearer '):
        # Tách chuỗi token từ header 'Authorization'
        token = authorization_header.split(' ')[1]
        user_id = DB_HELPER.get_user_by_token(token)[0]
        return user_id,token
    else:
        return user_id,token

@app.route("/users", methods=["GET"])
def get_users():
    query = "SELECT * FROM User"
    users = execute_query(query)
    if users:
        return jsonify(users)
    else:
        return jsonify([])



@app.route("/get_info", methods=["GET"])
def get_info():
    # require token in headers
    authorization_header = request.headers.get('Authorization')
    user_id,token=token_to_uid(authorization_header)
    if user_id is None:
        return jsonify({"message": "Please login to use this feature!!!!"}), 401
    else:
        user_info = DB_HELPER.get_user_by_token(token)
        print(user_info)
        user_info = {"Name": user_info[1], "Email": user_info[2], "DoB": user_info[3], "Status": user_info[4]}
        return jsonify({"message": "Success", "user_info": user_info})

# create a new route to create database
@app.route("/database", methods=["GET"])
def create_database():
    # use the DatabaseHelper class to create the database
    helper = CreateDatabase("EduSmart.db")
    helper.create_database()
    # create tables in the database
    helper.create_tables()
    return jsonify({"message": "Database created successfully"})


# create a new route to login
@app.route("/login", methods=["POST"])
def login():
    request_data = request.json
    email = request_data["email"]
    email = email.lower()
    password = request_data["password"]
    password = encrypt_password(password)
    user = DB_HELPER.get_user_by_email(email,password)
    user_id = user[0] if user else None
    user_role = user[7] if user else None
    if user:
        access_token = generate_token()
        expiry_time = datetime.now() + timedelta(hours=24)
        status_add_token = DB_HELPER.add_token(user_id, email,access_token, expiry_time)
        if status_add_token:
            return jsonify(
                {"message": "Login Successfully", "access_token": access_token, "role": user_role}
            )
        else:
            return jsonify({"message": "Email or Password is incorrect !!!!", "access_token": "","role": ""}),401
    else:
        return jsonify({"message": "Email or Password is incorrect !!!!", "access_token": "","role": ""}),401


# create a new route to register
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = str(data.get("name"))
    password = data.get("password")
    password = encrypt_password(password)
    email = data.get("email")
    try:
        dob= data.get("dob")
    except:
        dob = None
    access_token = ""
    status = DB_HELPER.add_user(username, password, email, dob, "USER", access_token)
    if status:
        return jsonify({"message": True,"error": ""})
    else:
        return jsonify({"message": False,"error": "Email already exists"}),401

# create a new route to edit user
@app.route("/edit_user", methods=["POST"])
def edit_user():
    authorization_header = request.headers.get('Authorization')
    user_id, token = token_to_uid(authorization_header)
    print(user_id)
    old_password = None
    if user_id is None:
        return jsonify({"message": "Please login to use this feature!!!!"}), 401
    else:
        data = request.json
        username = str(data.get("name"))
        email = data.get("email")
        dob = data.get("dob")
        try:
            old_password = data.get("old_password")
        except:
            old_password = None

        try:
            password = data.get("new_password")
            if password:
                password = encrypt_password(password)
        except:
            password = None

        if old_password:
            old_password = encrypt_password(old_password)
            user = DB_HELPER.get_user_by_uid(user_id)
            print(user)
            if old_password != user[2]:
                return jsonify({"message": "Old password is not correct"}), 401
            
        status = DB_HELPER.update_user(user_id, email, username, password, dob)
        if status:
            return jsonify({"message": "Change information successfully"})
        else:
            return jsonify({"message": "Change information failed"}), 401


# create a new route to add class
@app.route("/class", methods=["POST", "GET"])
def class_db():
    if request.method == "POST" and request.form.get("whoami") == "admin":
        # get request post data
        class_name = request.form.get("class_name")
        query = "INSERT INTO Class (ClassName) VALUES (?)"
        execute_query(query, (class_name,))
        return render_template("add_info.html")
    elif request.method == "POST" and request.form.get("whoami") != "admin":
        return jsonify({"message": "You are not admin"})
    else:
        query = "SELECT * FROM Class"
        classes = execute_query(query)

        if classes:
            json_data = [{"id": item[0], "name": item[1]} for item in classes]
            return jsonify(json_data)
        else:
            return jsonify([])

# create docs for method
# create a new route to add topic
@app.route("/topic", methods=["POST", "GET"])
def topic_db():
    if request.method == "POST" and request.form.get("whoami") == "admin":
        # get request post data
        topic_name = request.form.get("topic_name")
        chapter_id = request.form.get("chapter_id")
        query = "INSERT INTO Topic (TopicName, ChapterID) VALUES (?, ?)"
        class_id = "SELECT ClassID FROM Chapter WHERE ChapterID = ?"
        class_id = execute_query(class_id, (chapter_id,))
        execute_query(query, (topic_name, chapter_id))
        return render_template(
            "add_info.html",
            class_id=class_id[0][0],
            chapter_id=chapter_id,
            notify="Topic " + topic_name + " was add successfully",
        )
    elif request.method == "POST" and request.form.get("whoami") != "admin":
        return jsonify({"message": "You are not admin"})
    else:
        chapter_id = request.args.get("chapter_id")
        query = "SELECT TopicID,TopicName FROM Topic WHERE ChapterID = ?"
        topics = execute_query(query, (chapter_id,))
        if topics:
            json_data = [{"id": item[0], "name": item[1]} for item in topics]
            return jsonify(json_data)
        else:
            return jsonify([])


# create a new route to add chapter
@app.route(
    "/chapter", methods=["POST", "GET"]
)  # chapter_name and class_id are required
def chapter_db():
    if request.method == "POST" and request.form.get("whoami") == "admin":
        # get request post data
        chapter_name = request.form.get("chapter_name")
        class_id = request.form.get("class_id")
        query = "INSERT INTO Chapter (ChapterName, ClassID) VALUES (?, ?)"
        execute_query(query, (chapter_name, class_id))
        return render_template(
            "add_info.html",
            class_id=class_id,
            notify="Chapter " + chapter_name + " was add successfully",
        )
    elif request.method == "POST" and request.form.get("whoami") != "admin":
        return jsonify({"message": "You are not admin"})
    else:
        query = "SELECT ChapterID,ChapterName FROM Chapter WHERE ClassID = ?"
        class_id = request.args.get("class_id")
        chapters = execute_query(query, (class_id,))
        if chapters:
            json_data = [{"id": item[0], "name": item[1]} for item in chapters]
            return jsonify(json_data)
        else:
            return jsonify([])


# delete database and create new database
@app.route("/delete_db", methods=["GET"])
def delete_database():
    query = "DROP DATABASE EduSmart"
    execute_query(query)
    return jsonify({"message": "Database deleted successfully"})

# create a new route to show add_info template
@app.route("/add_info", methods=["GET"])
def add_info():
    return render_template("add_info.html", class_id=1)

# create a new route to add question and answer
@app.route("/question_manager", methods=["GET"])
def question_manager():
    classes = execute_query("SELECT * FROM Class")
    classes = [{"id": item[0], "name": item[1]} for item in classes]

    questions = DB_HELPER.get_all_questions()
    if questions:
        json_data = [
            {
                "id": item[0],
                "question": item[1],
                "ans_id": item[2],
                "answer": json.loads(item[3]),
                "correct_ans": item[4],
                "explaination": item[5],
            }
            for item in questions
        ]
        # convert item[3] to json data
        return render_template(
            "question_manager.html", questions=json_data, classes=classes
        )
    else:
        return jsonify([])


@app.route("/question", methods=["GET"])
def question_db():
    classes = execute_query("SELECT * FROM Class")
    return render_template("add_question.html", classes=classes)


@app.route("/add_question", methods=["POST"])
def add_question():
    # add question and answer to database
    data = request.form
    class_id = data.get("class_id")
    chapter_id = data.get("chapter_id")
    topic_id = data.get("topic_id")
    question = data.get("question")
    question = latex2mathjax.convert_latex_to_mathjax(question)
    answer = data.get("ans")
    answer = latex2mathjax.convert_latex_to_mathjax(answer)
    correct_answer = data.get("correct")
    correct_answer = latex2mathjax.convert_latex_to_mathjax(correct_answer)
    explain = data.get("explaination")
    explain = latex2mathjax.convert_latex_to_mathjax(explain)
    query = "INSERT INTO Question (ClassID, TopicID, ChapterID, QuestionContent) VALUES (?, ?, ?, ?)"
    execute_query(
        query, (class_id, topic_id, chapter_id, question)
    )  # add question to database
    question_id = execute_query(
        "SELECT QuestionID FROM Question WHERE QuestionContent = ?", (question,)
    )[0][0]
    query = "INSERT INTO Answers (QuestionID, AnswerOptions, CorrectAnswer, Explaination) VALUES (?, ?, ?, ?)"
    execute_query(
        query, (question_id, answer, correct_answer, explain)
    )  # add answer to database
    return redirect("/question_manager")


# forgot password and send code to email
@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    email = request.json.get("email")
    is_exist = DB_HELPER.get_email(email)
    current_time = datetime.now()
    expired_at = current_time + timedelta(minutes=5)
    if is_exist:
        code = random.randint(10000000, 99999999)
        DB_HELPER.add_code(email, code, expired_at)
        utils.send_email(email, "Your code is " + str(code))
        return jsonify({"message": "Code has been sent to your email"})
    else:
        return jsonify({"message": "Email does not exist"})


# create a new route to change password,check code if same
@app.route("/change_password", methods=["POST"])
def change_password():
    email = request.json.get("email")
    code = request.json.get("code")
    new_password = request.json.get("new_password")
    is_exist = DB_HELPER.get_email(email)
    if is_exist:
        if DB_HELPER.compare_code(email, code):
            new_password = encrypt_password(new_password)
            DB_HELPER.update_password(email, new_password)
            DB_HELPER.delete_code(email)
            return jsonify({"message": "Password changed successfully"})
        else:
            return jsonify({"message": "Code is not correct"})
    else:
        return jsonify({"message": "Email does not exist"})


# create new route to delete old token
@app.route("/delete_token", methods=["POST"])
def delete_token():
    token = request.json.get("token")
    status = DB_HELPER.revoke_token(token)
    return jsonify({"message": status})

@app.route('/generate-questions', methods=['POST'])
def generate_questions_route():
    authorization_header = request.headers.get('Authorization')
    user_id,token=token_to_uid(authorization_header)
    if user_id is None:
        return jsonify({"message": "Please login to use this feature!!!!"}), 401
    else:
        try:
            data = request.json
            class_ids = data.get('class_ids', [])
            topic_ids = data.get('topic_ids', [])
            chapter_ids = data.get('chapter_ids', [])
            num_questions = data.get('num_questions', 1)
            if class_ids == [None] and topic_ids == [] and chapter_ids == []:
                return jsonify({"message": "Please select class !!!"}), 400
            # Gọi hàm generate_questions với các tham số từ request
            questions = DB_HELPER.generate_questions(class_ids, topic_ids, chapter_ids, num_questions,token,user_id)
            # create json response with questions
            if questions is not None:
                # return id,name,position
                json_data = {"question":[{"id": item[0], "name": item[1],"position":questions.index(item)} for item in questions]}
                
                return jsonify(json_data)
            else:
                return jsonify({"message": "Error creating question !!!"}), 500
        except Exception as e:
            return jsonify({"message": "An unknown error: {}".format(e)}), 500


if __name__ == "__main__":    app.run(debug=True, host="0.0.0.0", port=5000)
