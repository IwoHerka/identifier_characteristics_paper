import os
from exts import get_exts



lang = 'elixir'
exts = set(get_exts(lang))
directory_path = f"data/{lang}"
extensions = delete_all(directory_path, exts)
