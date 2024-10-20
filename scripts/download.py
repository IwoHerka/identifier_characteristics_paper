import os
import shutil
import math
import subprocess
import time
import requests

from rich.console import Console
from db.models import Repo
from db.utils import add_repo, update_repo, get_repos

console = Console()


def get_top_repos_by_language(language, num, page):
    """
    Download info on top 'num' GitHub repositories on specified page for
    specified language.
    """
    token = os.getenv("GITHUB_TOKEN")
    
    # Define the URL and parameters for the request
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"language:{language}",
        "sort": "stars",
        "order": "desc",
        "per_page": num,
        "page": page,
    }

    # Set the Authorization header with Bearer token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()["items"]
    else:
        console.print("Failed to retrieve data:", response.status_code)
        return []


def clone_repos(dest_dir, force=False, only_missing=False):
    """
    Clone repository for each repo in 'repos' table. For each repo, fill in
    'path' and 'readme' columns.
    """
    repos = get_repos()

    if only_missing:
        repos = repos.filter(Repo.path == None)

    repos = repos.all()

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for repo in repos:
        if repo.path and not force:
            continue

        dest_repo_path = os.path.join(dest_dir, repo.lang, f"{repo.owner}_{repo.name}")

        if os.path.exists(dest_repo_path):
            if force:
                console.print(f"'{repo.name}' already cloned, deleting")
                subprocess.run(["rm", "-r", "-f", dest_repo_path])
            else:
                console.print(f"'{repo.name}' already cloned, skipping")
                continue

        console.print(f"Cloning {repo.name} into {dest_repo_path}...")
        url = f"https://github.com/{repo.owner}/{repo.name}.git"
        subprocess.run(["git", "clone", "--depth", "1", url, dest_repo_path])

        # Read the entire README.md and decide how much to save
        readme_path = os.path.join(dest_repo_path, "README.md")
        readme_content = ""

        try:
            with open(readme_path, "r", encoding="utf-8") as readme_file:
                lines = readme_file.readlines()
                if len(lines) < 25:
                    readme_content = "".join(lines)
                else:
                    readme_content = "".join(lines[:25])
        except IOError:
            readme_content = None
            print(f"Error reading README.md for {repo.name}")
        except UnicodeDecodeError:
            readme_content = "unicode_decode_error"

        update_repo(repo, path=dest_repo_path, readme=readme_content)


def download_repos(lang, dest_dir, num_projects):
    """
    Download top 'num_projects' repositories for specified language and save their
    info to the database.

    Note: This function does not check for IntegrityError - table must be empty!
    """
    per_page = min(num_projects, 100)
    max_page = math.ceil(num_projects / per_page)
    delay = os.getenv("GITHUB_REQUEST_DELAY", 2)
    console.print(f"Looking for repositories, per_page={per_page}, max_page={max_page}")

    for page in range(1, max_page + 1):
        console.print(f"Downloading page {page}/{max_page} for {lang}", style="yellow")
        repos = get_top_repos_by_language(lang, per_page, page)
        time.sleep(delay)

        for repo in repos:
            console.print(f'Adding {repo["full_name"]}')
            add_repo(
                id=repo["id"],
                name=repo["name"],
                stars=repo["stargazers_count"],
                size=repo["size"],
                lang=lang,
                owner=repo["owner"]["login"],
            )
