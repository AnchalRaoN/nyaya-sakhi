import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

msg = client.messages.create(
    body='Test message from Python directly',
    from_='whatsapp:' + os.getenv('TWILIO_WHATSAPP_NUMBER'),
    to='whatsapp:+918660762433'
)

print('SUCCESS:', msg.sid)