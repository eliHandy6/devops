import psycopg2
import time
from twilio.rest import Client

# Twilio account details
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
RECIPIENT_PHONE_NUMBER = "recipient_phone_number"

# PostgreSQL database details
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"

# Thresholds for resource utilization
CPU_THRESHOLD = 50  # Percentage
MEMORY_THRESHOLD = 80  # Percentage

def send_sms_alert(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=RECIPIENT_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def get_top_sessions():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pid, usename, query, state, now() - query_start AS duration,
                   cpu_usage, mem_usage
            FROM pg_stat_activity
            WHERE state = 'active'
            ORDER BY cpu_usage DESC, mem_usage DESC
            LIMIT 5;
        """)

        top_sessions = cursor.fetchall()
        cursor.close()
        conn.close()
        return top_sessions
    except psycopg2.Error as e:
        print("Error:", e)
        return []

def main():
    while True:
        top_sessions = get_top_sessions()
        if top_sessions:
            alert_message = "Top sessions based on resource utilization:\n"
            for session in top_sessions:
                alert_message += (
                    f"PID: {session[0]}, User: {session[1]}, Query: {session[2]}\n"
                    f"State: {session[3]}, Duration: {session[4]}, "
                    f"CPU Usage: {session[5]}%, Mem Usage: {session[6]}%\n\n"
                )
            send_sms_alert(alert_message)

        time.sleep(900)  # Sleep for 15 minutes

if __name__ == "__main__":
    main()
