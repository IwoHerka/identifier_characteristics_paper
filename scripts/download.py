import os
import shutil
import math
import subprocess
import time
import requests

from rich.console import Console
from db.models import Repo
from scripts.lang import LANG_TO_EXT
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
    file_extensions = [ext for lang in LANG_TO_EXT.values() for ext in lang]
    repos = get_repos()

    if only_missing:
        repos = repos.filter(Repo.path == None)

    repos = repos.all()

    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}"
    }


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

        # Initialize a new git repository
        subprocess.run(["git", "init", dest_repo_path])
        subprocess.run(["git", "-C", dest_repo_path, "remote", "add", "origin", url])

        # Enable sparse-checkout
        subprocess.run(["git", "-C", dest_repo_path, "config", "core.sparseCheckout", "true"])

        # Specify the files to checkout
        sparse_checkout_path = os.path.join(dest_repo_path, ".git", "info", "sparse-checkout")
        with open(sparse_checkout_path, "w") as sparse_file:
            if file_extensions:
                for extension in file_extensions:
                    console.print(f"Adding {extension} to sparse checkout")
                    sparse_file.write(f"*{extension}\n")
            else:
                sparse_file.write("*\n")  # Checkout all files if no extension is specified

            # Add readme files to sparse checkout
            sparse_file.write("README.md\n")
            sparse_file.write("readme.md\n")
            sparse_file.write("README.txt\n")
            sparse_file.write("readme.txt\n")
            sparse_file.write("README.rst\n")
            sparse_file.write("readme.rst\n")
            sparse_file.write("readme\n")
            sparse_file.write("README\n")

        # Fetch the default branch using GitHub API
        repo_api_url = f"https://api.github.com/repos/{repo.owner}/{repo.name}"
        response = requests.get(repo_api_url, headers=headers)
        if response.status_code == 200:
            default_branch = response.json().get("default_branch", "main")
        else:
            console.print(f"Failed to get default branch for {repo.name}, using 'main' as fallback")
            default_branch = "main"

        # Perform the checkout using the default branch
        subprocess.run(["git", "-C", dest_repo_path, "pull", "origin", default_branch, "--depth", "1"])

        # ... existing code for reading README and updating repo ...
        # Read the entire README.md and decide how much to save
        readme_content = ""
        readme_files = ["README.md", "readme.md", "README.txt", "readme.txt", "README.rst", "readme.rst", "readme", "README"]

        for readme_file in readme_files:
            readme_path = os.path.join(dest_repo_path, readme_file)
            if os.path.exists(readme_path):
                break
        else:
            readme_path = None

        try:
            with open(readme_path, "r", encoding="utf-8") as readme_file:
                lines = readme_file.readlines()
                if len(lines) < 25:
                    readme_content = "".join(lines)
                else:
                    readme_content = "".join(lines[:25])
        except Exception as e:
            readme_content = None
            print(f"Error reading README.md for {repo.name}: {e}")
        except UnicodeDecodeError:
            readme_content = "unicode_decode_error"

        update_repo(repo, path=dest_repo_path, readme=readme_content)


import requests
import os

def get_first_commit_date(repo_id):
    """
    Get the date of the first commit in a GitHub repository.

    :param owner: Owner of the repository
    :param repo: Name of the repository
    :return: Date of the first commit as a string
    """
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # GitHub API URL to list commits
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    
    # Parameters to get all commits
    params = {
        "per_page": 100,
        "page": 1
    }
    
    all_commits = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to retrieve commits: {response.status_code}")
            return None
        
        commits = response.json()
        if not commits:
            break
        
        all_commits.extend(commits)
        params["page"] += 1
    
    # The first commit is the last one in the list
    first_commit = all_commits[-1]
    first_commit_date = first_commit['commit']['committer']['date']
    
    return first_commit_date


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
