import requests
import os
import subprocess

def get_top_repos_by_language(language, num, page):
    url = "https://api.github.com/search/repositories"

    params = {
        "q": f"language:{language}",
        "sort": "stars",
        "order": "desc",
        "per_page": num, 
        "page": page
    }

    # Make the API request
    response = requests.get(url, params=params)
    
    # Check if the request was successful
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
            print(f'Repository {repo_name} already cloned. Skipping...')
            continue

        print(f'Cloning {repo_name} into {dest_repo_path}...')
        subprocess.run(["git", "clone", clone_url, dest_repo_path])


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



if __name__ == '__main__':
    # Example usage
    # language = 'OCaml'
    language = 'Fortran'
    # dest_dir = 'data/ocaml'
    dest_dir = 'data/fortran'
    # ext = '.ml'
    ext = '.f'
    max_page = 10
    total_loc = 0

    for page in range(1, max_page):
        print(f'Downloading page {page}/{max_page} for {language}')
        download_top_repos(language, dest_dir, 100, page)

    # files = list_source_code_files(dest_dir, ext)
    # total_loc += count_total_lines(files)

    # print(f'num files: {len(files)}')
    # print(f'LOC: {total_loc}')

