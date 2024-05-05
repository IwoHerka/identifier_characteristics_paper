import os
import csv
import requests

from rich.console import Console
from db.utils import *

console = Console()


def get_grammar(name):
    try:
        response = requests.get(f'http://localhost:5001/{name}/FUNCTION')
        return '.'.join(response.json())
    except:
        return ''


def save_grammar(outfile, names):
    print(outfile)
    with open(outfile, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        console.print(f'Extracting to {outfile}...', style='bold red')

        for name in names:
            grammar = get_grammar(name)
            console.print(f'{name} -> {grammar}', style='yellow')
            writer.writerow([name, grammar]) 
            outfile.flush()


def load_csv_file(file_path):
    name_grammar_map = {}
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            if len(row) >= 2 and row[1]:
                name, grammar = row[0], row[1]
                name_grammar_map[name] = grammar

    return name_grammar_map


def save_to_csv(name_grammar_map, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name', 'grammar'])  # Write headers

        for name, grammar in name_grammar_map.items():
            if grammar:
                # Checks if grammar is not an empty string
                writer.writerow([name, grammar])


def extract_grammar():
    known_grammars = load_csv_file('build/grammars.csv')
    periodic_update = 0

    for name in get_unique_function_names():
        console.print(f'Checking name: {name}...')

        # if not get_grammar_by_name(name):
        # console.print(f'Not found, updating grammar, checking cache')

        if name in known_grammars:
            grammar = known_grammars[name]
            console.print('Cache hit')
        else:
            console.print('Cache miss')
            grammar = get_grammar(name)
            known_grammars[name] = grammar
            update_function_grammar(name, grammar)

        periodic_update += 1

        if periodic_update >= 100:
            save_to_csv(known_grammars, 'build/grammars.csv')
            periodic_update = 0

    save_to_csv(known_grammars, 'build/grammars.csv')
