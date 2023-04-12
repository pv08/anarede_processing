import os
from src.utils.ana_dict import AnaredeDict
from src.utils.functions import mkdir_if_not_exists, write_json

class Anarede(AnaredeDict):
    def __init__(self, args):
        super(Anarede, self).__init__()
        self.args = args
        self.file = args.file
        self.line_breaker = '99999'
        self.assign_value = {'TITU': False, 'DCTE':False,  'DBAR':False, 'DLIN':False}
        self.keywords = {'TITU': '', 'DCTE':[],  'DBAR':[], 'DLIN':[]}
        print(f"[!] - Importing .pwf file...")
        self.makeDatabase()
        mkdir_if_not_exists('etc/')
        self.DCTE = self.catchValues(self.keywords['DCTE'], self.DCTE_cols)
        write_json(self.DCTE, 'etc/DCTE.json')
        print(f"[+] - DCTE exported on etc/DCTE.json")
        self.DBAR = self.catchValues(self.keywords['DBAR'], self.DBAR_cols)
        write_json(self.DBAR, 'etc/DBAR.json')
        print(f"[+] - DBAR exported on etc/DBAR.json")
        self.DLIN = self.catchValues(self.keywords['DLIN'], self.DLIN_cols)
        write_json(self.DLIN, 'etc/DLIN.json')
        print(f"[+] - DLIN exported on etc/DLIN.json")

        self.y_bus = {i:  [complex(0, 0) for j in range(0, len(self.DBAR))] for i in range(0, len(self.DBAR))}
        self.create_triangular_impedances()
        self.create_principal_diagonal()
            

    @staticmethod
    def return_impedance(resistence, reactance):
        impedance_real = resistence/ ((resistence ** 2) + (reactance ** 2))
        impedance_imag = (reactance*(-1))/ ((resistence ** 2) + (reactance ** 2))
        return complex(impedance_real, impedance_imag)

    @staticmethod
    def return_susceptance_shunt(value, base):
        try:
            return complex(0, (value/2*base))
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

        
    
    def makeDatabase(self):
        file = open(self.file, 'r')
        for line in file:
            value = line
            keyword = line.rstrip()
            if self.assign_value['TITU']:
                self.keywords['TITU'] = keyword
                self.assign_value['TITU'] = False
            
            if self.assign_value['DCTE'] and keyword != self.line_breaker:
                self.keywords['DCTE'] += [value]
            else:
                self.assign_value['DCTE'] = False

            if self.assign_value['DBAR'] and keyword != self.line_breaker:
                self.keywords['DBAR'] += [value]
            else:
                self.assign_value['DBAR'] = False

            if self.assign_value['DLIN'] and keyword != self.line_breaker:
                self.keywords['DLIN'] += [value]
            else:
                self.assign_value['DLIN'] = False

            if keyword in self.keywords.keys():
                self.assign_value[keyword] = True            
    
    def create_triangular_impedances(self):
        for record in self.DLIN:
            get_from = record.get('from') - 1
            get_to = record.get('to') - 1
            resistence = record.get('resistence')/100
            reactance = record.get('reactance')/100

            impedance = self.return_impedance(resistence=resistence, reactance=reactance)
            
            if type(record.get('tap')) == float: #has a transformer
                impedance = self.return_transformer_relation(value=impedance, tap=record.get('tap'))
                self.y_bus[get_from][get_to] += impedance * (-1)
                self.y_bus[get_to][get_from] += impedance * (-1)
                
            else:
                self.y_bus[get_from][get_to] += impedance * (-1)
                self.y_bus[get_to][get_from] += impedance * (-1)
    
    def create_principal_diagonal(self):
        for line, bar in zip(self.y_bus.keys(), self.DBAR):
            if type(bar.get('capacitor')) == float:
                capacitance = self.return_capacitor(value=bar.get('capacitor'), base=100, tension=bar.get('tension'))
                self.y_bus[line][line] = (sum(self.y_bus[line]) * (-1)) + capacitance
            else:
                self.y_bus[line][line] = sum(self.y_bus[line]) * (-1)
            for record in self.DLIN:
                get_from = record.get('from') - 1
                get_to = record.get('to') - 1

                resistence = record.get('resistence')/100
                reactance = record.get('reactance')/100
                
                susceptance = self.return_susceptance_shunt(value=record.get('susceptance'), base=100)
                impedance = self.return_impedance(resistence=resistence, reactance=reactance)

                if type(record.get('tap')) == float:
                    if line == get_from:
                        B = self.return_transformer_B(value=impedance, tap=record.get('tap'))
                        self.y_bus[line][line] += susceptance + B
                    if line == get_to:
                        C = self.return_transformer_C(value=impedance, tap=record.get('tap'))
                        self.y_bus[line][line] += susceptance + C
                else:
                    if line == get_from or line == get_to:
                        self.y_bus[line][line] += susceptance

