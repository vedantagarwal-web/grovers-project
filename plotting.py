# plotting.py
"""
Makes (a) failure‑probability bar chart and (b) AET heat‑map.
Usage:
    %run plotting.py      # in a notebook (enables inline plotting)
  or
    python plotting.py    # from the shell
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import circuits, noise_model
from circuits import accept, logical_outcome
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit_aer.noise import NoiseModel
from qiskit.providers.fake_provider import FakeNairobi

def draw():
    df = pd.read_pickle("grover_results.pkl")

    # ------------- bar chart -----------------
    fail = 1 - df.groupby('n')['success'].mean()
    classical = df.groupby('n')['classical'].mean()
    plt.figure(figsize=(6,4))
    plt.bar(fail.index-0.15, fail,   width=0.3, label="Quantum (ours)")
    plt.bar(classical.index+0.15, classical,
            width=0.3, label="Optimal classical")
    plt.ylabel("failure probability")
    plt.xlabel("qubits n")
    plt.title("Grover failure vs. classical bound")
    plt.legend()
    plt.show()

    # ------------- AET heat‑map (n=2 encoded) -------------
    rows = {'00':0,'01':1,'10':2,'11':3}
    cols = ["0000","0010","0101","0111",
            "0001","0011","0100","0110",
            "1000","1010","1101","1111",
            "1001","1011","1100","1110"]
    table = np.zeros((4,16))

    # set up your AerSimulator once, with noise
    


# grab a fake device that *has* defaults() (gate times, T1/T2, etc)
    fake_device = FakeNairobi()

# build a NoiseModel from its real calibration
    noise_model = NoiseModel.from_backend(fake_device)

# now give AerSimulator *both* that noise_model *and* the fake_device’s timing info
    backend = AerSimulator.from_backend(
        fake_device,
        noise_model=noise_model,
    )

    for m, row in rows.items():
        # build & compile the encoded circuit
        qc = circuits.grover_encoded(m, q_queries=1)
        qc = transpile(qc, backend, optimization_level=1)  # <-- this strips out your U_encode etc.

        # run & collect
        result = backend.run(qc, shots=20000).result()
        counts = result.get_counts()

        # post‑select only the code‑space
        good = {k:v for k,v in counts.items() if accept(k)}
        for bits, v in good.items():
            table[row, cols.index(bits)] += v

    # normalize rows → probabilities
    table = (table.T / table.sum(axis=1)).T

    plt.figure(figsize=(8,2.5))
    plt.imshow(table, vmin=0, vmax=0.5, aspect='auto', cmap='plasma')
    plt.xticks(range(16), cols, rotation=90)
    plt.yticks(range(4), list(rows.keys()))
    plt.colorbar(label="Probability")
    plt.title("Algorithmic Error Tomography ([[4,2,2]] post‑selection)")
    plt.show()


if __name__ == "__main__":
    # if run under IPython / %run, enable inline plotting
    try:
        from IPython import get_ipython
        get_ipython().run_line_magic('matplotlib', 'inline')
    except:
        pass

    draw()