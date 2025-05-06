import json
import os
from datetime import datetime, timezone
from github import Github

GITHUB_TOKEN = os.getenv("GH_TOKEN")
g = Github(GITHUB_TOKEN)

with open("repos.json") as f:
    repos = json.load(f)

for repo_fullname in repos:
    repo = g.get_repo(repo_fullname)
    issues = repo.get_issues(state="open")

    for issue in issues:
        if not issue.assignee:
            continue

        # Using due date from issue title or body (custom convention)
        # You can update this logic if due date is tracked in a label or milestone
        if "due:" in issue.title.lower():
            try:
                due_str = issue.title.lower().split("due:")[-1].strip().split()[0]
                due_date = datetime.strptime(due_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if due_date < datetime.now(timezone.utc):
                    print(f"Unassigning issue {issue.number} in {repo.name} — past due")
                    issue.remove_from_assignees(issue.assignee.login)
            except Exception as e:
                print(f"Error parsing due date in issue {issue.number}: {e}")
