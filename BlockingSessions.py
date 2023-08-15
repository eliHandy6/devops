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

def send_sms_alert(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=RECIPIENT_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def get_blocking_sessions():
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
            SELECT
                bl.pid AS blocked_pid,
                a.usename AS blocked_user,
                ka.query AS blocking_statement,
                now() - ka.query_start AS blocking_duration
            FROM
                pg_catalog.pg_locks bl
            JOIN
                pg_catalog.pg_stat_activity a ON bl.pid = a.pid
            JOIN
                pg_catalog.pg_locks kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid
            JOIN
                pg_catalog.pg_stat_activity ka ON kl.pid = ka.pid
            WHERE
                NOT bl.granted;
        """)

        blocking_sessions = cursor.fetchall()
        cursor.close()
        conn.close()
        return blocking_sessions
    except psycopg2.Error as e:
        print("Error:", e)
        return []

def main():
    while True:
        blocking_sessions = get_blocking_sessions()
        if blocking_sessions:
            alert_message = "Blocking sessions detected:\n"
            for session in blocking_sessions:
                alert_message += (
                    f"Blocked PID: {session[0]}, Blocked User: {session[1]}, "
                    f"Blocking Duration: {session[3]}, Blocking Statement: {session[2]}\n"
                )
            send_sms_alert(alert_message)

        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    main()
