import os
import time
import json
import urllib
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
# constants
AT_BOT = "<@" + BOT_ID + ">"

EXAMPLE_COMMAND = "search"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "try @gitify search <stuff to search>  e.g @gitify search ionic sms plugin"                
    if command.startswith(EXAMPLE_COMMAND):
        query = urllib.quote_plus(command[7:])
        response = {
            'repositories': 'https://github.com/search?q='+query+'&type=Repositories&utf8=%E2%9C%93',
            'codes': 'https://github.com/search?q='+query+'&type=Code&utf8=%E2%9C%93',
            'commits': 'https://github.com/search?q='+query+'&type=Commits&utf8=%E2%9C%93',
            'Issues': 'https://github.com/search?q='+query+'&type=Issues&utf8=%E2%9C%93',
            'wikis': 'https://github.com/search?q='+query+'&type=Wikis&utf8=%E2%9C%93',
            'users': 'https://github.com/search?q='+query+'&type=Users&utf8=%E2%9C%93'
        }
        message = "`"+str(json.dumps(response))+"`"

    slack_client.api_call(
        "chat.postMessage", 
        channel=channel,
        text=message, 
        as_user=True
    )


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
