import os
import random
import subprocess

from rich.console import Console

console = Console()

import requests


def get_top_repos_by_language(language, num, page):
    url = "https://api.github.com/search/repositories"

    params = {
        "q": f"language:{language}",
        "sort": "stars",
        "order": "desc",
        "per_page": num, 
        "page": page
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Failed to retrieve data:", response.status_code)
        return []


def print_repos(repos):
    for repo in repos:
        print(f"Name: {repo['name']}")
        print(f"URL: {repo['html_url']}")
        print(f"Stars: {repo['stargazers_count']}")
        print(f"Language: {repo['language']}")
        print("-" * 60)


def clone_repos(repos, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for repo in repos:
        clone_url = repo['clone_url']
        repo_name = repo['name']
        dest_repo_path = os.path.join(dest_dir, repo_name)

        # Check if the repository has already been cloned
        if os.path.exists(dest_repo_path):
            console.print(f'\'{repo_name}\' already cloned, skipping', style='yellow')
            continue

        print(f'Cloning {repo_name} into {dest_repo_path}...')
        subprocess.run(["git", "clone", "--depth", "1", clone_url, dest_repo_path])


def download_top_repos(language, dest_dir, top_n, page):
    top_repos = get_top_repos_by_language(language, top_n, page)
    clone_repos(top_repos, dest_dir)


def list_source_code_files(directory, extensions):
    source_code_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.exists(full_path):
                if file.endswith(extensions):
                    source_code_files.append(full_path)

    return source_code_files


def count_total_lines(file_paths):
    total_lines = 0

    for file_path in file_paths:
        try:
            with open(file_path, "rb") as f:
                total_lines += sum(1 for l in f if l.strip())
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    return total_lines



def download_all(lang, ext, dest_dir, min_page, max_page, per_page):
    total_loc = 0

    for page in range(1, max_page):
        console.print(f'Downloading page {page}/{max_page} for {lang}', style='bold red')
        download_top_repos(lang, dest_dir, per_page, page)

    files = list_source_code_files(dest_dir, ext)
    total_loc += count_total_lines(files)

    console.print(f'Total number of files: {len(files)}', style='bold red')
    console.print(f'Total lines of code: {total_loc}', style='bold red')
    console.bell()


# repos = []

# import time

# for i in range(0, 5):
#     page = get_top_repos_by_language('Python', 100, i)
#     projects = [p['name'] for p in page]
#     console.print(len(projects))
#     repos.extend(projects)
#     time.sleep(2)


# console.print(f'Number of repositories: {len(repos)}')
# repos = random.sample(repos, 100)

# for repo in repos:
#     console.print(repo, style='red')
