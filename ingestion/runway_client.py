import os
import requests

class RunwayClient:
    def __init__(self):
        token = os.getenv("RUNWAY_API_TOKEN")
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_current_release_status(self):
        response = requests.get("https://api.runway.team/v1/releases", headers=self.headers)
        response.raise_for_status()
        return response.json()

def create_runway_client():
    return RunwayClient()