import csv
import requests
from rich.console import Console

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
