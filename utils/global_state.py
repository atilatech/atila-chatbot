BAD_BAD_NOT_GOOD_GLOBAL_STATE = {}

DEFAULT_STATE = {
    'state': 'start',
    'search_term': None,
    'results': []
}

def set_searching(incoming_number):
    if incoming_number not in BAD_BAD_NOT_GOOD_GLOBAL_STATE:
        BAD_BAD_NOT_GOOD_GLOBAL_STATE[incoming_number] = DEFAULT_STATE
    BAD_BAD_NOT_GOOD_GLOBAL_STATE[incoming_number]['state'] = 'searching'

def get_is_searching(incoming_number):
    if incoming_number not in BAD_BAD_NOT_GOOD_GLOBAL_STATE:
        return False
    return BAD_BAD_NOT_GOOD_GLOBAL_STATE[incoming_number]['state'] == 'searching'

def save_results(incoming_number, results):
    if incoming_number not in BAD_BAD_NOT_GOOD_GLOBAL_STATE:
        BAD_BAD_NOT_GOOD_GLOBAL_STATE[incoming_number] = DEFAULT_STATE
    BAD_BAD_NOT_GOOD_GLOBAL_STATE[incoming_number]['results'] = results

def get_result_index(incoming_number, index):
    return BAD_BAD_NOT_GOOD_GLOBAL_STATE[incoming_number]['results'][index]