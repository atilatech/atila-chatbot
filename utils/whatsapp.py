from twilio.rest import Client

from utils.credentials import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WHATSAPP_NUMBER

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

TWILIO_CHARACTER_LIMIT = 1000  # Twilio has a 1600 character limit. https://www.twilio.com/docs/errors/21617


def send_whatsapp_message(text, destination_number: str, media_url: str = None):
    if not destination_number.startswith('whatsapp:'):
        destination_number = f'whatsapp:{destination_number}'

    destination_number = destination_number.replace(' ', '')
    message = client.messages.create(
        from_=f'whatsapp:{WHATSAPP_NUMBER}',
        body=text[:TWILIO_CHARACTER_LIMIT],
        media_url=media_url,
        to=f'{destination_number}'  # Add your WhatsApp No. here
    )
    print(message.sid)
