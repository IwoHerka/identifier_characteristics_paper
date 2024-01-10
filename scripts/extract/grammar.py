import csv
import os
import re
import time
from multiprocessing import Process

import requests
from rich.console import Console

from db.engine import get_engine
from db.utils import (get_distinct_function_names_without_grammar,
                      init_local_session, update_function_grammar)

TAGGER_BASE_PORT = 5000
NUM_PROCESSES = 4

console = Console()


class Grammar:
    @staticmethod
    def extract():
        fn_names = get_distinct_function_names_without_grammar()
        processes = []

        for i in range(NUM_PROCESSES):
            chunk = Grammar._get_chunk(fn_names, i, NUM_PROCESSES)
            p = Process(target=Grammar._process, args=(chunk, TAGGER_BASE_PORT + i))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    @staticmethod
    def _get_grammar(name, port):
        """
        Make HTTP request to SCANL tagger to obtain grammar of a function name.
        """
        try:
            response = requests.get(f"http://localhost:{port}/{name}/FUNCTION")
            return ".".join(response.json())
        except Exception as e:
            console.print(e)
            return ""

    @staticmethod
    def _get_chunk(values, index, num_processes):
        chunk_size = len(values) // num_processes
        start = index * chunk_size

        # For the last chunk, ensure it includes any remaining elements
        if index == num_processes - 1:
            end = len(values)
        else:
            end = start + chunk_size

        return values[start:end]

    @staticmethod
    def _process(names, port):
        session = init_local_session()
        last_commit_time = time.time()

        for i, oname in enumerate(names):
            oname = oname[0]

            if oname:
                name = re.sub(r"[^\w-]", "", oname)
                name = re.sub(r"\d+$", "", name)
                if name and len(name) > 1 and "test" not in name:
                    grammar = Grammar._get_grammar(name, port)
                    console.print(f"{oname} : {name} -> {grammar}")
                    update_function_grammar(session, oname, grammar)

            if i % 50 == 0:
                session.commit()
                current_time = time.time()
                elapsed_time = current_time - last_commit_time
                console.print(
                    f"Commit completed. Time elapsed since last commit: {elapsed_time:.2f} seconds"
                )
                last_commit_time = current_time
