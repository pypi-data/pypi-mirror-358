# File: branchlog/__main__.py
import argparse
import os
from datetime import datetime, timedelta
from collections import defaultdict
from branchlog.local_git import GitRepository
import logging

def parse_args():
    parser = argparse.ArgumentParser(description="List Git branches you worked on in the last N days.")
    parser.add_argument("--days", type=int, default=7, help="Number of past days to check")
    parser.add_argument("--author", type=str, help="Git author name (default: git config user.name)")
    parser.add_argument("--path", type=str, default=".", help="Path to the Git project (default: current directory)")
    return parser.parse_args()


def render_output(summary, author, days):
    if not summary:
        logging.info(f"No commits found by '{author}' in the last {days} days.")
        return

    grouped = defaultdict(list)
    total_commits = 0

    for branch, count, preview in summary:
        prefix = branch.split("/")[0] if "/" in branch else "other"
        grouped[prefix].append((branch, count, preview))
        total_commits += count

    most_active = max(summary, key=lambda x: x[1]) if summary else (None, 0, "")

    logging.info(f"\nBranches with commits by '{author}' in the last {days} days:\n")
    for group, branches in grouped.items():
        logging.info(f"🔹 Group: {group}/*")
        for b, count, preview in branches:
            logging.info(f"- {b} ({count} commits, latest: {preview})")
        logging.info("")
    logging.info("📊 Summary:")
    logging.info(f"- Total branches: {len(summary)}")
    logging.info(f"- Total commits: {total_commits}")
    logging.info(f"- Most active branch: {most_active[0]} ({most_active[1]} commits)")


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()

    try:
        os.chdir(args.path)
    except FileNotFoundError:
        logging.error(f"Path '{args.path}' does not exist.")
        return
    except NotADirectoryError:
        logging.error(f"Path '{args.path}' is not a directory.")
        return

    repo = GitRepository()

    if not repo.is_valid_repo():
        logging.info("Not inside a Git repository.")
        return

    author = args.author or repo.get_user()
    since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    branches = repo.get_local_branches()

    summary = []

    for branch in branches:
        commits = repo.get_commits(branch, author, since_date)
        if commits:
            summary.append((branch, len(commits), commits[0][:50]))

    render_output(summary, author, args.days)


if __name__ == "__main__":
    main()
