import os
import csv
import requests
from multiprocessing import Process

from rich.console import Console
from db.utils import *
from db.engine import get_engine

console = Console()


def get_grammar(name, port):
    try:
        response = requests.get(f'http://localhost:{port}/{name}/FUNCTION')
        return '.'.join(response.json())
    except:
        return ''


def save_grammar(outfile, names):
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


TAGGER_BASE_PORT = 5000

def get_chunk(values, index, num_processes):
    chunk_size = len(values) // num_processes
    start = index * chunk_size

    # For the last chunk, ensure it includes any remaining elements
    if index == num_processes - 1:
        end = len(values)
    else:
        end = start + chunk_size

    return values[start:end]


def extract_grammar():
    num_processes = 4
    fn_names = get_distinct_function_names_without_grammar()

    processes = []
    for i in range(num_processes):
        chunk = get_chunk(fn_names, i, num_processes)
        p = Process(target=foo, args=(chunk, TAGGER_BASE_PORT + i))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


# TODO: Clean up
# More info to console
def foo(names, port):
    session = new_session(get_engine())

    for i, name in enumerate(names):
        console.print(f'Checking name: {name}...')
        grammar = get_grammar(name, port)
        update_function_grammar(session, name, grammar)
