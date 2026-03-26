import smtplib
from email.mime.text import MIMEText
from db_utils import get_db_connection
import datetime

EMAIL_ADDRESS = "harshithakv2529@gmail.com"
EMAIL_PASSWORD = "gmdv dncg igkm qygx"

def get_absent_periods(today, upto_period=None):
    """
    Fetch absent periods. If upto_period is given, only return absences till that period.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if upto_period:
        cursor.execute("""
            SELECT s.name, s.email, a.period 
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            WHERE a.date=%s AND a.status='A' AND a.period <= %s
            ORDER BY s.name
        """, (today, upto_period))
    else:
        cursor.execute("""
            SELECT s.name, s.email, a.period 
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            WHERE a.date=%s AND a.status='A'
            ORDER BY s.name
        """, (today,))
    
    data = cursor.fetchall()
    conn.close()
    return data


def send_email(subject, body, recipient):
    """Send email to recipient."""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient

    server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
    server.quit()


def send_midday_alert():
    """Send mail after 2 periods."""
    today = datetime.date.today()
    absentees = get_absent_periods(today, upto_period=2)

    if not absentees:
        print("[INFO] No absentees in first 2 periods.")
        return

    students = {}
    for row in absentees:
        students.setdefault((row["name"], row["email"]), []).append(str(row["period"]))

    for (name, email), periods in students.items():
        body = (
            f"Dear Parent,\n\n"
            f"This is a mid-day alert. Your child {name} was absent in periods: {', '.join(periods)}.\n\n"
            f"Please ensure their attendance for upcoming classes.\n\n"
            f"Regards,\nAttendance System"
        )
        send_email("Mid-day Attendance Alert", body, email)
        print(f"[INFO] Mid-day alert sent to {email}")


def send_endday_summary():
    """Send mail at end of the day."""
    today = datetime.date.today()
    absentees = get_absent_periods(today)

    if not absentees:
        print("[INFO] All students present today.")
        return

    students = {}
    for row in absentees:
        students.setdefault((row["name"], row["email"]), []).append(str(row["period"]))

    for (name, email), periods in students.items():
        body = (
            f"Dear Parent,\n\n"
            f"Attendance summary for today ({today}):\n"
            f"{name} was absent in periods: {', '.join(periods)}.\n\n"
            f"Regards,\nAttendance System"
        )
        send_email("End of Day Attendance Summary", body, email)
        print(f"[INFO] End-of-day summary sent to {email}")


if __name__ == "__main__":
    # Run one of these depending on the time of the day
    # For mid-day alert (after 2 periods):
    # send_midday_alert()
    
    # For end-of-day summary (after last period):
    send_endday_summary()
