# BranchLog

> 🔍 Track which Git branches you've worked on recently.

**BranchLog** is a simple CLI tool that shows Git branches where you've made commits recently — perfect for developers who juggle multiple branches and want a quick summary of their weekly activity.

---

## ✨ Features

* ✅ List all local branches you’ve committed to in the last *N* days
* ✅ Filter by author (default: your Git username)
* ✅ Group branches by type (e.g. `feature/*`, `fix/*`, `hotfix/*`)
* ✅ Show commit counts and latest commit messages
* ✅ Analyze any Git repository with `--path`

---

## 🛠 Installation

```bash
pip install branchlog
```

Or install from source:

```bash
git clone https://github.com/yourusername/branchlog.git
cd branchlog
pip install -e .
```

---

## 🚀 Usage

```bash
branchlog --days 7
```

### Options

| Option     | Description                                              |
| ---------- | -------------------------------------------------------- |
| `--days`   | Number of past days to check for commits (default: `7`)  |
| `--author` | Git author name (default: current git user)              |
| `--path`   | Path to the Git project (default: current directory `.`) |

### Example

```bash
branchlog --days 14 --author rahman --path ~/projects/myapp
```

---

## 📊 Output Example

```
Branches with commits by 'rahman' in the last 7 days:

🔹 Group: feature/*
- feature/api-integration (3 commits, latest: fix: handle null response)
- feature/login-refactor (2 commits, latest: refactor: improved error handling)

🔹 Group: fix/*
- fix/user-crash (1 commit, latest: fix: crash on empty user list)

📊 Summary:
- Total branches: 3
- Total commits: 6
- Most active branch: feature/api-integration (3 commits)
```

---

## 🦪 Pro Tip

Run `branchlog` from a scheduled cron job or GitHub Action to keep a daily/weekly activity log!

---

## 💡 Roadmap Ideas

* GitHub API integration
* Detect merged/unmerged branches
* Visualize commit trends
* Export as markdown or JSON

---

## 📄 License

MIT License © [Rahman](mailto:tanmay1007031@gmail.com)

---

## 🙌 Contributions Welcome

If you have ideas, feedback, or bug reports, feel free to open an issue or pull request.
