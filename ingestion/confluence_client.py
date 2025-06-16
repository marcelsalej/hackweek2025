import os
from atlassian import Confluence

def create_confluence_client():
    return Confluence(
        url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        password=os.getenv("CONFLUENCE_API_TOKEN")
    )