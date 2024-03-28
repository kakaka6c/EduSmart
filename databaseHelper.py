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
                SessionID VARCHAR(255),
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID),
                CHECK (DoB < CURRENT_DATE),
                CHECK (Email LIKE '%@%.%'),
                CHECK (Phone LIKE '[0-9]%')
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
        
    def get_user_by_username(self, username):
        query = "SELECT * FROM User WHERE Username = ?"
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, (username,))
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
        
    
    
if __name__ == "__main__":
    helper = CreateDatabase("EduSmart.db")
    helper.create_database()
    helper.create_tables()
