import os
from github import Github

def create_github_client():
    token = os.getenv("GITHUB_TOKEN")
    return Github(token)