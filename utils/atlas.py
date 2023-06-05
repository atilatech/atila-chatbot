from time import sleep
import requests

from utils.credentials import ATILA_CORE_SERVICE_URL
from pytube import YouTube
from pytube.exceptions import RegexMatchError

from utils.database import database
from utils.whatsapp import send_whatsapp_message, TWILIO_CHARACTER_LIMIT

invalid_link_message = "Invalid link. Please submit a valid youtube link."
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

search_help_text = f"Please send a search in the following format: search <youtube link> <search phrase>"

commands = ['help', 'email', 'search', 'contact']

MAX_FREE_SEARCHES = 3

subscription_link = "https://buy.stripe.com/9AQaI6fEh9SV63KeUU"


def can_transcribe_and_search_video(incoming_number):
    conversation_state = database['users'].find_one(
        {'phone': incoming_number, 'platform': 'whatsapp'})
    searches_count = conversation_state.get('atlas_searches', 0)
    is_premium = conversation_state.get('is_premium', False)

    if not is_premium and searches_count >= MAX_FREE_SEARCHES:
        send_whatsapp_message("You've reached the limit of free searches. "
                              f"Upgrade to get more searches:\n\n{subscription_link}",
                              incoming_number)
        return False

    return True


def transcribe_and_search_video(query="", url=None, summarize=True, incoming_number=None) -> dict | None:
    video = get_video_from_url(url)
    if not video:
        send_whatsapp_message(invalid_link_message, incoming_number)
        return None

    if not can_transcribe_and_search_video(incoming_number):
        return None

    send_whatsapp_message(f"Please wait. Getting transcript for: {video.title}", incoming_number,
                          media_url=video.thumbnail_url)

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
        if result.get('created'):
            # only count against the free limit if it's a new video
            database['users'].update_one(
                {'phone': incoming_number, 'platform': 'whatsapp'},
                {'$inc': {'atlas_searches': 1}})
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
    print('update_conversation_state', message)
    result = database['users'].update_one(
        {'phone': phone, 'platform': 'whatsapp'},
        {
            '$push': {
                'messages': {
                    '$each': [message],
                    '$slice': -MESSAGE_CONTEXT_WINDOW
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


def handle_search(search_term, url, incoming_number):
    results = transcribe_and_search_video(query=search_term, url=url, summarize=False,
                                          incoming_number=incoming_number)

    if not results:
        return

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
    result = transcribe_and_search_video(url=incoming_message, incoming_number=incoming_number)
    if not result:
        return
    elif 'error' in result:
        send_whatsapp_message(result['error'], incoming_number)
    else:
        video_text = result['video']['text']
        if 'summaries' in result['video']:
            video_text = "\n\n".join(summary['text'] for summary in result['video']['summaries'])

        title = f"*{result['video']['title']}*\n\n{result['video']['url']}"
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
    if command.startswith('search'):
        if len(incoming_message.split(' ')) >= 3:
            _, url, *search_term = incoming_message.split(' ')
            search_term = ' '.join(search_term)
            handle_search(search_term, url, incoming_number)
        elif len(conversation_state['messages']) > 1:
            send_whatsapp_message(f"Enter your search phrase", incoming_number)
        else:
            send_whatsapp_message(search_help_text, incoming_number)


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
    elif len(conversation_state['messages']) > 1 and \
            standardize_input(conversation_state['messages'][-2]).startswith('search'):
        search_term = conversation_state['messages'][-1]
        url = conversation_state['messages'][-3]
        handle_search(search_term, url, incoming_number)
    else:
        send_whatsapp_message(start_text, incoming_number)

    return 'ok'
