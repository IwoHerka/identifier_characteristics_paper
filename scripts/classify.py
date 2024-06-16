# Functions to, given a README file, use ChatGPT4 to classify a project type.
# Expectes OPENAI key env variable.

# TODO: Add Bard API

import os
import csv
import random

from openai import OpenAI
from rich.console import Console

console = Console()


def read_first_20_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()[:25]  # Read the first 20 lines
            return ''.join(lines)  # Join the lines into a single string
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def list_readme_files(directory):
    readme_files = []
    
    # List all directories in the given directory
    directories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    
    # Iterate through each directory
    for dir_name in directories:
        dir_path = os.path.join(directory, dir_name)
        
        # Get paths of README files directly within the directory
        for file in os.listdir(dir_path):
            if file.lower().startswith('readme.'):
                readme_files.append((os.path.join(dir_path, file), dir_path))
    
    return readme_files


def get_written(csv_file_path):
    first_column_values = set()
    
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Skip the header if your CSV file has one
        next(reader, None)  # Uncomment this line if your CSV has a header
        
        for row in reader:
            if row:  # Check if the row is not empty
                first_column_values.add(row[0])
    
    return first_column_values


# TODO: Make into a command in main.py
def classify(lang, outdir, limit):
    client = OpenAI(api_key=os.environ.get("OPENAI"))

    f = f'{outdir}/{lang}.csv'
    written = get_written(f)
    # console.print(written)

    i = 0

    with open(f, 'a', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        a = list_readme_files(f'data/{lang}')
        random.shuffle(a)
        random.shuffle(a)
        random.shuffle(a)

        for readme, dir_path in a:
            project_name = dir_path.split('/')[-1]
            readme_head = read_first_20_lines(readme)

            i += 1

            if i == limit:
                break

            if project_name in written:
                continue

            console.print(f'#{i}', style='red')

            prompt = f"""
            Given a fragment of the README, determine whether project belongs to one of the following categories:

            - lib/web - library related to networking, such as HTTP clients, HTTP servers, web scrappers or other utilities
            - lib/cli - library related to command line, such as CLI utilities, pretty printing, tools for building CLI apps
            - edu - educational, typically a collection of code examples, articles, something that is not an app, for human to read
            - lib/db - library related to databases, such as database ORMs, utilities, integrations and so on
            - lib/ml - project related to machine learning, AI, deep learning, and so on

            If project doesn't fit into any of those, assign it to 'lib/other'. It is
            likely that you will encounter projects which don't fit, so don't try
            to fit them forcibly. When classifying, pick one most
            dominant/core/crucial aspect of it. For example, is the project is a
            web app for covnerting screenshots to code using AI, the category
            should be lib/ml, not lib/web. If project is not runnable, but a
            collection of resources, it's probably 'edu'. Then, give a short, one
            sentence summary what the project is about. Provide answer in the
            format:

            <type>,'<summary>'

            Here is the fragment of the README (it may contain some HTML, ignore it):

            {readme_head}
            """

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                # model="gpt-3.5-turbo"
                model="gpt-4"
            )

            response = chat_completion.choices[0].message.content

            console.print(f'{project_name},{response}', style='yellow')
            writer.writerow([project_name] + response.split(','))
            out_file.flush()


if __name__ == '__main__':
    classify()
