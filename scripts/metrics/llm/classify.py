# Functions to, given a README file, use ChatGPT4 to classify a project type.
# Expectes OPENAI key env variable.

# TODO: Add Bard API

import os
import csv
import random
import requests

from openai import OpenAI
from rich.console import Console

from db.models import Repo
from db.utils import init_local_session

console = Console()


def read_first_20_lines(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()[:25]  # Read the first 20 lines
            return "".join(lines)  # Join the lines into a single string
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def list_readme_files(directory):
    readme_files = []

    # List all directories in the given directory
    directories = [
        d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))
    ]

    # Iterate through each directory
    for dir_name in directories:
        dir_path = os.path.join(directory, dir_name)

        # Get paths of README files directly within the directory
        for file in os.listdir(dir_path):
            if file.lower().startswith("readme."):
                readme_files.append((os.path.join(dir_path, file), dir_path))

    return readme_files


def get_written(csv_file_path):
    first_column_values = set()

    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)

        # Skip the header if your CSV file has one
        next(reader, None)  # Uncomment this line if your CSV has a header

        for row in reader:
            if row:  # Check if the row is not empty
                first_column_values.add(row[0])

    return first_column_values


def classify():
    session = init_local_session()

    for repo in Repo.all(session, lang='javascript'):
        if repo.about is not None:
            continue

        console.print(f"Download 'about' for {repo.name}", style="red")

        url = f"https://github.com/{repo.owner}/{repo.name}"
        about_url = f"https://api.github.com/repos/{repo.owner}/{repo.name}"
        token = os.getenv("GITHUB_TOKEN", "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")
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(about_url, headers=headers)
        if response.status_code == 200:
            about_info = response.json()
            about = about_info.get("description", "")
            repo.about = (about or "-")[:250]
            session.commit()
        else:
            console.print(f"Failed to download 'about' for {repo.name}", style="red")


if __name__ == "__main__":
    classify()
