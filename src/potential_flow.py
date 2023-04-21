import numpy as np
import math
from src.utils.functions import convert_to_float, write_json, write_csv, mkdir_if_not_exists, plot_convergence
from numpy import cos, sin

class PotentialFlow:
    def __init__(self, DCTE, DLIN, DBAR, y_bus, max_iter):
        self.DCTE = DCTE
        self.DLIN = DLIN
        self.DBAR = DBAR
        self.y_bus = y_bus
        self.max_iter = max_iter
        self.sys_data = {}
        self.convergence = []
        print("*************** PowerFlow ******************")
        self.potential_flow()
        mkdir_if_not_exists('results/potential_flow')
        print("[!] - Bar's final data exported to 'results/potential_flow/bars_final_data.json'")
        write_json(self.sys_data, 'results/potential_flow/bars_final_data.json')
        string = ""
        for bar in self.sys_data.keys():
            string += str(bar + 1) + " & " + self.sys_data[bar]['type'] + " & "
            string += str(round(self.sys_data[bar]['V'], 4)) + r" \angle " + str(round(math.degrees(self.sys_data[bar]['O']), 2)) + "º & "
            string += str(round(self.sys_data[bar]['P'] * 100, 2)) + " & " + str(round(self.sys_data[bar]['Q'] * 100, 2)) + r" \\ "
            string += "\n"
        print(string)
        write_csv(self.convergence, 'results/potential_flow/convergence_report.csv')
        print("[!] - Convergence report exported to 'results/potential_flow/convergence_report.csv'")

        iteration_arr = [value['iter'] for value in self.convergence]
        P_arr = [(value['convP'], value['P_bus']) for value in self.convergence]
        Q_arr = [(value['convQ'], value['Q_bus']) for value in self.convergence]
        plot_convergence(iteration_arr, P_arr, Q_arr)


    @staticmethod
    def return_value_pu(value, base):
        return value/base

    def update_O_V(self, O_arr, V_arr):
        for bar in self.sys_data.keys():
            self.sys_data[bar]['O'] += O_arr[bar]

        for bar in self.sys_data.keys():
            self.sys_data[bar]['V'] += V_arr[bar]

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
        PQs = [True if self.sys_data[i]['type'] == 'PQ' else False for i in self.sys_data.keys()]
        PVs = [True if self.sys_data[i]['type'] != 'VO' else False for i in self.sys_data.keys()]

        print(f"[!] - {PQs.count(True)}NPQ + {PVs.count(True)}NPV = {2*PQs.count(True)}")
        #define P e Q and dP e dQ
        self.make_d()
        h = 0

        while self.not_converged():
            iteration = {
                'iter': h,
                'convP': max(abs(self.dPs)),
                'P_bus': np.argmax(abs(self.dPs)),
                'convQ': max(abs(self.dQs)),
                'Q_bus': np.argmax(abs(self.dQs))
            }
            print(f"[*] - iteration: {iteration['iter']} | P_Bar[Num - {iteration['P_bus'] + 1}]: {iteration['convP']*100} MW | Q_Bar[Num - {iteration['Q_bus'] + 1}]: {iteration['convQ']*100} MVAr")
            self.convergence.append(iteration)

            jacobiana = self.find_jacobiana_matrix()

            iteration_state = np.linalg.solve(jacobiana, self.dPQY)
            O_values = iteration_state[: len(self.sys_data.keys())]
            V_values = iteration_state[len(self.sys_data.keys()):]

            self.update_O_V(O_arr=O_values, V_arr=V_values)

            self.make_d()

            h += 1

            if h >= self.max_iter:
                raise EOFError("*************** Divergent System ******************")

        iteration = {
            'iter': h,
            'convP': max(abs(self.dPs)),
            'P_bus': np.argmax(abs(self.dPs)),
            'convQ': max(abs(self.dQs)),
            'Q_bus': np.argmax(abs(self.dQs))
        }
        print(
            f"[*] - iteration: {iteration['iter']} | P_Bar[Num - {iteration['P_bus'] + 1}]: {iteration['convP'] * 100} MW | Q_Bar[Num - {iteration['Q_bus'] + 1}]: {iteration['convQ'] * 100} MVAr")
        self.convergence.append(iteration)
        jacobiana = self.find_jacobiana_matrix()

        iteration_state = np.linalg.solve(jacobiana, self.dPQY)
        O_values = iteration_state[: len(self.sys_data.keys())]
        V_values = iteration_state[len(self.sys_data.keys()):]

        self.update_O_V(O_arr=O_values, V_arr=V_values)

        self.make_d()


        print("*************** Converged System ******************")



    def make_initial_data(self):
        for bar, idx in zip(self.DBAR, range(0, len(self.DBAR))):
            #load PQ
            P_g = self.return_value_pu(value=convert_to_float(value=bar.get('active_generation')), base=100) #potencia at gerada
            P_d = self.return_value_pu(value=convert_to_float(value=bar.get('active_load')), base=100) #potencia at demandada
            P_esp = P_g - P_d

            Q_g = self.return_value_pu(value=convert_to_float(value=bar.get('reactive_generation')), base=100) #potencia re gerada
            Q_d = self.return_value_pu(value=convert_to_float(value=bar.get('reactive_load')), base=100) #potencia re gerada
            Q_esp = Q_g - Q_d

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
        self.dPs = np.array([self.sys_data[value]['dP'] for value in self.sys_data.keys()])
        self.dQs = np.array([self.sys_data[value]['dQ'] for value in self.sys_data.keys()])
        self.dPQY = np.concatenate((self.dPs, self.dQs))




    def return_base_comp(self, k, m):
        V_k = self.sys_data[k]['V']
        V_m = self.sys_data[m]['V']
        G_km = self.y_bus[k][m].real
        B_km = self.y_bus[k][m].imag
        O_km = self.sys_data[k]['O'] - self.sys_data[m]['O']
        return V_k, V_m, G_km, B_km, O_km


    def define_H(self, k, m):
        V_k, V_m, G_km, B_km, O_km = self.return_base_comp(k, m)
        if k != m:
            H_km = V_k * V_m * ((G_km * sin(O_km)) - (B_km * cos(O_km)))
            return H_km
        B_kk = self.y_bus[k][k].imag
        H_kk = ((-(V_k ** 2) * B_kk) - self.calc_potential(k, V_k, self.sys_data[k]['O'], active=False))
        return H_kk
    def define_N(self, k, m):
        V_k, V_m, G_km, B_km, O_km = self.return_base_comp(k, m)
        if k != m:
            N_km = V_m * ((G_km * cos(O_km)) + (B_km * sin(O_km)))
            return N_km
        G_kk = self.y_bus[k][k].real
        N_kk = (self.calc_potential(k, V_k, self.sys_data[k]['O']) + ((V_k ** 2) * G_kk)) / V_k
        return N_kk
    def define_M(self, k, m):
        V_k, V_m, G_km, B_km, O_km = self.return_base_comp(k, m)
        if k != m:
            M_km = -V_k * V_m * ((G_km * cos(O_km)) + (B_km * sin(O_km)))
            return M_km
        G_kk = self.y_bus[k][k].real
        M_kk = self.calc_potential(k, V_k, self.sys_data[k]['O']) - ((V_k ** 2) * G_kk)
        return M_kk
    def define_L(self, k, m):
        V_k, V_m, G_km, B_km, O_km = self.return_base_comp(k, m)
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


