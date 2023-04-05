class AnaredeDict:
    def __init__(self, DCTE, DBAR, DLIN):
        self.DCTE = DCTE
        self.DCTE_cols = {
            'name': (1, 4),
            'value': (5, 11)
        }
        self.DBAR = DBAR
        self.DBAR_cols = {
            'number': (0, 5),
            'operation': (5, 6),
            'state': (6, 7),
            'type': (7, 8),
            'tension_base_group': (8, 10),
            'name': (10, 21),
            'tension_limit_group': (22, 24),
            'tension': (22, 24),
        }
        self.DLIN = DLIN
    
        