import asyncio

from flask import Flask, request

# from utils.atlas import handle_incoming_atlas_chat_message
from utils.credentials import WHATSAPP_NUMBER
import datetime

from utils.mentors import handle_mentors_search, handle_mentor_selection
from utils.mentorship_code import AtilaMentorship
from utils.whatsapp import send_whatsapp_message
from utils.global_state import set_searching

app = Flask(__name__)

one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
unix_timestamp_one_hour_ago = int(one_hour_ago.timestamp())


@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Welcome to Atila'


@app.route('/whatsapp', methods=['POST'])
async def whatsapp():
    print('/whatsapp')
    print('request.form', request.form)
    incoming_msg = request.form.get('Body').strip()
    incoming_number = request.form.get('WaId')
    first_name = request.form.get('ProfileName')
    command_string = incoming_msg.lower()
    if WHATSAPP_NUMBER in incoming_number:
        response = 'this number is from the bot'
        print(response)
        return response
    if command_string.startswith('mentor code generate'):
        response = AtilaMentorship.handle_command_generate_mentorship_code(command_string)
        send_whatsapp_message(response, incoming_number)
    else:
        send_whatsapp_message(f"invalid command", incoming_number)

    return 'ok'

    # return handle_incoming_atlas_chat_message(incoming_msg, incoming_number, first_name)


def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


async def run_flask_app():
    # Mac OSX Monterey (12.x) currently uses ports 5000 and 7000 for its Control centre hence the issue.
    # Try running your app from port other than 5000 and 7000
    # https://stackoverflow.com/a/72797062/5405197
    app.run(threaded=True, port=5001)


if __name__ == '__main__':
    # Run the Flask app asynchronously
    asyncio.run(run_flask_app())
