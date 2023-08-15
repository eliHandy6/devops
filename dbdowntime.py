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

def check_database_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()
        return True
    except psycopg2.Error as e:
        return False

def main():
    while True:
        # Check database connection
        if not check_database_connection():
            send_sms_alert("Database connection failed!")

        # Add other monitoring checks here
        # Example: Check for slow queries, high CPU usage, etc.

        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    main()
