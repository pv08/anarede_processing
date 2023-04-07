
class Anarede:
    def __init__(self, args):
        self.args = args
        self.file = args.file
        self.line_breaker = '99999'
        self.assign_value = {'TITU': False, 'DCTE':False,  'DBAR':False, 'DLIN':False}
        self.keywords = {'TITU': '', 'DCTE':[],  'DBAR':[], 'DLIN':[]}
        self.makeDatabase()
        
        
    
    def makeDatabase(self):
        file = open(self.file, 'r')
        for line in file:
            value = line
            keyword = line.rstrip()
            print(line, end='')
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
        