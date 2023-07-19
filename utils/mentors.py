from utils.whatsapp import send_whatsapp_message
import algoliasearch

def handle_mentors_search(search_term: str, incoming_number: str):

    send_whatsapp_message(f"search results for '{search_term}'", incoming_number)
