import subprocess

class GitRepository:
    def __init__(self):
        pass

    def is_valid_repo(self):
        return subprocess.call([
            "git", "rev-parse", "--is-inside-work-tree"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def get_user(self):
        return subprocess.getoutput("git config user.name")

    def get_local_branches(self):
        result = subprocess.getoutput("git for-each-ref --format='%(refname:short)' refs/heads")
        return result.strip().split("\n") if result.strip() else []

    def get_commits(self, branch, author, since_date):
        cmd = f'git log {branch} --since="{since_date}" --author="{author}" --oneline'
        output = subprocess.getoutput(cmd)
        return output.strip().split("\n") if output.strip() else []
