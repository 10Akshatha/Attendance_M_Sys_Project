import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from tabulate import tabulate  # for pretty table output
import datetime

def view_attendance():
    # Connect to DB
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)

    print("\n--- Attendance Viewer ---")
    print("1. View all attendance")
    print("2. View attendance by date")
    print("3. View attendance by date and period")
    choice = input("\nEnter your choice (1-3): ")

    if choice == "1":
        cursor.execute("SELECT * FROM attendance ORDER BY date DESC, period ASC")
    elif choice == "2":
        date_input = input("Enter date (YYYY-MM-DD): ")
        cursor.execute("SELECT * FROM attendance WHERE date=%s ORDER BY period ASC", (date_input,))
    elif choice == "3":
        date_input = input("Enter date (YYYY-MM-DD): ")
        period_input = input("Enter period number: ")
        cursor.execute("SELECT * FROM attendance WHERE date=%s AND period=%s", (date_input, period_input))
    else:
        print("Invalid choice.")
        cursor.close()
        conn.close()
        return

    rows = cursor.fetchall()

    if not rows:
        print("\n[INFO] No records found for the selected filter.")
    else:
        table = []
        for row in rows:
            table.append([
                row["id"],
                row["student_id"],
                row["date"].strftime("%Y-%m-%d") if isinstance(row["date"], datetime.date) else row["date"],
                row.get("period", "-"),
                row["status"]
            ])
        print("\n" + tabulate(table, headers=["ID", "USN", "Date", "Period", "Status"], tablefmt="grid"))

    cursor.close()
    conn.close()

if __name__ == "__main__":
    view_attendance()

