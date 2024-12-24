import csv
import os
from multiprocessing import Process

import requests
from rich.console import Console
import re

from db.engine import get_engine
from db.utils import (
    get_distinct_function_names_without_grammar,
    update_function_grammar,
    init_local_session
)

TAGGER_BASE_PORT = 5000
NUM_PROCESSES = 4

console = Console()


class Grammar:
    @staticmethod
    def extract():
        fn_names = get_distinct_function_names_without_grammar()
        processes = []

        for i in range(NUM_PROCESSES):
            chunk = Grammar.__get_chunk(fn_names, i, NUM_PROCESSES)
            p = Process(target=Grammar.__process, args=(chunk, TAGGER_BASE_PORT + i))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    @staticmethod
    def __get_grammar(name, port):
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
    def __get_chunk(values, index, num_processes):
        chunk_size = len(values) // num_processes
        start = index * chunk_size

        # For the last chunk, ensure it includes any remaining elements
        if index == num_processes - 1:
            end = len(values)
        else:
            end = start + chunk_size

        return values[start:end]

    @staticmethod
    def __process(names, port):
        session = init_local_session()

        try:
            for i, name in enumerate(names):
                name = re.sub(r'[^\w-]', '', name)
                name = re.sub(r'\d+$', '', name)
                if name != '':
                    grammar = Grammar.__get_grammar(name, port)
                    console.print(f"'{name}' -> {grammar}")
                    update_function_grammar(session, name, grammar)
        except Exception as e:
            console.print(e)
        finally:
            session.close()