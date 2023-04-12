import json
import pandas as pd

def write_json(arr, name):
    with open(f'{name}.json', 'w') as json_file:
        json_file.write(json.dumps(arr, indent=4))

def return_impedance(resistence, reactance):
    impedance_real = resistence/ ((resistence ** 2) + (reactance ** 2))
    impedance_imag = (reactance*(-1))/ ((resistence ** 2) + (reactance ** 2))
    return complex(impedance_real, impedance_imag)

def return_susceptance_shunt(value, base):
    try:
        return complex(0, (value/2*base))
    except:
        return complex(0, 0)

def return_transformer_relation(value, tap):
    return value*tap

def return_transformer_B(value, tap):
    return (tap * (tap - 1)) * value

def return_transformer_C(value, tap):
    return (1 - tap) * value

def return_capacitor(value, base, tension):
    return complex(0, (value/base) * tension)


def write_csv(dictionary, name):
    df = pd.DataFrame(dictionary)
    df.to_csv(f"{name}.csv", index=False)
    print(df)