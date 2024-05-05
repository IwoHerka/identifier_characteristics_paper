# import csv
# import os

# from tree_sitter import Language, Parser
# from rich.console import Console

# from ..parsing.parsers import *
# from ..exts import is_ext_valid

# console = Console()


# def list_files(directory):
#     for dirpath, dirnames, filenames in os.walk(directory):
#         for filename in filenames:
#             yield os.path.join(dirpath, filename)


# def extract_project(indir, lang, output_dir):
#     """
#     Generates (function, names) CSV per project per language.
#     Output typically in build/projects/<lang>/<project>.csv
#     with format: <function name>, <names>
     
#     data/<lang>/** -> build/projects/<lang>/<project>.csv
#     """
#     parser = Parser()
#     parser.set_language(Language('build/parser_bindings.so', lang))

#     for directory in next(os.walk(indir))[1]:
#         out_file = os.path.join(output_dir, f'{directory}.csv')

#         with open(out_file, 'w', newline='', encoding='utf-8') as out_file:
#             writer = csv.writer(out_file)
#             console.print(f'Extracting to {out_file}...', style='bold red')

#             for file in list_files(f'data/{lang}/{directory}'):
#                 if 'README.md' in file or not is_ext_valid(file):
#                     continue

#                 try:
#                     console.print(file)
#                     fnames = extract(parser, file, globals()[f'extract_{lang}'])

#                     for fname, names in fnames.items():
#                         writer.writerow([fname, ' '.join(names)]) 
#                 except Exception as e: 
#                     print(e)
#                     pass
