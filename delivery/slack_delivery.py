import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def format_slack_message(summary: str):
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": summary
                }
            }
        ]
    }

def send_message(channel_id: str, blocks: list):
    token = os.getenv("SLACK_BOT_TOKEN")
    client = WebClient(token=token)
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text="Standup Summary"
        )
        print(f"Message sent successfully to channel {channel_id} (ts: {result['ts']})")
    except SlackApiError as e:
        print(f"Error sending message to Slack: {e.response['error']}")