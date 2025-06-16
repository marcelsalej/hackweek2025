def fetch_jira_issues(jira_client, jql: str):
    issues = jira_client.search_issues(jql)
    return [{"key": i.key, "summary": i.fields.summary, "status": i.fields.status.name} for i in issues]