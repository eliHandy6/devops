import psycopg2
import time
from twilio.rest import Client

# Twilio account details
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
RECIPIENT_PHONE_NUMBER = "recipient_phone_number"

# Primary PostgreSQL database details
PRIMARY_DB_HOST = "primary_db_host"
PRIMARY_DB_PORT = "5432"
PRIMARY_DB_NAME = "primary_db_name"
PRIMARY_DB_USER = "primary_db_user"
PRIMARY_DB_PASSWORD = "primary_db_password"

# Standby (DR) PostgreSQL database details
STANDBY_DB_HOST = "standby_db_host"
STANDBY_DB_PORT = "5432"
STANDBY_DB_NAME = "standby_db_name"
STANDBY_DB_USER = "standby_db_user"
STANDBY_DB_PASSWORD = "standby_db_password"

# Synchronization level threshold
SYNC_LEVEL_THRESHOLD = 10  # Allowed difference in bytes

def send_sms_alert(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=RECIPIENT_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def get_sync_level():
    try:
        primary_conn = psycopg2.connect(
            host=PRIMARY_DB_HOST,
            port=PRIMARY_DB_PORT,
            database=PRIMARY_DB_NAME,
            user=PRIMARY_DB_USER,
            password=PRIMARY_DB_PASSWORD
        )

        standby_conn = psycopg2.connect(
            host=STANDBY_DB_HOST,
            port=STANDBY_DB_PORT,
            database=STANDBY_DB_NAME,
            user=STANDBY_DB_USER,
            password=STANDBY_DB_PASSWORD
        )

        primary_cursor = primary_conn.cursor()
        standby_cursor = standby_conn.cursor()

        primary_cursor.execute("SELECT pg_current_xlog_location()")
        standby_cursor.execute("SELECT pg_last_xlog_receive_location()")

        primary_location = primary_cursor.fetchone()[0]
        standby_location = standby_cursor.fetchone()[0]

        primary_cursor.close()
        standby_cursor.close()
        primary_conn.close()
        standby_conn.close()

        return abs(int(primary_location, 16) - int(standby_location, 16))
    except psycopg2.Error as e:
        print("Error:", e)
        return None

def main():
    while True:
        sync_level = get_sync_level()
        if sync_level is not None and sync_level > SYNC_LEVEL_THRESHOLD:
            send_sms_alert(f"Synchronization level deviation detected: {sync_level} bytes")

        time.sleep(3600)  # Sleep for 1 hour

if __name__ == "__main__":
    main()
