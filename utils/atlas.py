from time import sleep

from utils.credentials import ATILA_CORE_SERVICE_URL
from pytube import YouTube
from pytube.exceptions import RegexMatchError

from utils.database import database
from utils.whatsapp import send_whatsapp_message, TWILIO_CHARACTER_LIMIT

invalid_message = "Invalid link. Please submit a valid youtube link."
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

commands = ['help', 'email', 'search', 'contact']


def transcribe_and_search_video(query="", url=None, summarize=True) -> dict:
    import requests

    endpoint_url = f"{ATILA_CORE_SERVICE_URL}/atlas/search"

    payload = {
        "q": query,
        "url": url,
        "summarize": summarize
    }

    response = requests.post(endpoint_url, json=payload)

    try:
        response.raise_for_status()
        result = response.json()
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


MESSAGE_CONTEXT_WINDOW = 5


def update_conversation_state(message: str, phone: str, first_name: str):
    # store last N messages
    # https://www.mongodb.com/docs/manual/reference/operator/update/slice/#slice-from-the-end-of-the-array
    result = database['users'].update_one(
        {'phone': phone, 'platform': 'whatsapp'},
        {
            '$push': {
                'messages': {
                    '$each': [message],
                    '$slice': MESSAGE_CONTEXT_WINDOW
                }
            },
            '$set': {'first_name': first_name}
        },
        upsert=True
    )

    return database['users'].find_one(result.upserted_id)


def seconds_to_minutes_and_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    minutes_and_seconds = f"{int(minutes)}:{int(remaining_seconds):02}"
    print(minutes_and_seconds)
    return minutes_and_seconds


def handle_search(incoming_message, incoming_number):
    if len(incoming_message.split(' ')) == 3:
        _, url, search_term = incoming_message.split(' ')
    else:
        send_whatsapp_message('enter a search term', incoming_number)
        return

    results = transcribe_and_search_video(query=search_term, url=url, summarize=False)

    title = results['video']['title']
    if len(results['results']['matches']) > 0:
        title = f"Search results for '{search_term}' in {title}"
        send_whatsapp_message(title, incoming_number)
        for result in results['results']['matches'][:5]:
            formatted_start_time = seconds_to_minutes_and_seconds(result['metadata']['start'])

            send_whatsapp_message(f"{formatted_start_time}: {result['metadata']['url']}\n\n"
                                  f"{result['metadata']['text']}", incoming_number)
    else:
        send_whatsapp_message(f"No matching search terms for '{search_term}' in {title}",
                              incoming_number)


def handle_transcribe_link(incoming_message, incoming_number):
    video = get_video_from_url(incoming_message)
    if not video:
        send_whatsapp_message(invalid_message, incoming_number)
    else:
        send_whatsapp_message(f"Please wait. Getting transcript for: {video.title}", incoming_number,
                              media_url=video.thumbnail_url)
        result = transcribe_and_search_video(url=incoming_message)
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


def handle_command(incoming_message, incoming_number, conversation_state):
    command = standardize_input(incoming_message)
    if command.startswith('help'):
        send_whatsapp_message(help_paragraph, incoming_number)
        return
    print('incoming_message.split(' ')', incoming_message.split(' '))
    if command.startswith('search'):
        handle_search(incoming_message, incoming_number)


def standardize_input(incoming_message):
    """
    Users may send text with uppercase, additional spaces etc.
    standardize the input for easier processing.
    Note: Don't do this globally e.g. YouTube URLs are case-sensitive
    :param incoming_message:
    :return:
    """
    return incoming_message.lower().strip()


def handle_incoming_atlas_chat_message(incoming_message: str, incoming_number: str, first_name: str):
    conversation_state = update_conversation_state(incoming_message, incoming_number, first_name)

    if any(standardize_input(incoming_message).startswith(command) for command in commands):
        handle_command(incoming_message, incoming_number, conversation_state)
    elif incoming_message.startswith('http'):
        handle_transcribe_link(incoming_message, incoming_number)
    else:
        send_whatsapp_message(start_text, incoming_number)

    return 'ok'
