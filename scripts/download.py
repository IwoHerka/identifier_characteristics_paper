import os
import shutil
import random
import math
import subprocess
import requests
from datetime import datetime
import csv

from rich.console import Console
from db.utils import add_repo, update_repo, get_repos
from scripts.exts import get_exts

console = Console()


def get_top_repos_by_language(language, num, page):
    """
    Download top 'num' GitHub repositories on specified page for specified language.
    """
    url = "https://api.github.com/search/repositories"

    params = {
        "q": f"language:{language}",
        "sort": "stars",
        "order": "desc",
        "per_page": num, 
        "page": page
    }

    console.print(params)
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Failed to retrieve data:", response.status_code)
        console.print(response)
        return []


def print_repos(repos):
    for repo in repos:
        print(f"Name: {repo['name']}")
        print(f"URL: {repo['html_url']}")
        print(f"Stars: {repo['stargazers_count']}")
        print(f"Language: {repo['language']}")
        print("-" * 60)


def clone_repos(dest_dir):
    """
    Clone repository for each repo in 'repos' table. For each repo, fill in
    'path' and 'readme' columns.
    """
    repos = get_repos()

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for repo in repos:
        # Optionally:
        # if repo.path:
        #     continue

        dest_repo_path = os.path.join(dest_dir, repo.lang, f'{repo.owner}_{repo.name}')

        # Check if the repository has already been cloned
        if os.path.exists(dest_repo_path):
            print(f'\'{repo.name}\' already cloned, skipping')
        else:
            print(f'Cloning {repo.name} into {dest_repo_path}...')
            url = f'https://github.com/{repo.owner}/{repo.name}.git'
            subprocess.run(["git", "clone", "--depth", "1", url, dest_repo_path])

        # Read the entire README.md and decide how much to save
        readme_path = os.path.join(dest_repo_path, 'README.md')
        readme_content = ""

        try:
            with open(readme_path, 'r', encoding='utf-8') as readme_file:
                lines = readme_file.readlines()
                if len(lines) < 25:
                    readme_content = ''.join(lines) 
                else:
                    readme_content = ''.join(lines[:25])
        except IOError:
            readme_content = None
            print(f'Error reading README.md for {repo.name}')
        except UnicodeDecodeError:
            readme_content = "unicode_decode_error"

        # remove_symlinks(dest_repo_path)
        # remove_files_by_extension(dest_repo_path, repo.lang)
        # flatten_directory(dest_repo_path)
        update_repo(repo, path=dest_repo_path, readme=readme_content)


def download_lang(lang, dest_dir, num_projects):
    per_page = min(num_projects, 100)
    max_page = math.ceil(num_projects / per_page)
    console.print(f'Looking for repositories, per_page={per_page}, max_page={max_page}')

    for page in range(1, max_page+1):
        console.print(f'Downloading page {page}/{max_page} for {lang}', style='yellow')
        repos = get_top_repos_by_language(lang, per_page, page)

        for repo in repos:
            console.print(f'Adding {repo["full_name"]}')
            add_repo(
                id=repo['id'],
                name=repo['name'],
                stars=repo['stargazers_count'],
                size=repo['size'],
                lang=lang,
                owner=repo['owner']['login']
            )
