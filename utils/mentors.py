from utils.whatsapp import send_whatsapp_message


def handle_mentors_search(incoming_message: str, incoming_number: str):
    send_whatsapp_message(f"search results for '{incoming_message}'", incoming_number)
