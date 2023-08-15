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

# Threshold for query execution time (in seconds)
LONG_QUERY_THRESHOLD = 10

def send_sms_alert(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=RECIPIENT_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def get_long_running_queries():
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
            SELECT pid, query, state, now() - query_start AS duration
            FROM pg_stat_activity
            WHERE state = 'active' AND now() - query_start > interval '%s seconds'
            ORDER BY duration DESC;
        """, (LONG_QUERY_THRESHOLD,))

        long_queries = cursor.fetchall()
        cursor.close()
        conn.close()
        return long_queries
    except psycopg2.Error as e:
        print("Error:", e)
        return []

def main():
    while True:
        long_queries = get_long_running_queries()
        if long_queries:
            alert_message = "Long running queries:\n"
            for query in long_queries:
                alert_message += f"PID: {query[0]}, Duration: {query[3]}, Query: {query[1]}\n"
            send_sms_alert(alert_message)

        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    main()
