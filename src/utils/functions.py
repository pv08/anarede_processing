import json

def write_json(arr, name):
    with open(f'{name}.json', 'w') as json_file:
        json_file.write(json.dumps(arr, indent=4))
