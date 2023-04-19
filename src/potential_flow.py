import numpy as np
from src.utils.functions import convert_to_float
from numpy import cos, sin

class PotentialFlow:
    def __init__(self, DCTE, DLIN, DBAR, y_bus):
        self.DCTE = DCTE
        self.DLIN = DLIN
        self.DBAR = DBAR
        self.y_bus = y_bus
        self.sys_data = {}
        self.convergence = []
        self.potential_flow()



        #TODO{1º - Montar o número de equações e icognitas pelo DBAR e printar (ex: 2NPQ + NPV)}






    @staticmethod
    def is_linked(b, g):
        if g == 0 and b == 0:
            return False
        return True
    @staticmethod
    def return_value_pu(value, base):
        return value/base


    def calc_potential(self, k, V_k, O_k, active=True):
        potential_calc = 0.0
        for bar, idx in zip(self.sys_data.keys(), range(0, len(self.sys_data))):
            V_m = self.sys_data[bar]['V']
            G_km = self.y_bus[k][idx].real
            B_km = self.y_bus[k][idx].imag
            O = O_k - self.sys_data[bar]['O']
            if active:
                potential_calc += V_m * ((G_km * cos(O)) + (B_km * sin(O)))

            else:
                potential_calc += V_m * ((G_km * sin(O)) - (B_km * cos(O)))
        potential_calc *= V_k
        return potential_calc

    def not_converged(self):
        if (max(abs(self.dPs)) > (self.DCTE[0]['value']/100)) or (max(abs(self.dQs)) > (self.DCTE[1]['value']/100)):
            return True
        else:
            return False

    def potential_flow(self):
        #inicia os valores
        self.make_initial_data()
        #define P e Q and dP e dQ
        self.make_d()
        h = 0

        while self.not_converged():
            self.convergence.append({
                'iter': h,
                'convP': max(abs(self.dPs)),
                'P_bus': np.argmax(abs(self.dPs)),
                'convQ': max(abs(self.dQs)),
                'Q_bus': np.argmax(abs(self.dQs))
            })
            jacobiana = self.find_jacobiana_matrix()

            iteration_state = np.linalg.solve(jacobiana, self.dPQY)
            O_values = iteration_state[: len(self.sys_data.keys())]
            V_values = iteration_state[len(self.sys_data.keys()):]

            for bar in self.sys_data.keys():
                self.sys_data[bar]['O'] += O_values[bar]

            for bar in self.sys_data.keys():
                self.sys_data[bar]['V'] += V_values[bar]

            self.make_d()

            h += 1

        self.convergence.append({
            'iter': h,
            'convP': max(abs(self.dPs)),
            'P_bus': np.argmax(abs(self.dPs)),
            'convQ': max(abs(self.dQs)),
            'Q_bus': np.argmax(abs(self.dQs))
        })
        jacobiana = self.find_jacobiana_matrix()

        iteration_state = np.linalg.solve(jacobiana, self.dPQY)
        O_values = iteration_state[: len(self.sys_data.keys())]
        V_values = iteration_state[len(self.sys_data.keys()):]

        for bar in self.sys_data.keys():
            self.sys_data[bar]['O'] += O_values[bar]

        for bar in self.sys_data.keys():
            self.sys_data[bar]['V'] += V_values[bar]

        self.make_d()


        print(h, self.sys_data)


    def make_initial_data(self):
        for bar, idx in zip(self.DBAR, range(0, len(self.DBAR))):
            #load PQ
            P_g = self.return_value_pu(convert_to_float(value=bar.get('active_generation')), base=100) #potencia at gerada
            P_d = self.return_value_pu(convert_to_float(value=bar.get('active_load')), base=100) #potencia at demandada
            P_esp = P_g - P_d
            # P_calc = self.calc_potential(k=idx, V_k=1.0, O_k=0.0)
            # dP = P_esp - P_calc

            Q_g = self.return_value_pu(value=convert_to_float(bar.get('reactive_generation')), base=100) #potencia re gerada
            Q_d = self.return_value_pu(value=convert_to_float(bar.get('reactive_load')), base=100) #potencia re gerada
            Q_esp = Q_g - Q_d
            # Q_calc = self.calc_potential(k=idx, V_k=1.0, O_k=0.0, active=False)
            # dQ = Q_esp - Q_calc

            self.sys_data[idx] = {
                "P": P_esp,
                "Q": Q_esp,
                "V": bar['tension']/1000,
                "O": 0.0,
                "dP": 0.0,
                "dQ": 0.0
            }

            if bar['type'] != 2:
                if bar['type'] == 3 or type(bar['type']) is str:
                    self.sys_data[idx]['type'] = 'PQ'
                else:
                    self.sys_data[idx]['type'] = 'PV'
            else:
                self.sys_data[idx]['O'] = np.radians(bar['angle'])
                self.sys_data[idx]['type'] = 'VO'

    def make_d(self):
        for bar, idx in zip(self.DBAR, range(0, len(self.DBAR))):
            if bar['type'] != 2:
                P_calc = self.calc_potential(k=idx, V_k=self.sys_data[idx]['V'], O_k=self.sys_data[idx]['O'])
                self.sys_data[idx]['dP'] = self.sys_data[idx]['P'] - P_calc
                # self.sys_data[idx]['P'] = (P_calc * 100) + bar['active_load']
            if type(bar['type']) is str or bar['type'] == 3:
                Q_calc = self.calc_potential(k=idx, V_k=self.sys_data[idx]['V'], O_k=self.sys_data[idx]['O'], active=False)
                self.sys_data[idx]['dQ'] = self.sys_data[idx]['Q'] - Q_calc
        self.dPs = np.array([self.sys_data[value]['dP']for value in self.sys_data.keys()])
        self.dQs = np.array([self.sys_data[value]['dQ'] for value in self.sys_data.keys()])
        self.dPQY = np.concatenate((self.dPs, self.dQs))


    def define_H(self, k, m):
        V_k = self.sys_data[k]['V']
        V_m = self.sys_data[m]['V']
        G_km = self.y_bus[k][m].real
        B_km = self.y_bus[k][m].imag
        O_km = self.sys_data[k]['O'] - self.sys_data[m]['O']
        if k != m:
            H_km = V_k * V_m * ((G_km * sin(O_km)) - (B_km * cos(O_km)))
            return H_km
        B_kk = self.y_bus[k][k].imag
        H_kk = ((-(V_k ** 2) * B_kk) - self.calc_potential(k, V_k, self.sys_data[k]['O'], active=False))
        return H_kk
    def define_N(self, k, m):
        V_k = self.sys_data[k]['V']
        V_m = self.sys_data[m]['V']
        G_km = self.y_bus[k][m].real
        B_km = self.y_bus[k][m].imag
        O_km = self.sys_data[k]['O'] - self.sys_data[m]['O']
        if k != m:
            N_km = V_m * ((G_km * cos(O_km)) + (B_km * sin(O_km)))
            return N_km
        G_kk = self.y_bus[k][k].real
        N_kk = (self.calc_potential(k, V_k, self.sys_data[k]['O']) + ((V_k ** 2) * G_kk)) / V_k
        return N_kk
    def define_M(self, k, m):
        V_k = self.sys_data[k]['V']
        V_m = self.sys_data[m]['V']
        G_km = self.y_bus[k][m].real
        B_km = self.y_bus[k][m].imag
        O_km = self.sys_data[k]['O'] - self.sys_data[m]['O']
        if k != m:
            M_km = -V_k * V_m * ((G_km * cos(O_km)) + (B_km * sin(O_km)))
            return M_km
        G_kk = self.y_bus[k][k].real
        M_kk = self.calc_potential(k, V_k, self.sys_data[k]['O']) - ((V_k ** 2) * G_kk)
        return M_kk
    def define_L(self, k, m):
        V_k = self.sys_data[k]['V']
        V_m = self.sys_data[m]['V']
        G_km = self.y_bus[k][m].real
        B_km = self.y_bus[k][m].imag
        O_km = self.sys_data[k]['O'] - self.sys_data[m]['O']
        if k != m:
            L_km = V_k * ((G_km * sin(O_km)) - (B_km * cos(O_km)))
            return L_km
        B_kk = self.y_bus[k][k].imag
        L_kk = (self.calc_potential(k, V_k, self.sys_data[k]['O'], active=False) - ((V_k ** 2) * B_kk)) / V_k
        return L_kk

    def find_jacobiana_matrix(self):
        dp_dO = np.ones([len(self.sys_data.keys()), len(self.sys_data.keys())])
        dp_dv = np.ones([len(self.sys_data.keys()), len(self.sys_data.keys())])
        dq_dO = np.ones([len(self.sys_data.keys()), len(self.sys_data.keys())])
        dq_dv = np.ones([len(self.sys_data.keys()), len(self.sys_data.keys())])

        for k in range(0, len(self.sys_data.keys())):
            for m in range(0, len(self.sys_data.keys())):
                dp_dO[k, m] = self.define_H(k=k, m=m)
                dp_dv[k, m] = self.define_N(k=k, m=m)
                dq_dO[k, m] = self.define_M(k=k, m=m)
                dq_dv[k, m] = self.define_L(k=k, m=m)
        PQs = [True if self.sys_data[i]['type'] == 'PQ' else False for i in self.sys_data.keys()]
        PVs = [True if self.sys_data[i]['type'] != 'VO' else False for i in self.sys_data.keys()]
        for i, is_Q, is_P in zip(range(0, len(self.sys_data.keys())), PQs, PVs):
            if not is_P:
                dp_dv[i, :] = 0
                dp_dO[i, :] = 0
                dp_dO[:, i] = 0
                dp_dO[i, i] = 1
                dq_dO[:, i] = 0


            if not is_Q:
                dq_dv[i, :] = 0
                dq_dv[:, i] = 0
                dq_dv[i, i] = 1
                dq_dO[i, :] = 0
                dp_dv[:, i] = 0

        # [H    N]
        # [M    L]
        HM = np.concatenate( (dp_dO, dq_dO), axis= 0)
        NL = np.concatenate((dp_dv, dq_dv), axis=0)
        jacobiana = np.concatenate((HM, NL), axis=1)
        return jacobiana


