#!/usr/bin/env python3
"""
experiments.py
Runs Grover search for n=2..5, reproducing Nature (2024) results.
 * n=2  → encoded [[4,2,2]] + post‐selection
 * n=3‐5 → unencoded + robust dynamical‐decoupling

Set USE_ENCODED = False if you just want the unencoded baseline.
"""

import itertools, json, pickle, pathlib, math
import numpy as np, pandas as pd

# Qiskit imports
from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import transpile, schedule
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit.ignis.mitigation.measurement import complete_meas_cal, CompleteMeasFitter
from qiskit.transpiler.passes.scheduling.dynamical_decoupling import DynamicalDecoupling
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.circuit.library import XGate, YGate
from qiskit.providers.fake_provider import FakeNairobi

# your own modules
from circuits import grover_unencoded, grover_encoded, accept, logical_outcome
from dd_sequences import DD_FAMILIES
from noise_model import build_noise

# toggle encoded n=2 run
USE_ENCODED = True

# ------------------------------------------------------------------
#  Set up an AerSimulator that *has* .defaults() so DD actually fires
# ------------------------------------------------------------------
fake = FakeNairobi()
noise = NoiseModel.from_backend(fake)
backend = AerSimulator.from_backend(
    fake,
    noise_model=noise
)

# cache for measurement‐error mitigators
_mf_cache = {}

def meas_filter(n_phys):
    """
    Build (and cache) a measurement‐error filter for n_phys qubits.
    Usage:
        counts = backend.run(...).result().get_counts()
        mitigated = meas_filter(n_phys)(counts)
    """
    if n_phys not in _mf_cache:
        qr = QuantumRegister(n_phys, name="mcal")
        cal_circuits, state_labels = complete_meas_cal(qr=qr)
        # AerSimulator will run them as‐is; no need to transpile
        job = backend.run(cal_circuits, shots=4096)
        result = job.result()
        # pass qr[:] to qubit_list
        fitter = CompleteMeasFitter(result, state_labels, qubit_list=qr[:])
        _mf_cache[n_phys] = fitter.filter.apply
    return _mf_cache[n_phys]

# --------------------------------------------------------------------
# Helpers for robust DD insertion: flatten → rewrap → schedule → DD
# --------------------------------------------------------------------
def _flatten(circ: QuantumCircuit) -> QuantumCircuit:
    flat, prev = circ, None
    while flat.depth() != prev:
        prev = flat.depth()
        flat = flat.decompose()
    return flat

def _merge_to_single_qreg(circ: QuantumCircuit) -> QuantumCircuit:
    """Re‐package all qubits into one QuantumRegister 'q' plus the original clbits."""
    qr = QuantumRegister(circ.num_qubits, name="q")
    new = QuantumCircuit(qr, *circ.clbits, name=circ.name)
    new.append(circ.to_instruction(), qr[:] + circ.clbits)
    return new

def with_dd(circ: QuantumCircuit, backend, family: str) -> QuantumCircuit:
    """
    Insert robust DD into circ, using real‐device timings.
    If the backend has no .defaults(), we assume it's AerSimulator and skip DD.
    """
    if not hasattr(backend, "defaults"):
        return circ

    # 1) fully decompose
    flat = _flatten(circ)
    # 2) merge into one QR named 'q'
    phys = _merge_to_single_qreg(flat)
    # 3) schedule using Qiskit's built‐in scheduler (ALAP by default)
    sched_qc = schedule(phys, backend=backend)
    dag_sched = circuit_to_dag(sched_qc)

    # 4) build the pulse‐sequence as Gate objects
    seq = []
    for ax in DD_FAMILIES[family]:
        if   ax == "X":  seq.append(XGate())
        elif ax == "-X": seq.append(XGate().inverse())
        elif ax == "Y":  seq.append(YGate())
        elif ax == "-Y": seq.append(YGate().inverse())
        else:
            raise ValueError(f"Unknown axis '{ax}' in DD family '{family}'")

    # 5) run the DD pass
    dd_pass = DynamicalDecoupling(backend.properties(), seq)
    dag_dd  = dd_pass.run(dag_sched)

    # 6) back to a circuit
    return dag_to_circuit(dag_dd)

# --------------------------------------------------------------------
# Main sweep
# --------------------------------------------------------------------
def main():
    records = []

    for n in [2,3,4,5]:
        N = 2**n
        # optimal number of queries
        qopt = 1 if n == 2 else math.floor((math.pi/4)*math.sqrt(N))
        marked_states = [format(i, f"0{n}b") for i in range(N)]

        for marked in marked_states:
            # build the appropriate Grover circuit
            if n == 2 and USE_ENCODED:
                qc = grover_encoded(marked, q_queries=qopt)
                n_phys = 4
            else:
                qc_raw = grover_unencoded(n, marked, q_queries=qopt)
                qc = with_dd(qc_raw, backend, family='UR4') if n >= 3 else qc_raw
                n_phys = n

            # compile & run
            qc_t = transpile(qc, backend, optimization_level=1)
            result = backend.run(qc_t, shots=20000).result()
            counts = result.get_counts()

            # measurement‐error mitigation
            if n == 2:
                mitigated = counts
            else:
                mitigated = meas_filter(n_phys)(counts)

            # post‐selection & success‐rate
            if n == 2 and USE_ENCODED:
                # keep only code‐space outcomes
                good = {k:v for k,v in mitigated.items() if accept(k)}
                shots = sum(good.values())
                hits  = sum(v for k,v in good.items() if logical_outcome(k) == marked)
                success = hits/shots if shots else 0.0
            else:
                shots   = sum(mitigated.values())
                success = mitigated.get(marked, 0)/shots if shots else 0.0

            classical = (qopt + 1) / N

            records.append({
                'n':        n,
                'marked':   marked,
                'success':  success,
                'classical':classical,
                'shots':    shots
            })

    df = pd.DataFrame(records)
    df.to_pickle("grover_results.pkl")
    print("✅ Results saved to grover_results.pkl")

if __name__ == "__main__":
    main()