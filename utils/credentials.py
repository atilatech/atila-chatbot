import os

BOT_TOKEN = os.getenv('BOT_TOKEN', False)

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', False)
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', False)
MONGODB_URL = os.getenv('MONGODB_URL', False)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', False)
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', False)
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', False)

# do the same for ALGOLIA_APPLICATION_ID and ALGOLIA_API_KEY
ALGOLIA_APPLICATION_ID = os.getenv('ALGOLIA_APPLICATION_ID', False)
ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY', False)

ATILA_CORE_SERVICE_URL = "http://127.0.0.1:8000/api"

# In staging and prod ATILA_CORE_SERVICE_URL and ATILA_API_URL will be different endpoints
ATILA_API_URL = os.getenv('ATILA_API_URL', False)
ATILA_API_KEY = os.getenv('ATILA_API_KEY', False)
