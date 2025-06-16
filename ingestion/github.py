from github import Github

def fetch_github_activity(client: Github, repo_name: str):
    repo = client.get_repo(repo_name)
    prs = repo.get_pulls(state='closed', sort='updated', direction='desc')
    
    recent_prs = []
    for pr in prs[:20]:
        if pr.merged:
            recent_prs.append({"title": pr.title, "merged": pr.merged, "user": pr.user.login})
    return recent_prs