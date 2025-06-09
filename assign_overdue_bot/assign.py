import json
import os
from datetime import datetime, timezone
from github import Github
import time

# Set up GitHub token
#GITHUB_TOKEN = os.getenv("GH_TOKEN")
#g = Github(GITHUB_TOKEN)

token = os.getenv("GITHUB_TOKEN")
g = Github(token)

# Load the repositories from repos.json
with open("assign_overdue_bot/repos.json") as f:
    repos = json.load(f)
    print("loaded repos from json files")

# Load last run time from last_run.txt
if os.path.exists("assign_overdue_bot/last_run.txt"):
    with open("assign_overdue_bot/last_run.txt", "r") as f:
        last_run = datetime.fromisoformat(f.read().strip())
        print("last run time retrived from file")
else:
    last_run = datetime.now(timezone.utc)
    print("last run time set")

print(f"Last run: {last_run}")

# Loop through all repositories
for repo_fullname in repos:
    repo = g.get_repo(repo_fullname)
    issues = repo.get_issues(state="open")
    print("got issues from repo")

    for issue in issues:
        comments = issue.get_comments()
        print("got comments from issues")

        for comment in comments:
            print("going through comments")
            if comment.created_at <= last_run:
                print("comment created in last run")
                continue

            if "/assign me" in comment.body.lower():
                print("found /assign me in comments")
                if not issue.assignees:
                    print(f"Assigning {comment.user.login} to issue {issue.number} in {repo.name}")
                    issue.add_to_assignees(comment.user.login)

# Update last run time
with open("assign_overdue_bot/last_run.txt", "w") as f:
    f.write(datetime.now(timezone.utc).isoformat())
    print("last run time written in file")
