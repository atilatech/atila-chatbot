from time import sleep

from utils.credentials import ATILA_CORE_SERVICE_URL
from pytube import YouTube
from pytube.exceptions import RegexMatchError

from utils.whatsapp import send_whatsapp_message, TWILIO_CHARACTER_LIMIT

youtube_instructions = "Submit a link to a Youtube video, channel or playlist."
help_text = "Type 'help' to see more detailed instructions and examples."
start_text = f"""
This chatbot helps transcribe Youtube videos.\n
To start: {youtube_instructions}\n
{help_text}
"""

help_paragraph = f"""
1. {youtube_instructions}\n
2. Type 'email' to get the transcript sent to your email\n
3. Type 'search' to search within the video for a phrase\n
4. Type 'contact' to message the Atila team
{help_text}\n 
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


def get_video_from_url(url):
    try:
        video = YouTube(url)
        return video
    except RegexMatchError:
        return False


def handle_incoming_atlas_chat_message(incoming_message, incoming_number):
    invalid_message = "Invalid link. Please submit a valid youtube link."
    if invalid_message.lower().strip() == 'help':
        send_whatsapp_message(help_paragraph, incoming_number)
    if incoming_message.startswith('http'):
        video = get_video_from_url(incoming_message)
        if not video:
            send_whatsapp_message(invalid_message, incoming_number)
        else:
            send_whatsapp_message(f"Please wait. Getting transcript for: {video.title}", incoming_number,
                                  media_url=video.thumbnail_url)
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

                sleep(3)
                if len(video_text) > TWILIO_CHARACTER_LIMIT:
                    send_whatsapp_message("1. Reply 'email'"
                                          "to get the full transcript sent to your email.",
                                          incoming_number)

                send_whatsapp_message("Reply 'search' to find a keyword within the video",
                                      incoming_number)
    else:
        send_whatsapp_message(start_text, incoming_number)

    return 'ok'
