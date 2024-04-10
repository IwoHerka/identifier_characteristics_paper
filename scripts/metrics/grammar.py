import requests



def get_grammar(name):
    response = requests.get(f'http://localhost:5000/{name}/FUNCTION')
    return '.'.join(response.json())
