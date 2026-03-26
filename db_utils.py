import mysql.connector

# Database Config
DB_HOST = "localhost"
DB_USER = ""
DB_PASSWORD = ""
DB_NAME = ""

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        img_path TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20),
        date DATE,
        status ENUM('P','A'),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("[INFO] Database and tables ready.")
