import argparse
from src.anarede import Anarede
from src.utils.ana_dict import AnaredeDict
from src.utils.functions import write_json, write_csv

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--file', type=str, default='data/file.pwf')
    args = args.parse_args()
    anarede = Anarede(args=args)
    ana_dict = AnaredeDict(DCTE=anarede.keywords['DCTE'], DBAR=anarede.keywords['DBAR'], DLIN=anarede.keywords['DLIN'])
    ana_dict.convertRecords()
    write_json(ana_dict.convertedDCTE, 'DCTE')
    write_json(ana_dict.convertedDBAR, 'DBAR')
    write_json(ana_dict.convertedDLIN, 'DLIN')

    matrix = {i:  [complex(round(0, 4), round(0, 4)) for j in range(0, len(ana_dict.convertedDBAR))] for i in range(0, len(ana_dict.convertedDBAR))}
    change = ana_dict.convertedDLIN[0].get('from') - 1
    soma_real = 0
    soma_img = 0
    for record in ana_dict.convertedDLIN:
        get_from = record.get('from') - 1
        get_to = record.get('to') - 1
        resistence = record.get('resistence')/100
        reactance = record.get('reactance')/100
        impedance_real = resistence/ ((resistence ** 2) + (reactance ** 2))
        impedance_imag = (reactance*(-1))/ ((resistence ** 2) + (reactance ** 2))
        matrix[get_from][get_to] = complex(round(impedance_real, 4), round(impedance_imag, 4)) * (-1)
        matrix[get_to][get_from] = complex(round(impedance_real, 4), round(impedance_imag, 4)) * (-1)
        
        if get_from != change:
            matrix[change][change] = complex(round(soma_real, 4), round(soma_img, 4))
            change = get_from
            soma_real = 0
            soma_img = 0

        soma_real += impedance_real
        soma_img += impedance_imag
    for bar in matrix.keys():
        print(f"{bar}: {matrix[bar]}")
    write_csv(matrix, 'y_barra')
if __name__ == "__main__":
    main()