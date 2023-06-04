import os

BOT_TOKEN = os.getenv('BOT_TOKEN', False)

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', False)
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', False)
MONGODB_URL = os.getenv('MONGODB_URL', False)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', False)
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', False)
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', False)

ATILA_CORE_SERVICE_URL = "https://atila-core-service.herokuapp.com/api"
