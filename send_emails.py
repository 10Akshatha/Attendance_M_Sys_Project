import smtplib
from email.mime.text import MIMEText
from db_utils import get_db_connection
import datetime

# ---------- EMAIL CONFIG ----------
EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""

# ---------- EMAIL UTILITY FUNCTION ----------
def send_email(to, subject, body):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to

        server.sendmail(EMAIL_ADDRESS, to, msg.as_string())
        server.quit()
        print(f"[INFO] Email sent to {to}")

    except Exception as e:
        print(f"[ERROR] Could not send email to {to}: {e}")

# ---------- FUNCTION: FIRST ALERT ----------
def send_first_alert():
    """Sends alert after 2 periods for absentees."""
    today = datetime.date.today()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name, s.email, a.period
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        WHERE a.date = %s AND a.period IN (1, 2) AND a.status = 'A'
    """, (today,))
    absentees = cursor.fetchall()
    conn.close()

    if not absentees:
        print("[INFO] No absentees in Period 1 or 2.")
        return

    for student in absentees:
        body = (
            f"Dear Parent,\n\n"
            f"Your child {student['name']} was absent in Period {student['period']} today ({today}).\n"
            f"Please ensure attendance in upcoming classes.\n\n"
            f"Regards,\nAttendance System"
        )
        send_email(student["email"], "Attendance Alert (Morning)", body)

# ---------- FUNCTION: FINAL SUMMARY ----------
def send_final_summary():
    """Sends final summary at end of the day."""
    today = datetime.date.today()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name, s.email, GROUP_CONCAT(a.period ORDER BY a.period) AS absent_periods
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        WHERE a.date = %s AND a.status = 'A'
        GROUP BY s.student_id
    """, (today,))
    absentees = cursor.fetchall()
    conn.close()

    if not absentees:
        print("[INFO] No absentees today.")
        return

    for student in absentees:
        body = (
            f"Dear Parent,\n\n"
            f"Your child {student['name']} was absent in Period(s): {student['absent_periods']} on {today}.\n\n"
            f"Regards,\nAttendance System"
        )
        send_email(student["email"], "Daily Attendance Summary", body)

# ---------- AUTOMATIC LOGIC ----------
if __name__ == "__main__":
    current_hour = datetime.datetime.now().hour

    # Example: assume school starts at 9 AM
    # After 2 periods (~11 AM), send alert
    # After 4 PM, send summary
    if 8 <= current_hour < 10:
        print("[INFO] Sending first alert (after 2 periods)...")
        send_first_alert()
    elif current_hour >= 12:
        print("[INFO] Sending final summary (end of day)...")
        send_final_summary()
    else:
        print("[INFO] Not the scheduled time for sending emails.")
