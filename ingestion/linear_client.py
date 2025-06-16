import os
import requests

class LinearClient:
    def __init__(self):
        self.api_key = os.getenv("LINEAR_API_KEY")
        self.headers = {"Authorization": self.api_key}

    def issues(self, team_id):
        query = {
            "query": """
                query Issues($teamId: String!) {
                    issues(filter: {team: {id: {eq: $teamId}}}) {
                        nodes {
                            id
                            title
                            state {
                                name
                            }
                        }
                    }
                }
            """,
            "variables": { "teamId": team_id }
        }
        response = requests.post("https://api.linear.app/graphql", json=query, headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]["issues"]["nodes"]

def create_linear_client():
    return LinearClient()