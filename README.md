# Usluge

Usluge is a service for finding service providers.

Usluge means service in Montenegrin.

Try it at http://usluge.io/

## Quickstart

This project was created using [Python Telegram Bot: Your first Bot tutorial](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot).
and [Building a WhatsApp bot on Python](https://www.geeksforgeeks.org/building-whatsapp-bot-on-python/)

See:
1. https://t.me/atilatechbot
2. https://wa.me/18078085377

`python -m venv botenv/`

`source botenv/bin/activate`

`pip install -r requirements.txt`

### Whatsapp Quickstart

`source .env; python app.py` or `flask run --debug`
`--debug` enables hot reload

`brew install ngrok/ngrok/ngrok`
`ngrok http 5000`

The WhatsApp chatbot can only send you messages if you have messaged it in the last 24 hours.
So make sure you've sent a message to the chatbot using the wa.me link provided earlier.

```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=heyman&WaId=<your_phone_number>&ProfileName=Tomiwa[CURL]" \
  http://127.0.0.1:5001/whatsapp

```


```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=mentor search healthcare&WaId=19058758867&ProfileName=Tomiwa[CURL]" \
  http://127.0.0.1:5001/whatsapp
```

## Embed the Data
`python bot_helpers/embed.py`

`source .env; python bot.py`

## Deployment

## Telegram Chatbot

This project exists as a bot on a `vps`, run it by `ssh` into the repo

`ssh -i /Users/tomiwa/.ssh/id_rsa_digitalocean root@167.172.106.44 ; cd usluge ; python bot.py`

### Copy local files to Server

If file is only on local machine:
`scp -i /Users/tomiwa/.ssh/id_rsa_digitalocean /Users/tomiwa/Desktop/tomiwa/code/atila/atila-chatbot/.env root@167.172.106.44:/root/atila-chatbot`

`scp -i /Users/tomiwa/.ssh/id_rsa_digitalocean /Users/tomiwa/Desktop/tomiwa/code/usluge/utils/taxi.py root@167.172.106.44:/root/usluge`

### Starting and Stopping Server

1. "Close your process (ctrl + c)": The process currently running in the terminal needs to be stopped. This is done by pressing 'ctrl + c' in the terminal window.
2. "Write 'screen'": This is the command to start a new screen session. You simply type 'screen' into the terminal and press 'Enter'
3. "Press enter until you basically get the terminal back": When you start a new screen session, you might see some introductory information. Press 'Enter' to clear this and get back to the command prompt
4. "Then run the process": Now you should start your Python process again within this new screen session
5. "Then Ctrl + a": This is the command used in Screen to indicate that you're about to enter a command for Screen itself, rather than the process running within Screen
6. "And then D": After 'ctrl + a', pressing 'D' tells Screen to detach the current session. This means that the session will keep running, but you're no longer actively viewing it in your terminal. This is how you can keep the Python process running even after closing the terminal window
7. In the future, you can reattach to this session by typing screen -r in the terminal, which will allow you to interact with your Python process again.
ps aux | grep python

`kill 1234`

## Whatsapp Bot

The chatbot also exists as a whatsapp chatbot.

## Data Modelling

conversation_state
- phone
- platform
- app
- command
- input_message