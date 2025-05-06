import json
import os
import time
from datetime import datetime, timezone
from github import Github

GITHUB_TOKEN = os.getenv("GH_TOKEN")
g = Github(GITHUB_TOKEN)

with open("repos.json") as f:
    repos = json.load(f)

# Load last run time
if os.path.exists("last_run.txt"):
    with open("last_run.txt", "r") as f:
        last_run = datetime.fromisoformat(f.read().strip())
else:
    last_run = datetime.now(timezone.utc)

print(f"Last run: {last_run}")

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
