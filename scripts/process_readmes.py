import requests

# List of GitHub repositories in the format "owner/repo"
repositories = [
    "torvalds/linux",
    "facebook/react",
    # Add more repository names here
]


def download_readme_first_20_lines(repo):
    """
    Download the first 20 lines of the README.md file for a given GitHub repository.
    """
    # GitHub API URL for the README.md file content
    url = f"https://api.github.com/repos/{repo}/readme"
    
    # Optional: Replace 'your_token_here' with your GitHub Personal Access Token to increase rate limit
    headers = {"Accept": "application/vnd.github.v3.raw"} #, "Authorization": "token your_token_here"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.text.splitlines()[:20]  # Get the first 20 lines
        return "\n".join(content)
    else:
        return "Error: Could not fetch README.md"


for repo in repositories:
    print(f"First 20 lines of README.md for {repo}:")
    readme_lines = download_readme_first_20_lines(repo)
    print(readme_lines)
    print("-" * 80)  # Separator

