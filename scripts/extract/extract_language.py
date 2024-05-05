# import csv
# import os

# from ..parsing.parsers import *
# from tree_sitter import Language, Parser


# def list_files(directory):
#     for dirpath, dirnames, filenames in os.walk(directory):
#         for filename in filenames:
#             yield os.path.join(dirpath, filename)


# def extract_language(lang, indir, outdir):
#     """
#     Generates (function, names) CSV per language with all projects from project
#     download directory.
#     E.g.: data/<lang>/** -> build/names/<lang>.csv
#     """
#     parser = Parser()
#     print(lang)
#     parser.set_language(Language('build/parser_bindings.so', lang))
#     outfile = f'{outdir}/{lang}.csv'
    
#     with open(outfile, 'w', newline='', encoding='utf-8') as outfile:
#         writer = csv.writer(outfile)

#         for file in list_files(indir):
#             if 'README.md' in file:
#                 continue

#             print(f'Writing names for {file}...')

#             try:
#                 fnames = extract(parser, file, globals()[f'extract_{lang}'])

#                 for fname, names in fnames.items():
#                     writer.writerow([fname, ' '.join(names)]) 
#             except Exception as e: 
#                 print(e)
#                 pass
