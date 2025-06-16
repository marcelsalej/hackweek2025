import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Ingestion ---
from ingestion.slack import fetch_recent_messages
from ingestion.github import fetch_github_activity
from ingestion.jira import fetch_jira_issues
from ingestion.linear import fetch_linear_issues
from ingestion.confluence import fetch_confluence_updates
from ingestion.runway import fetch_runway_status

# --- Client Creation ---
from ingestion.github_client import create_github_client
from ingestion.jira_client import create_jira_client
from ingestion.linear_client import create_linear_client
from ingestion.confluence_client import create_confluence_client
from ingestion.runway_client import create_runway_client

# --- Processing ---
from processing.summarizer import generate_summary

# --- Delivery ---
from delivery.slack_delivery import format_slack_message, send_message


def main():
    """Main function to orchestrate the standup summary generation."""
    all_context = []
    print("Starting standup summarizer...")

    # 1. Gather context from various sources by checking for relevant env vars
    
    # Slack
    slack_channel_id = os.getenv("SLACK_STANDUP_CHANNEL_ID")
    if slack_channel_id:
        print("Fetching Slack messages...")
        slack_msgs = fetch_recent_messages(channel_id=slack_channel_id)
        all_context.extend([f"Slack Update: {msg}" for msg in slack_msgs])

    # GitHub
    github_repo = os.getenv("GITHUB_REPO_NAME")
    if github_repo and os.getenv("GITHUB_TOKEN"):
        print("Fetching GitHub activity...")
        gh_client = create_github_client()
        gh_activity = fetch_github_activity(gh_client, repo_name=github_repo)
        all_context.extend([f"GitHub PR Merged by {pr['user']}: {pr['title']}" for pr in gh_activity])

    # Jira
    jira_jql = os.getenv("JIRA_JQL")
    if jira_jql and os.getenv("JIRA_SERVER_URL"):
        print("Fetching Jira issues...")
        jira_client = create_jira_client()
        jira_issues = fetch_jira_issues(jira_client, jql=jira_jql)
        all_context.extend([f"Jira Issue {i['key']} ({i['status']}): {i['summary']}" for i in jira_issues])

    # Linear
    linear_team_id = os.getenv("LINEAR_TEAM_ID")
    if linear_team_id and os.getenv("LINEAR_API_KEY"):
        print("Fetching Linear issues...")
        linear_client = create_linear_client()
        linear_issues = fetch_linear_issues(linear_client, team_id=linear_team_id)
        all_context.extend([f"Linear Issue {i['id']} ({i['state']['name']}): {i['title']}" for i in linear_issues])
        
    # Confluence
    confluence_space = os.getenv("CONFLUENCE_SPACE_KEY")
    if confluence_space and os.getenv("CONfluence_URL"):
        print("Fetching Confluence updates...")
        confluence_client = create_confluence_client()
        confluence_pages = fetch_confluence_updates(confluence_client, space_key=confluence_space)
        all_context.extend([f"Confluence Update: Page '{p['title']}' was recently updated." for p in confluence_pages])

    # Runway
    if os.getenv("RUNWAY_API_TOKEN"):
        print("Fetching Runway status...")
        runway_client = create_runway_client()
        runway_status = fetch_runway_status(runway_client)
        all_context.append(f"Runway Status: {str(runway_status)}")


    if not all_context:
        print("No data fetched from any source. Exiting.")
        return

    context_str = "\n".join(all_context)
    print("\n--- Combined Context for Summarization ---\n", context_str)

    # 2. Generate summary
    print("\n--- Generating summary... ---")
    summary = generate_summary(context_str)
    print(summary)

    # 3. Deliver summary to Slack
    target_channel_id = os.getenv("SLACK_TARGET_CHANNEL_ID")
    if target_channel_id:
        print(f"\n--- Sending summary to Slack channel {target_channel_id}... ---")
        slack_message_blocks = format_slack_message(summary)
        send_message(channel_id=target_channel_id, blocks=slack_message_blocks["blocks"])
    else:
        print("\n--- Skipping Slack delivery: SLACK_TARGET_CHANNEL_ID not set. ---")

if __name__ == "__main__":
    main()