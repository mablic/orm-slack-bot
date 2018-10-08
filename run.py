import os
import time
import re
from googlesearch import search
from slackclient import SlackClient
from Model import Users
from datetime import datetime
import json


slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
DELAY = 1  # 1 second delay
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


with open('name_convert.json') as f:
    ID_Dict = json.load(f)


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel, user, bot):
    """
        Executes bot command if the command is known
    """
    # Regex match for google search
    bot_response = re.match(r".*?\W*(google)\s+\b(.*)", command.lower())
    bot_user = parse_direct_mention(command)[0]
    # This is where you start to implement more commands!
    query = ""
    if bot_user != bot:
        if bot_response:
            query = bot_response.group(2)
            tmp = [i for i in search(query, tld="co.in", num=10, stop=1, pause=2)]
            try:
                response = tmp[0]
            # Exception for index out of range
            except IndexError:
                response = "No Search"
        else:
            return

        # Add search into db
        print(user, bot)
        user_name = ID_Dict.get(user, 'None')
        Users.insert(user_name, query, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    else:
        read_all = re.match(r".*?\W*(findall)", command.lower())
        read_by_name = re.match(r".*?\W*(where)\s+\b(.*)\s+\b(.*)", command.lower())
        if read_all:
            response = Users.select('', '')
            response = str(response)
        elif read_by_name:
            try:
                query1 = read_by_name.group(2)
                query2 = read_by_name.group(3)
                response = Users.select(query1, query2)
                response = str(response)
            except ValueError:
                return
        else:
            return
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Bot running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            events = slack_client.rtm_read()
            for event in events:
                if (
                    'channel' in event and
                    'text' in event and
                    event.get('type') == 'message'
                ):
                    channel = event['channel']
                    command = event['text']
                    user_id = event.get('user', '')
                    if command:
                        handle_command(command, channel, user_id, starterbot_id)
                    time.sleep(DELAY)
    else:
        print("Connection failed.")


