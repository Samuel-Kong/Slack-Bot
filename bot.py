import os
import time
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.rtm_v2 import RTMClient

slack_token = os.environ.get('SLACK_BOT_TOKEN')
slack_client = WebClient(token=slack_token)
starterbot_id = None

RTM_READ_DELAY = 1
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(event_data):
    event = event_data.get("event", {})
    if event.get("type") == "message" and not event.get("subtype"):
        user_id, message = parse_direct_mention(event.get("text", ""))
        if user_id == starterbot_id:
            return message, event.get("channel")
    return None, None

def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)
    response = None
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    try:
        slack_client.chat_postMessage(
            channel=channel,
            text=response or default_response
        )
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")

@RTMClient.run_on(event="message")
def message_handler(**payload):
    data = payload["data"]
    web_client = payload["web_client"]
    global starterbot_id

    if starterbot_id is None:
        auth_response = web_client.auth_test()
        starterbot_id = auth_response["user_id"]

    command, channel = parse_bot_commands({"event": data})
    if command:
        handle_command(command, channel)

if __name__ == "__main__":
    rtm_client = RTMClient(token=slack_token)
    print("Starter Bot connected and running!")
    rtm_client.start()
