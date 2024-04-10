
from rich.console import Console


console = Console()

import os
import csv
from collections import defaultdict

def count_projects_by_category(directory):
    results = {}
    summary = defaultdict(lambda: defaultdict(int))
    
    # Navigate through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            path = os.path.join(directory, filename)
            category_count = defaultdict(int)
            total_projects = 0
            
            # Open and read the CSV file
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip the header if there is one
                next(reader, None)
                
                # Count projects by category and total projects
                for row in reader:
                    if len(row) > 1:  # Assuming the format is as specified
                        category = row[1]
                        category_count[category] += 1
                        total_projects += 1

            # Store results for this file and update summary
            results[filename] = {}
            for category, count in category_count.items():
                proportion = count / total_projects if total_projects else 0
                results[filename][category] = (count, proportion)
                summary[category][filename] = count
    
    return results, dict(summary)

# Example usage
directory_path = 'build/classified'
project_counts = count_projects_by_category(directory_path)
console.print(project_counts)

