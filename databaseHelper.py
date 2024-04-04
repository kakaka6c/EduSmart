import sqlite3

class CreateDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        
    def create_database(self):
        try:
            conn = sqlite3.connect(self.db_name)
            print("Kết nối đến cơ sở dữ liệu thành công.")
            conn.close()
        except sqlite3.Error as e:
            print("Lỗi khi kết nối đến cơ sở dữ liệu:", e)

    def create_tables(self): # Hàm tạo bảng, Status của User có thể là 1 trong 3 giá trị: 'USER', 'VIP', 'ADMIN'
        create_table_queries = [
            '''CREATE TABLE IF NOT EXISTS Answers (
                AnswerID INTEGER PRIMARY KEY,
                QuestionID INTEGER,
                AnswerOptions TEXT,
                CorrectAnswer TEXT,
                Explanation TEXT,
                FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID)
            )''',
            '''CREATE TABLE IF NOT EXISTS Chapter (
                ChapterID INTEGER PRIMARY KEY,
                ChapterName TEXT UNIQUE,
                ClassID INTEGER,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID)
            )''',
            '''CREATE TABLE IF NOT EXISTS Class (
                ClassID INTEGER PRIMARY KEY,
                ClassName TEXT UNIQUE
            )''',
            '''CREATE TABLE IF NOT EXISTS Exam (
                ExamID INTEGER PRIMARY KEY,
                UserID INTEGER,
                Score REAL,
                TimeTaken INTEGER,
                StartTime DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (UserID) REFERENCES User(UserID)
            )''',
            '''CREATE TABLE IF NOT EXISTS Exam_Questions (
                ExamQuestionID INTEGER PRIMARY KEY,
                ExamID INTEGER,
                QuestionID INTEGER,
                QuestionOrder INTEGER,
                Score REAL,
                FOREIGN KEY (ExamID) REFERENCES Exam(ExamID),
                FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID)
            )''',
            '''CREATE TABLE IF NOT EXISTS ExamResult (
                ExamResultID INTEGER PRIMARY KEY,
                UserID INTEGER,
                ExamID INTEGER,
                CorrectAnswers INTEGER,
                IncorrectAnswers INTEGER,
                Score REAL,
                AnswerDetails TEXT,
                FOREIGN KEY (UserID) REFERENCES User(UserID),
                FOREIGN KEY (ExamID) REFERENCES Exam(ExamID)
            )''',
            '''CREATE TABLE IF NOT EXISTS Question (
                QuestionID INTEGER PRIMARY KEY,
                ClassID INTEGER,
                TopicID INTEGER,
                ChapterID INTEGER,
                QuestionContent TEXT,
                UsageCount INTEGER DEFAULT 0,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID),
                FOREIGN KEY (TopicID) REFERENCES Topic(TopicID),
                FOREIGN KEY (ChapterID) REFERENCES Chapter(ChapterID)
            )''',
            '''CREATE TABLE IF NOT EXISTS Topic (
                TopicID INTEGER PRIMARY KEY,
                TopicName TEXT UNIQUE,
                ChapterID INTEGER,
                FOREIGN KEY (ChapterID) REFERENCES Chapter(ChapterID)
            )''',
            '''CREATE TABLE IF NOT EXISTS User (
                UserID INTEGER PRIMARY KEY,
                Username VARCHAR(50) UNIQUE,
                PasswordHash VARCHAR(255),
                Email VARCHAR(100),
                Phone VARCHAR(20),
                ClassID INTEGER,
                DoB DATE,
                AverageScore REAL,
                Status VARCHAR(50),
                ExpiryDate DATE,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID),
            )''',
            '''CREATE TABLE AccessToken (
                UserID INTEGER PRIMARY KEY,
                access_token TEXT,
                expiry_token DATETIME,
                FOREIGN KEY (UserID) REFERENCES User(UserID)
            )'''
        ]

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            for query in create_table_queries:
                cursor.execute(query)
            conn.commit()
            print("Các bảng đã được tạo thành công.")
            conn.close()
        except sqlite3.Error as e:
            print("Lỗi khi tạo bảng:", e)

class DatabaseHelper:
    def __init__(self, db_name):
        self.db_name = db_name
        
    def get_user_by_email(self, email,password):
        # check if email and password are correct
        query = "SELECT * FROM User WHERE Email = ? AND PasswordHash = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            conn.close()
            return user
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
    
    def get_user_by_uid(self, user_id):
        query = "SELECT * FROM User WHERE UserID = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            conn.close()
            return user
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
    
    def get_all_questions(self):
        query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query)
            questions = cursor.fetchall()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
    
    def get_email(self,email):
        # search if this email is already in the database
        query = "SELECT * FROM User WHERE Email = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            conn.close()
            return True if user else False
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return False
    
    def add_token(self, user_id, email,access_token, expiry_time):
        # update the token for the user
        query = "UPDATE AccessToken SET email= ?, access_token = ?, expiry_token = ? WHERE UserID = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email, access_token, expiry_time, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm token:", e)
            return False
    
    def add_user(self, username, password, email, dob, status,token):
        add_user_to_User = "INSERT INTO User (Username, PasswordHash, Email, DoB, Status) VALUES (?, ?, ?, ?, ?)"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(add_user_to_User, (username, password, email, dob, status))
            add_token_to_Access_Token = "INSERT INTO AccessToken (UserID, access_token) VALUES (?, ?)"
            cursor.execute("SELECT UserID FROM User WHERE Email = ?", (email,))
            user_id = cursor.fetchone()[0]
            cursor.execute(add_token_to_Access_Token, (user_id, token))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm người dùng:", e)
            return False
    
    def update_user(self, user_id, email, username, password, dob):
        query = "UPDATE User SET Email = ?, Username = ?,"
        parameters = [email, username]

        # Kiểm tra xem người dùng có muốn thay đổi mật khẩu không
        if password is not None:
            query += " PasswordHash = ?,"
            parameters.append(password)

        query += " DoB = ? WHERE UserID = ?"
        parameters.extend([dob, user_id])
        # print(query, parameters)
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật thông tin người dùng:", e)
            return False

    
        
    
    def add_code(self, email, code, expired_at):
        query = "INSERT INTO PasswordReset (Email, Code, expired_at) VALUES (?, ?, ?)"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email, code, expired_at))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm mã code:", e)
            return False
    
    def revoke_token(self, token):
        query = "DELETE FROM AccessToken WHERE access_token = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (token,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thu hồi token:", e)
            return False
    
    def refresh_token(self, token):
        # delete the expired token
        query = "DELETE FROM AccessToken WHERE expiry_token < datetime('now')"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("Lỗi khi làm mới token:", e)
            return False

    def delete_code(self, email):
        query = "DELETE FROM PasswordReset WHERE Email = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa mã code:", e)
            return False

    def update_password(self, email, password):
        query = "UPDATE User SET PasswordHash = ? WHERE Email = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (password, email))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thay đổi mật khẩu:", e)
            return False

    def compare_code(self, email, code):
        query = "SELECT * FROM PasswordReset WHERE Email = ? AND Code = ? AND expired_at > datetime('now')"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email, code))
            result = cursor.fetchone()
            conn.close()
            return True if result else False
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return False

    def get_user_by_token(self, token):
        query = "SELECT u.UserID, u.Username, u.Email, u.DoB, u.Status FROM User u JOIN AccessToken a ON u.UserID = a.UserID WHERE a.access_token = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (token,))
            user = cursor.fetchone()
            conn.close()
            return user
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
    
    def get_token_by_user(self, email):
        query = "SELECT access_token FROM AccessToken WHERE UserID =? "
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            token = cursor.fetchone()
            conn.close()
            return token
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
        
    def load_questions_by_topic(self, topic_id):
        query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE q.TopicID = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (topic_id,))
            questions = cursor.fetchall()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
        
    def load_questions_by_chapter(self, chapter_id):
        query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE q.ChapterID = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (chapter_id,))
            questions = cursor.fetchall()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
    
    def load_questions_by_class(self, class_id):
        query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE q.ClassID = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (class_id,))
            questions = cursor.fetchall()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None
        
    def generate_questions(self,class_ids, topic_ids=None, chapter_ids=None, num_questions=1,token=None,user_id=None):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # Tạo danh sách các điều kiện WHERE cho class_id, topic_id và chapter_id
            conditions = []
            params = []
            if class_ids:
                conditions.append("q.ClassID IN ({})".format(','.join(['?']*len(class_ids))))
                params.extend(class_ids)
            if topic_ids:
                conditions.append("q.TopicID IN ({})".format(','.join(['?']*len(topic_ids))))
                params.extend(topic_ids)
            if chapter_ids:
                conditions.append("q.ChapterID IN ({})".format(','.join(['?']*len(chapter_ids))))
                params.extend(chapter_ids)
            where_clause = " AND ".join(conditions)
            # Thêm điều kiện WHERE vào câu truy vấn
            if not where_clause:
                query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID ORDER BY q.UsageCount DESC LIMIT ?"
                params.append(num_questions)
            else:
                query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE {} ORDER BY q.UsageCount DESC LIMIT ?".format(where_clause)
                params.append(num_questions)
            cursor.execute(query, params)
            questions = cursor.fetchall()
            for question in questions:
                cursor.execute("UPDATE Question SET UsageCount = UsageCount + 1 WHERE QuestionID = ?", (question[0],))
                # add question to exam_questions
                exam_id = self.create_an_exam(cursor,user_id)
                self.add_exam_question(cursor,exam_id, question[0], questions.index(question)+1, 1)
            conn.commit()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None

    def create_an_exam(self, cursor,user_id):
        query = "INSERT INTO Exam (UserID) VALUES (?)"
        try:
            cursor.execute(query, (user_id,))
            cursor.execute("SELECT last_insert_rowid()")
            exam_id = cursor.fetchone()[0]
            return exam_id
        except sqlite3.Error as e:
            print("Lỗi khi tạo bài thi:", e)
            return None
    
    def add_exam_question(self,cursor, exam_id, question_id, question_order, score):
        query = "INSERT INTO Exam_Questions (ExamID, QuestionID, QuestionOrder, Score) VALUES (?, ?, ?, ?)"
        try:
            cursor.execute(query, (exam_id, question_id, question_order, score))
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm câu hỏi vào bài thi:", e)
            return False