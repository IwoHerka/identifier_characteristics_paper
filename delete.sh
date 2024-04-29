#!/bin/bash

# Define an array of extensions to keep
extensions=(
    ".c"
    ".clj"
    ".ex" ".exs"
    ".erl" ".es" ".escript"
    ".f" ".for" ".ftn" ".f90" ".f95" ".f03" ".f08" ".f15" ".f18" ".fpp"
    ".hs" ".lhs"
    ".java"
    ".js"
    ".ml" ".mli"
    ".py"
    ".md"
)

# The directory to search
directory="_data"

# Build a negated condition for find to exclude files with specified extensions
condition=""
for ext in "${extensions[@]}"; do
    if [ -z "$condition" ]; then
        condition="-not -name '*$ext'"
    else
        condition="$condition -and -not -name '*$ext'"
    fi
done

# Use find to delete files not matching the specified extensions
find "$directory" -type f $condition -exec rm -f -v {} \;

