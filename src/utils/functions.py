import json
import pandas as pd

def write_json(arr, name):
    with open(f'{name}.json', 'w') as json_file:
        json_file.write(json.dumps(arr, indent=4))

def write_csv(dictionary, name):
    df = pd.DataFrame(dictionary)
    df.to_csv(f"{name}.csv", index=False)
    print(df)