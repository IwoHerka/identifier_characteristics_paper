import random

import pandas as pd


def sample_large_csv(input_filepath, output_filepath, sample_size):
    """
    Samples 'sample_size' rows from a very large CSV file and writes them to a new CSV file.

    Parameters:
    - input_filepath: Path to the input CSV file.
    - output_filepath: Path where the sampled CSV will be saved.
    - sample_size: Number of random rows to sample.
    """
    # First, determine the total number of rows in the file (excluding the header)
    with open(input_filepath, 'r', encoding='utf-8') as file:
        total_rows = sum(1 for row in file) - 1
    
    # Generate 'sample_size' random row indices
    if sample_size < total_rows:
        sampled_indices = set(sorted(random.sample(range(total_rows), sample_size)))
    else:
        # If sample_size is greater than or equal to total_rows, use all rows
        sampled_indices = set(range(total_rows))
    
    # Initialize variables for processing
    chunksize = 10000  # Adjust based on your system's memory constraints
    processed_rows = 0  # Keep track of processed rows to adjust indices correctly

    # Process the CSV in chunks and write sampled rows to a new file
    with open(output_filepath, 'w', encoding='utf-8', newline='') as output_file:
        for chunk in pd.read_csv(input_filepath, chunksize=chunksize):
            # Adjust indices within the chunk based on processed rows
            rows_in_chunk = set(range(processed_rows, processed_rows + len(chunk)))
            sampled_rows_in_chunk = sampled_indices & rows_in_chunk
            # Adjust indices to be relative to the current chunk
            relative_indices = [index - processed_rows for index in sampled_rows_in_chunk]
            
            if relative_indices:
                sampled_chunk = chunk.iloc[relative_indices]
                # Write header only for the first chunk and append rows to the output file
                sampled_chunk.to_csv(output_file, mode='a', header=output_file.tell()==0, index=False)
            
            processed_rows += len(chunk)
            # Remove sampled rows from the set to avoid attempting to sample them again
            sampled_indices -= sampled_rows_in_chunk


if __name__ == '__main__':
    # Example usage:
    # sample_large_csv('build/names/c.csv', 'build/sampled/c.csv', 500000)
    sample_large_csv('build/names/clojure.csv', 'build/sampled/clojure.csv', 500000)
    sample_large_csv('build/names/elixir.csv', 'build/sampled/elixir.csv', 500000)
    # sample_large_csv('build/names/erlang.csv', 'build/sampled/erlang.csv', 500000)
    # sample_large_csv('build/names/haskell.csv', 'build/sampled/haskell.csv', 500000)
    sample_large_csv('build/names/java.csv', 'build/sampled/java.csv', 500000)
    sample_large_csv('build/names/javascript.csv', 'build/sampled/javascript.csv', 500000)
    # sample_large_csv('build/names/ocaml.csv', 'build/sampled/ocaml.csv', 500000)
    sample_large_csv('build/names/python.csv', 'build/sampled/python.csv', 500000)

