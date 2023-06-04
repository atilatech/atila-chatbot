from time import sleep

from utils.credentials import ATILA_CORE_SERVICE_URL
from pytube import YouTube
from pytube.exceptions import RegexMatchError

from utils.whatsapp import send_whatsapp_message, TWILIO_CHARACTER_LIMIT

instructions = """
1. Type 'email' to get the transcript sent to your email
2. Type 'search' to find something within the email
3. Type another video link to transcribe another video 
"""


def transcribe_video(url):
    import requests

    endpoint_url = f"{ATILA_CORE_SERVICE_URL}/atlas/search"

    payload = {
        "q": "",
        "url": url,
        "summarize": True
    }

    response = requests.post(endpoint_url, json=payload)

    try:
        response.raise_for_status()
        result = response.json()
        print(result)
        return result
    except requests.HTTPError as err:
        error_message = response.text
        print(f"HTTP Error occurred: {err}\nError message: {error_message}")
        return {'error': error_message}
    except requests.RequestException as err:
        print(f"An error occurred: {err}")
        return {'error': err}


def is_valid_video(url):
    try:
        YouTube(url)
        return True
    except RegexMatchError:
        return False


def handle_incoming_atlas_chat_message(incoming_message, incoming_number):
    if incoming_message.startswith('http'):
        if not is_valid_video(incoming_message):
            send_whatsapp_message('Invalid link. Please submit a valid youtube link', incoming_number)
        else:
            result = transcribe_video(incoming_message)
            if 'error' in result:
                send_whatsapp_message(result['error'], incoming_number)
            else:
                video_text = result['video']['text']
                if 'summaries' in result['video']:
                    video_text = "\n\n".join(summary['text'] for summary in result['video']['summaries'])

                title = f"*{result['video']['title']}*\n\n"
                send_whatsapp_message(title + video_text, incoming_number,
                                      media_url=result['video']['image'])
                if len(video_text) > TWILIO_CHARACTER_LIMIT:
                    send_whatsapp_message("1. Reply 'email'"
                                          "to get the full transcript sent to your email.",
                                          incoming_number)

                send_whatsapp_message("Reply 'search' to find a keyword within the video",
                                      incoming_number)

    return 'ok'
