from http.client import HTTPException

import requests

from utils.credentials import ATILA_API_KEY, ATILA_API_URL


class AtilaMentorship:
    mentorship_url = f"{ATILA_API_URL}/mentorship"
    mentorship_code_url = f"{mentorship_url}/codes/"

    @staticmethod
    def handle_command_generate_mentorship_code(command_string):

        parts = command_string.split()

        # Extract the count part if it exists
        if len(parts) == 4:
            count_str = parts[3]
            # Convert count to integer, default to 1 if empty
            count = int(count_str) if count_str.isdigit() else 1
        else:
            # Default to 1 if the format is incorrect
            count = 1
        codes = AtilaMentorship.generate_mentorship_code(count)

        codes_list = codes.get('codes', [])
        codes_string = "\n".join(code['code'] for code in codes_list)
        return codes_string

    @staticmethod
    def generate_mentorship_code(count=1):
        """
        Save a new scholarship to the database.
        """

        headers = {
            'Authorization': 'Token {}'.format(ATILA_API_KEY)
        }
        response = requests.post(AtilaMentorship.mentorship_code_url, json={"count": count}, headers=headers)

        print(f"\nresponse.status_code: {response.status_code}")
        if 200 <= response.status_code < 300:
            print(f"\nSuccessfully created codes")
        else:
            print(f"Error saving scholarship: {response.json()}")
            raise HTTPException(response.json())
        return response.json()
