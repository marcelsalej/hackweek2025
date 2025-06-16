import os
from jira import JIRA

def create_jira_client():
    server_url = os.getenv("JIRA_SERVER_URL")
    email = os.getenv("JIRA_USER_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    options = {"server": server_url}
    return JIRA(options, basic_auth=(email, api_token))