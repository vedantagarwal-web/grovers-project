"""
Short robust dynamical‑decoupling pulse lists copied from
Pokharel & Lidar (2024).
Each list is the *axis* for a π pulse (X, −X, Y, −Y).
The actual pulse objects are generated inside experiments.py
using qiskit.schedules.library.
"""

UR4  =  ['X', 'Y', '-X', '-Y']        # Universally‑Robust (UR) 4‑pulse
CDD2 =  ['X', '-X', '-X', 'X']        # Concatenated DD level‑2 (4 pulses)
RGA8 =  ['X', 'Y', '-X', '-Y',        # Robust GA sequence, 8 pulses
         'Y', 'X', '-Y', '-X']

DD_FAMILIES = {'UR4':UR4, 'CDD2':CDD2, 'RGA8':RGA8}