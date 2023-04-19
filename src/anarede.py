import os
from src.utils.ana_dict import AnaredeDict
from src.y_bus import YBus
from src.potential_flow import PotentialFlow
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

        self.y_bus = YBus(DBAR=self.DBAR, DLIN=self.DLIN)
        potential = PotentialFlow(DCTE=self.DCTE, DLIN=self.DLIN, DBAR=self.DBAR, y_bus=self.y_bus.y_bus)



    
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
    
