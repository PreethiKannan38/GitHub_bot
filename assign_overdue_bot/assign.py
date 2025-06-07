import json
import os
from datetime import datetime, timezone
from github import Github
import time

# Set up GitHub token
GITHUB_TOKEN = os.getenv("GH_TOKEN")
g = Github(GITHUB_TOKEN)

# Load the repositories from repos.json
with open("assign_overdue_bot/repos.json") as f:
    repos = json.load(f)

# Load last run time from last_run.txt
if os.path.exists("last_run.txt"):
    with open("last_run.txt", "r") as f:
        last_run = datetime.fromisoformat(f.read().strip())
else:
    last_run = datetime.now(timezone.utc)

print(f"Last run: {last_run}")

# Loop through all repositories
for repo_fullname in repos:
    repo = g.get_repo(repo_fullname)
    issues = repo.get_issues(state="open")

    for issue in issues:
        comments = issue.get_comments()

        for comment in comments:
            if comment.created_at <= last_run:
                continue

            if "/assign me" in comment.body.lower():
                if issue.assignee is None:
                    print(f"Assigning {comment.user.login} to issue {issue.number} in {repo.name}")
                    issue.add_to_assignees(comment.user.login)

# Update last run time
with open("last_run.txt", "w") as f:
    f.write(datetime.now(timezone.utc).isoformat())
