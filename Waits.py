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

# List of wait event types to monitor
WAIT_EVENTS_TO_MONITOR = ["Lock", "IO"]

def send_sms_alert(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=RECIPIENT_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def get_waiting_sessions():
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
            SELECT pid, usename, wait_event_type, wait_event, now() - xact_start AS duration
            FROM pg_stat_activity
            WHERE state = 'active' AND wait_event IS NOT NULL
            ORDER BY duration DESC;
        """)

        waiting_sessions = cursor.fetchall()
        cursor.close()
        conn.close()
        return waiting_sessions
    except psycopg2.Error as e:
        print("Error:", e)
        return []

def main():
    while True:
        waiting_sessions = get_waiting_sessions()
        if waiting_sessions:
            alert_message = "Waiting sessions detected:\n"
            for session in waiting_sessions:
                if session[2] in WAIT_EVENTS_TO_MONITOR:
                    alert_message += (
                        f"PID: {session[0]}, User: {session[1]}, "
                        f"Wait Event Type: {session[2]}, Wait Event: {session[3]}\n"
                        f"Duration: {session[4]}\n\n"
                    )
            if alert_message != "Waiting sessions detected:\n":
                send_sms_alert(alert_message)

        time.sleep(900)  # Sleep for 15 minutes

if __name__ == "__main__":
    main()
