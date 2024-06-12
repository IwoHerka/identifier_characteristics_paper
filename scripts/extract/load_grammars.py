import os
import csv

# TODO: Probably not needed

def load_csv_file(file_path):
    name_grammar_map = {}
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) >= 2 and row[1]:  # Ensure there are at least two elements and grammar is not empty
                name, grammar = row[0], row[1]
                name_grammar_map[name] = grammar

    return name_grammar_map


def save_to_csv(name_grammar_map, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name', 'grammar'])  # Write headers
        for name, grammar in name_grammar_map.items():
            if grammar:  # Checks if grammar is not an empty string
                writer.writerow([name, grammar])


# if __name__ == "__main__":
#     result = load_csv_file('build/grammars.csv')
#     save_to_csv(result, 'build/grammars.csv')
