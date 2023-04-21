import json
import pandas as pd
import os
import matplotlib.pyplot as plt
def mkdir_if_not_exists(default_save_path: str):
    if not os.path.exists(default_save_path):
        os.mkdir(default_save_path)

def write_json(arr, name):
    with open(f'{name}', 'w') as json_file:
        json_file.write(json.dumps(arr, indent=4))


def write_csv(dictionary, name):
    df = pd.DataFrame(dictionary)
    df.to_csv(f"{name}", index=False)

def convert_to_float(value):
    try:
        return float(value)
    except:
        return 0.0

def plot_convergence(x_arr, p_arr, q_arr, save_plots=True, plt_types=['.eps']):
    mkdir_if_not_exists('results/figs/')
    p_value = list(zip(*p_arr))
    q_value = list(zip(*q_arr))
    plt.figure(figsize=(8, 8))
    plt.title('Evolução dos erros de potência')
    plt.plot(x_arr, p_value[0], '-o', label='Erro pot. ativa')
    plt.plot(x_arr, q_value[0], '-^', label='Erro pot. reativa')
    for p_bar, q_bar, x in zip(p_arr, q_arr, x_arr):
        style = dict(size=10, color='gray')
        plt.text(x, p_bar[0], f'PBar: {p_bar[1]}', **style)
        plt.text(x, q_bar[0]+0.35, f'QBar: {q_bar[1]}', **style)

    plt.xlabel('Iterações')
    plt.ylabel('Potência (p.u)')
    plt.legend()
    if save_plots:
        for types in plt_types:
            plt.savefig(f'results/figs/convergence{types}', dpi=600, bbox_inches='tight')
    plt.show()
    plt.close()
