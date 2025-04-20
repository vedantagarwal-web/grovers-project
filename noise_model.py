"""
Open‑system model used by Pokharel & Lidar.
Combines amplitude‑damping, phase‑damping and depolarisation.
"""

import numpy as np
from qiskit_aer.noise import NoiseModel, amplitude_damping_error, \
                              phase_damping_error, depolarizing_error

def build_noise(t1=80e3, t2=60e3, gate_us=0.05,
                dep1=5e-4, dep2=3e-3):
    nm = NoiseModel()
    p_ad = 1 - np.exp(-gate_us / t1)
    p_pd = 0.5 * (1 + np.exp(-gate_us * (1/t2 - 1/(2*t1))))
    ad  = amplitude_damping_error(p_ad)
    pd  = phase_damping_error(p_pd)
    nm.add_all_qubit_quantum_error(ad.compose(pd)
                                   .compose(depolarizing_error(dep1, 1)),
                                   ['u1','u2','u3'])

    nm.add_all_qubit_quantum_error(depolarizing_error(dep2,2), ['cx'])
    return nm