from time import sleep
from utils.credentials import ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY
from utils.whatsapp import send_whatsapp_message
from algoliasearch.search_client import SearchClient

algolia_client = SearchClient.create(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY)


def handle_mentors_search(search_term: str, incoming_number: str):
    results = search_mentors(search_term)
    # display results
    for index, result in enumerate(results[:5]):
        send_whatsapp_message(f"{get_profile_message(result, index)}", incoming_number, media_url=result['profile_pic_url'])
        # wait
        sleep(3)



def search_mentors(search_term):
    # Connect and authenticate with your Algolia app

    # Create a new index and add a record
    index = algolia_client.init_index("prod_mentor_index")

    # Search the index and print the results
    results = index.search(search_term)
    profiles = [get_profile(result) for result in results['hits']]

    print(profiles)
    return profiles

def get_profile(search_result):
    return {
        'first_name': search_result['user_json']['first_name'],
        'last_name': search_result['user_json']['last_name'],
        'profile_pic_url': search_result['user_json']['profile_pic_url'],
        'description': search_result['description'],
    }

def get_profile_message(profile, index):
    return f"{index + 1}. {profile['first_name']} {profile['last_name']}\n\n{profile['description']}"
