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

# Load last run time assign.py finised running from last_run.txt
if os.path.exists("last_run.txt"):
    with open("last_run.txt", "r") as f:
        last_run = datetime.fromisoformat(f.read().strip())
else:
    # If the file does not exist (this is the first time running), assume it was run just now
    last_run = datetime.now(timezone.utc)

print(f"Last run: {last_run}")

# loop through all repositories in SoC
for repo_fullname in repos:
    repo = g.get_repo(repo_fullname)
    issues = repo.get_issues(state="open")

    # Handle pagination for issues
    while issues:
        for issue in issues:
            comments = issue.get_comments()

            # Handle pagination for comments
            while comments:
                for comment in comments:
                    # If the comment was made before the last run, skip it
                    if comment.created_at <= last_run:
                        continue

                    # Assign user if "/assign me" is found and issue is unassigned
                    if "/assign me" in comment.body.lower():
                        if issue.assignee is None:
                            print(f"Assigning {comment.user.login} to issue {issue.number} in {repo.name}")
                            issue.add_to_assignees(comment.user.login)

                # Handle pagination, moving to the next page of comments if available
                if comments.has_next_page:
                    comments = comments.get_page(comments.next_page)
                else:
                    break

        # Move to the next page of issues if available
        if issues.has_next_page:
            issues = issues.get_page(issues.next_page)
        else:
            break

# Update last run time after all comments have been processed
with open("last_run.txt", "w") as f:
    f.write(datetime.now(timezone.utc).isoformat())
