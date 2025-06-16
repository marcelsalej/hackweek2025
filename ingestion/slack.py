import os
from slack_sdk import WebClient

def fetch_recent_messages(channel_id: str):
    token = os.getenv("SLACK_BOT_TOKEN")
    client = WebClient(token=token)
    response = client.conversations_history(channel=channel_id, limit=100)
    return [msg["text"] for msg in response["messages"] if "text" in msg and "bot_id" not in msg]