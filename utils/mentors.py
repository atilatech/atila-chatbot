from utils.credentials import ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY
from utils.whatsapp import send_whatsapp_message
from algoliasearch.search_client import SearchClient

algolia_client = SearchClient.create(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY)


def handle_mentors_search(incoming_message: str, incoming_number: str):
    word_1, word_2, *search_term = incoming_message.split(' ')
    results = search_mentors(search_term)
    # display results
    send_whatsapp_message(f"search results for '{incoming_message}'", incoming_number)


def search_mentors(search_term):
    # Connect and authenticate with your Algolia app

    # Create a new index and add a record
    index = algolia_client.init_index("prod_mentor_index")

    # Search the index and print the results
    results = index.search(search_term)
    print(results["hits"])
    return results["hits"]


search_mentors('healthcare')
