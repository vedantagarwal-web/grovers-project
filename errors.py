import random
from qiskit import QuantumCircuit

def x_error(p, qubits=(0,1,2,3)):
    qc = QuantumCircuit(4, name=f"Xerr{p}")
    on=[]
    for i in qubits:
        if random.random()<p: qc.x(i); on.append(i)
    return qc,on

def z_error(p, qubits=(0,1,2,3)):
    qc = QuantumCircuit(4, name=f"Zerr{p}")
    on=[]
    for i in qubits:
        if random.random()<p: qc.z(i); on.append(i)
    return qc,on