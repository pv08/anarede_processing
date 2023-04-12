import argparse
from src.anarede import Anarede
from src.utils.ana_dict import AnaredeDict
from src.utils.functions import *

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

    matrix = {i:  [complex(0, 0) for j in range(0, len(ana_dict.convertedDBAR))] for i in range(0, len(ana_dict.convertedDBAR))}

    for record in ana_dict.convertedDLIN:
        get_from = record.get('from') - 1
        get_to = record.get('to') - 1
        resistence = record.get('resistence')/100
        reactance = record.get('reactance')/100

        impedance = return_impedance(resistence=resistence, reactance=reactance)
        
        if type(record.get('tap')) == float: #has a transformer
            impedance = return_transformer_relation(value=impedance, tap=record.get('tap'))
            matrix[get_from][get_to] += impedance * (-1)
            matrix[get_to][get_from] += impedance * (-1)
            
        else:
            matrix[get_from][get_to] += impedance * (-1)
            matrix[get_to][get_from] += impedance * (-1)

    
    for line, bar in zip(matrix.keys(), ana_dict.convertedDBAR):
        if type(bar.get('capacitor')) == float:
            capacitance = return_capacitor(value=bar.get('capacitor'), base=100, tension=bar.get('tension'))
            matrix[line][line] = (sum(matrix[line]) * (-1)) + capacitance
        else:
            matrix[line][line] = sum(matrix[line]) * (-1)
        for record in ana_dict.convertedDLIN:
            get_from = record.get('from') - 1
            get_to = record.get('to') - 1

            resistence = record.get('resistence')/100
            reactance = record.get('reactance')/100
            
            susceptance = return_susceptance_shunt(value=record.get('susceptance'), base=100)
            impedance = return_impedance(resistence=resistence, reactance=reactance)

            if type(record.get('tap')) == float:
                if line == get_from:
                    B = return_transformer_B(value=impedance, tap=record.get('tap'))
                    matrix[line][line] += susceptance + B
                if line == get_to:
                    C = return_transformer_C(value=impedance, tap=record.get('tap'))
                    matrix[line][line] += susceptance + C
            else:
                if line == get_from or line == get_to:
                    matrix[line][line] += susceptance

    write_csv(matrix, 'y_barra')
        
        
if __name__ == "__main__":
    main()