import numpy as np
from src.utils.functions import mkdir_if_not_exists, write_csv

class YBus:
    def __init__(self, DBAR, DLIN):
        self.DBAR = DBAR
        self.DLIN = DLIN
        self.y_bus = np.zeros((len(self.DBAR), len(self.DBAR)), dtype=complex)
        self.create_triangular_admitance()
        self.create_principal_diagonal()

        mkdir_if_not_exists('results/')
        print("*************** Y_BUS ******************")
        write_csv(self.y_bus, 'results/y_bus.csv')
        print("[!] - Y_Bus saved on the 'results/y_bus.csv'")

    @staticmethod
    def return_admitance(resistence, reactance):
        admitance_real = resistence/ ((resistence ** 2) + (reactance ** 2))
        admitance_imag = (reactance*(-1))/ ((resistence ** 2) + (reactance ** 2))
        return complex(admitance_real, admitance_imag)

    @staticmethod
    def return_susceptance_shunt(value, base):
        try:
            return complex(0, (value/(2*base)))
        except:
            return complex(0, 0)

    @staticmethod
    def return_transformer_relation(value, tap):
        return value*tap

    @staticmethod
    def return_transformer_B(value, tap):
        return (tap * (tap - 1)) * value

    @staticmethod
    def return_transformer_C(value, tap):
        return (1 - tap) * value

    @staticmethod
    def return_capacitor(value, base, tension):
        return complex(0, (value/base) * tension)


    def create_triangular_admitance(self):
        for record in self.DLIN:
            get_from = record.get('from') - 1
            get_to = record.get('to') - 1
            resistence = record.get('resistence') / 100
            reactance = record.get('reactance') / 100

            admitance = self.return_admitance(resistence=resistence, reactance=reactance)

            if type(record.get('tap')) == float:  # has a transformer
                admitance = self.return_transformer_relation(value=admitance, tap=1/record.get('tap'))
                self.y_bus[get_from][get_to] += admitance * (-1)
                self.y_bus[get_to][get_from] += admitance * (-1)

            else:
                self.y_bus[get_from][get_to] += admitance * (-1)
                self.y_bus[get_to][get_from] += admitance * (-1)

    def create_principal_diagonal(self):
        for line, bar in zip(range(0, len(self.y_bus)), self.DBAR):
            if type(bar.get('capacitor')) == float:
                capacitance = self.return_capacitor(value=bar.get('capacitor'), base=100, tension=bar.get(
                    'tension')/1000)
                self.y_bus[line][line] = (sum(self.y_bus[line]) * (-1)) + capacitance
            else:
                self.y_bus[line][line] = sum(self.y_bus[line]) * (-1)
            for record in self.DLIN:
                get_from = record.get('from') - 1
                get_to = record.get('to') - 1

                resistence = record.get('resistence') / 100
                reactance = record.get('reactance') / 100

                susceptance = self.return_susceptance_shunt(value=record.get('susceptance'), base=100)
                admitance = self.return_admitance(resistence=resistence, reactance=reactance)

                if type(record.get('tap')) == float:
                    if line == get_from:
                        B = self.return_transformer_B(value=admitance, tap=1/record.get('tap'))
                        self.y_bus[line][line] += susceptance + B
                    if line == get_to:
                        C = self.return_transformer_C(value=admitance, tap=1/record.get('tap'))
                        self.y_bus[line][line] += susceptance + C
                else:
                    if line == get_from or line == get_to:
                        self.y_bus[line][line] += susceptance

