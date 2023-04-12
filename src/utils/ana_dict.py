
class AnaredeDict:
    def __init__(self):
        
        self.DCTE_cols = {
            'name': {'ref':(0, 4), 'type': str},
            'value': {'ref': (5, 11), 'type': float}
        }
        self.DBAR_cols = {
            'number': {'ref': (0, 5), 'type': int},
            'operation': {'ref': (5, 6), 'type': str},
            'state': {'ref': (6, 7), 'type': str},
            'type': {'ref': (7, 8), 'type': int},
            'tension_base_group': {'ref': (8, 10), 'type': int},
            'name': {'ref': (10, 21), 'type': str},
            'tension_limit_group': {'ref': (22, 24), 'type': int},
            'tension': {'ref': (24, 28), 'type': float},
            'angle': {'ref': (28, 32), 'type': float},
            'active_generation': {'ref': (32, 37), 'type': float},
            'reactive_generation': {'ref': (37, 42), 'type': float},
            'reactive_generation_n': {'ref': (42, 47), 'type': float},
            'reactive_generation_m': {'ref': (47, 52), 'type': float},
            'control_bar': {'ref': (52, 58), 'type': str},
            'active_load': {'ref': (58, 63), 'type': float},
            'reactive_load': {'ref': (63, 68), 'type': float},
            'capacitor': {'ref': (68, 73), 'type': float},
            'area': {'ref': (73, 76), 'type': float},
            'definition_tension': {'ref': (76, 80), 'type': float}
        }
        
        self.DLIN_cols = {
            'from': {'ref': (0, 5), 'type': int},
            'state_from': {'ref': (5, 6), 'type': str},
            'operation': {'ref': (6, 8), 'type': str},
            'state_to': {'ref': (8, 10), 'type': str},
            'to': {'ref': (10, 15), 'type': int},
            'circuit': {'ref': (15, 17), 'type': int},
            'state': {'ref': (17, 18), 'type': str},
            'owner': {'ref': (18, 19), 'type': str},
            'manageable': {'ref': (19, 20), 'type': str},
            'resistence': {'ref': (20, 26), 'type': float},
            'reactance': {'ref': (26, 32), 'type': float},
            'susceptance': {'ref': (32, 38), 'type': float},
            'tap': {'ref': (38, 43), 'type': float},
            'min_tap': {'ref': (43, 48), 'type': float},
            'max_tap': {'ref': (48, 53), 'type': float},
            'lag': {'ref': (53, 58), 'type': float}
        }
           

    
    
    @staticmethod
    def catchValues(record, reference):
        arr = []
        for idx, value in zip(range(0, len(record)), record):
            if idx == 0:
                continue
            data = {}
            for key, ref in zip(reference.keys(), reference.values()):
                start, final = ref['ref']
                typ = ref['type']
                
                try:
                    if typ == str:
                        data[key] = typ(value[start: final].strip())
                    else:
                        data[key] = typ(value[start: final])
                except:
                    data[key] = value[start: final]
            arr.append(data)
        return arr

        