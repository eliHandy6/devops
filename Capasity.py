import psutil
import time
from twilio.rest import Client

# Twilio account details
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
RECIPIENT_PHONE_NUMBER = "recipient_phone_number"

# Thresholds for capacity usage (in percentage)
MEMORY_THRESHOLD = 70
CPU_THRESHOLD = 70
DISK_THRESHOLD = 70

def send_sms_alert(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=RECIPIENT_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def main():
    while True:
        # Check memory usage
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > MEMORY_THRESHOLD:
            send_sms_alert(f"Memory usage exceeded {MEMORY_THRESHOLD}%: {memory_usage}%")

        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > CPU_THRESHOLD:
            send_sms_alert(f"CPU usage exceeded {CPU_THRESHOLD}%: {cpu_usage}%")

        # Check disk usage (root partition)
        disk_usage = psutil.disk_usage('/').percent
        if disk_usage > DISK_THRESHOLD:
            send_sms_alert(f"Disk usage exceeded {DISK_THRESHOLD}%: {disk_usage}%")

        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    main()
