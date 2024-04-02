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
        
    def get_user_by_email(self, email):
        query = "SELECT UserID,status FROM User WHERE Email = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (email,))
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
    
    def add_token(self, user_id, access_token, expiry_token):
        query = "INSERT INTO AccessToken (UserID, access_token, expiry_token) VALUES (?, ?, ?)"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (user_id, access_token, expiry_token))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm token:", e)
            return False
    
    def add_user(self, username, password, email, dob, status):
        query = "INSERT INTO User (Username, PasswordHash, Email, DoB, Status) VALUES (?, ?, ?, ?, ?)"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (username, password, email, dob, status))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm người dùng:", e)
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
        
    def generate_questions(self, class_id, topic_id=None, chapter_id=None, num_questions=1):
        # if nothing None, return all questions and order by usage count
        if topic_id is None and chapter_id is None:
            query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE q.ClassID = ? ORDER BY q.UsageCount DESC LIMIT ?"
        elif topic_id is None:
            query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE q.ClassID = ? AND q.ChapterID = ? ORDER BY q.UsageCount DESC LIMIT ?"

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (class_id, topic_id, chapter_id, num_questions))
            questions = cursor.fetchall()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi truy vấn dữ liệu:", e)
            return None