import csv

# Specify the input and output file names
input_filename = "build/abbreviations.csv"
output_filename = "output.csv"

# Open the input file for reading and the output file for writing
with open(input_filename, mode="r", newline="") as infile, open(
    output_filename, mode="w", newline=""
) as outfile:
    reader = csv.reader(infile, delimiter="\t")
    writer = csv.writer(outfile)

    for row in reader:
        print(row)
        # Extract the abbreviation and full word from each row
        abbr, word = row[0], row[1]

        # Write the abbreviation and full word to the output file
        writer.writerow([word, abbr])

print(f"Processed {input_filename} and wrote results to {output_filename}.")
