from time import sleep
from utils.credentials import ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY
from utils.whatsapp import send_whatsapp_message
from algoliasearch.search_client import SearchClient
from utils.global_state import get_is_searching, get_result_index, save_results

algolia_client = SearchClient.create(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY)
index = algolia_client.init_index("prod_mentor_index")

def handle_mentors_search(search_term: str, incoming_number: str):
    results = search_mentors(search_term)
    print(results)
    # display results
    for index, result in enumerate(results[:5]):
        send_whatsapp_message(f"{get_profile_message(result, index)}", incoming_number, media_url=result['profile_pic_url'])
    save_results(incoming_number, get_result_ids(results))
    sleep(5)
    send_whatsapp_message(f"Select a mentor by replying with their number", incoming_number)

def get_result_ids(results):
    return [result['objectID'] for result in results]

def handle_mentor_selection(selection_index, incoming_number, conversation_state):
    if not get_is_searching(incoming_number):
        send_whatsapp_message(f"Please search for a mentor first with: mentor search <terms>", incoming_number)
        return
    result_id = get_result_index(incoming_number, int(selection_index) - 1)
    result = search_mentors(result_id)[0]
    send_detailed_mentor_info(incoming_number, result)


def send_detailed_mentor_info(incoming_number, result):
    send_whatsapp_message(result['detailed_description'], incoming_number, media_url=result['profile_pic_url'])
    if get_bio_voice_recording(result):
        send_whatsapp_message(get_bio_voice_recording(result), incoming_number)
    send_whatsapp_message(get_payment_message(result), incoming_number)


def get_payment_message(profile):
    return f"Pay for a mentorship session with {profile['first_name']}:\n\n{get_payment_link(profile)}"


def get_payment_link(profile):
    #TODO: get this for real
    return 'https://buy.stripe.com/test_00g8QI4eQ0gY2QI7ss'


def search_mentors(search_term):
    # Connect and authenticate with your Algolia app

    # Search the index and print the results
    results = index.search(search_term)
    profiles = [get_profile(result) for result in results['hits']]

    return profiles

def get_profile(search_result):
    return {
        'objectID': search_result['objectID'],
        'first_name': search_result['user_json']['first_name'],
        'last_name': search_result['user_json']['last_name'],
        'profile_pic_url': search_result['user_json']['profile_pic_url'],
        'bio_recording_url': search_result['bio_recording_url'],
        'description': search_result['description'],
        'detailed_description': get_profile_detailed_description(search_result),
    }

def get_profile_detailed_description(search_result):
    if search_result['bio_text'] != "":
        return search_result['bio_text']
    return search_result['description']

def get_profile_message(profile, index):
    return f"{index + 1}. {profile['first_name']} {profile['last_name']}\n\n{profile['description']}"

def get_bio_voice_recording(profile):
    return profile['bio_recording_url']
