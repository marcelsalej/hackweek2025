def fetch_linear_issues(linear_client, team_id):
    return linear_client.issues(team_id=team_id)