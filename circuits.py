"""
circuits.py
Quantum‑circuit building blocks used by experiments.py
Keeps *all* original oracles & encode/decode functions written earlier,
adds logical wrappers and Grover builders.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# ---------------------------------------------------------------------
#  [[4,2,2]]  encode / decode  (unchanged from your notebook)
# ---------------------------------------------------------------------
def encode_422():
    qc = QuantumCircuit(4, name="U_encode")
    qc.h(0)
    qc.cx(0,1); qc.cx(1,2); qc.cx(2,3)
    return qc

def decode_422():
    qc = QuantumCircuit(4, name="U_decode")
    qc.cx(2,3); qc.cx(1,2); qc.cx(0,1)
    qc.h(0)
    return qc

# ---------------------------------------------------------------------
#  stabiliser generators (as controlled gates so we can append)
# ---------------------------------------------------------------------
def stabilizer_1():
    qc = QuantumCircuit(4, name="S1")
    for i in range(4): qc.x(i)
    return qc.to_gate().control(1)

def stabilizer_2():
    qc = QuantumCircuit(4, name="S2")
    for i in range(4): qc.z(i)
    return qc.to_gate().control(1)

# ---------------------------------------------------------------------
#  Physical oracles  (verbatim from your partner’s notebook)
# ---------------------------------------------------------------------
def _oracle_template(bits_to_flip):
    qc = QuantumCircuit(4)
    for i in bits_to_flip: qc.x(i)
    for i in range(4): qc.s(i)
    for i in bits_to_flip: qc.z(i)
    for i in bits_to_flip: qc.x(i)
    return qc

oracle_00 = _oracle_template(bits_to_flip=[1,2])
oracle_01 = _oracle_template(bits_to_flip=[0,2])
oracle_10 = _oracle_template(bits_to_flip=[1,3])
oracle_11 = _oracle_template(bits_to_flip=[0,3])

_oracle = {"00": oracle_00, "01": oracle_01,
           "10": oracle_10, "11": oracle_11}

# ---------------------------------------------------------------------
#  logical wrappers for [[4,2,2]]
# ---------------------------------------------------------------------
def logical_H(qc, q):
    qc.h(q[1]); qc.h(q[2])

def logical_CZ(qc, q):
    qc.cz(q[0], q[2])

# circuits.py  – replace the old oracle_422 definition with this one
def oracle_422(marked: str):
    """
    Return a Gate that phase‑flips the logical |marked⟩ₗ state
    (marked ∈ {'00','01','10','11'}).
    """
    return _oracle[marked].to_gate(label=f"O_{marked}")   # <-- no ()

# ---------------------------------------------------------------------
#  Grover‑circuit builders  -------------------------------------------
# ---------------------------------------------------------------------
def grover_encoded(marked: str, q_queries=1):
    """2‑logical‑qubit Grover search protected by [[4,2,2]]."""
    q = QuantumRegister(4); c = ClassicalRegister(4)
    qc = QuantumCircuit(q, c, name=f"Grover422_{marked}")

    qc.append(encode_422(), q)
    logical_H(qc, q)

    for _ in range(q_queries):
        qc.append(oracle_422(marked), q)
        logical_H(qc, q)
        logical_CZ(qc, q)          # diffusion
        logical_H(qc, q)

    qc.append(decode_422(), q)
    qc.measure(q, c)
    return qc


def grover_unencoded(n: int, marked: str, q_queries=2):
    """Standard Grover on n physical qubits (n = 3–5 in this project)."""
    q = QuantumRegister(n); c = ClassicalRegister(n)
    qc = QuantumCircuit(q, c, name=f"Grover{n}_{marked}")

    qc.h(q)                         # |+>^n superposition
    for _ in range(q_queries):
        # oracle (phase‑flip the marked basis state)
        for i, bit in enumerate(marked[::-1]):
            if bit == "0": qc.x(q[i])
        qc.h(q[-1])
        qc.mcx(q[:-1], q[-1])
        qc.h(q[-1])
        for i, bit in enumerate(marked[::-1]):
            if bit == "0": qc.x(q[i])

        # diffusion
        qc.h(q); qc.x(q)
        qc.h(q[-1]); qc.mcx(q[:-1], q[-1]); qc.h(q[-1])
        qc.x(q); qc.h(q)

    qc.measure(q, c)
    return qc

# ---------------------------------------------------------------------
#  post‑selection helpers (Algorithmic Error Tomography)
# ---------------------------------------------------------------------
def syndrome(bits: str) -> str:
    """Return +1/–1 eigenvalues of (XXXX, ZZZZ) in binary."""
    return bits[0] + str(int(bits[1]) ^ int(bits[3]))

def accept(bits: str) -> bool:
    return syndrome(bits) == "00"

def logical_outcome(bits: str) -> str:
    z1 = bits[1]
    z2 = str(int(bits[1]) ^ int(bits[2]))
    return z1 + z2