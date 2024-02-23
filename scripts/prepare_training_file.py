import re

def extract_words(input_files, output_file, n):
    word_re = re.compile(r'\b\w+\b')
    
    with open(output_file, 'w') as outfile:
        for file_path in input_files:
            word_count = 0

            with open(file_path, 'r') as infile:
                for line in infile:
                    words = word_re.findall(line)

                    for word in words:
                        # Write the word to the output file
                        outfile.write(word + ' ')
                        word_count += 1

                        if word_count == n:
                            break

                    if word_count == n:
                        break

if __name__ == '__main__':
    input_files = [
        'build/raw/c.txt',
        'build/raw/clojure.txt',
        'build/raw/elixir.txt',
        'build/raw/erlang.txt',
        'build/raw/haskell.txt',
        'build/raw/java.txt',
        'build/raw/javascript.txt',
        'build/raw/ocaml.txt',
        'build/raw/python.txt',
    ]
    output_file = 'build/raw/all.txt'
    n = 20000000

    extract_words(input_files, output_file, n)

