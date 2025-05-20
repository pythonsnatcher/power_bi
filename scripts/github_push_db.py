import os
from dotenv import load_dotenv
from git import Repo, GitCommandError
import shutil

# Load environment variables
print("Loading environment variables...")
load_dotenv()

# Debug: Show .env values loaded
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN")
GITHUB_REPO     = os.getenv("GITHUB_REPO")
REPO_PATH       = os.getenv("REPO_PATH", "./temp_repo")
DB_FILE         = os.getenv("DB_FILE", "/Users/snatch/PycharmProjects/power_bi_project/2_0/football_data.sqlite")

print(f"GITHUB_USERNAME: {GITHUB_USERNAME}")
print(f"GITHUB_TOKEN: {'[HIDDEN]' if GITHUB_TOKEN else None}")
print(f"GITHUB_REPO: {GITHUB_REPO}")
print(f"REPO_PATH: {REPO_PATH}")
print(f"DB_FILE: {DB_FILE}")

# Check for missing variables
if not all([GITHUB_USERNAME, GITHUB_TOKEN, GITHUB_REPO]):
    raise ValueError("Missing one or more required .env variables: GITHUB_USERNAME, GITHUB_TOKEN, GITHUB_REPO")

# Build secure repo URL
try:
    secure_url = GITHUB_REPO.replace(
        "https://", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@"
    )
    print(f"Secure URL built: {secure_url.split('@')[1]}")
except Exception as e:
    raise RuntimeError(f"Failed to build secure GitHub URL: {e}")

# Clone the repo or pull it if already exists
if os.path.exists(REPO_PATH):
    print("Repo path exists. Trying to open and pull...")
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remotes.origin
        origin.pull()
        print("Repo pulled successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to pull repo: {e}")
else:
    print("Cloning GitHub repo...")
    try:
        repo = Repo.clone_from(secure_url, REPO_PATH)
        print("Repo cloned successfully.")
    except GitCommandError as e:
        raise RuntimeError(f"Git clone failed: {e}")

# Copy the database file into the repo
dest_path = os.path.join(REPO_PATH, os.path.basename(DB_FILE))
print(f"Copying DB file from {DB_FILE} to {dest_path}...")
try:
    shutil.copy2(DB_FILE, dest_path)
    print("Database file copied.")
except Exception as e:
    raise RuntimeError(f"Failed to copy DB file: {e}")

# Commit and push changes
print("Staging and committing changes...")
try:
    repo.git.add(A=True)
    repo.index.commit("Update football_data.sqlite")
    repo.remotes.origin.push()
    print("Changes pushed to GitHub.")
except Exception as e:
    raise RuntimeError(f"Git push failed: {e}")
