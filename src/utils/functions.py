import json
import pandas as pd
import os

def mkdir_if_not_exists(default_save_path: str):
    if not os.path.exists(default_save_path):
        os.mkdir(default_save_path)

def write_json(arr, name):
    with open(f'{name}', 'w') as json_file:
        json_file.write(json.dumps(arr, indent=4))


def write_csv(dictionary, name):
    df = pd.DataFrame(dictionary)
    df.to_csv(f"{name}", index=False)
    print(df)

def convert_to_float(value):
    try:
        return float(value)
    except:
        return 0.0