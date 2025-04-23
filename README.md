# Grover's Algorithm with Quantum Error Detection and Suppression

This repository implements Grover's quantum search algorithm with quantum error detection and suppression techniques, based on the research paper ["Better-than-classical Grover search via quantum error detection and suppression"](https://www.nature.com/articles/s41534-023-00794-6) (Pokharel & Lidar, 2024).

## Overview

This implementation demonstrates better-than-classical success probabilities for Grover's quantum search algorithm using:
- Up to 5 physical qubits
- [[4,2,2]] quantum error-detection code for 2 logical qubits
- Robust dynamical decoupling for error suppression
- Algorithmic error tomography for error analysis

## Key Features

- Implementation of basic Grover's algorithm
- Quantum error detection using [[4,2,2]] code
- Error suppression via dynamical decoupling
- Support for both encoded and unencoded quantum circuits
- Measurement error mitigation techniques

## Project Structure

```
.
├── circuits.py           # Core quantum circuit implementations
├── experiments.py        # Experimental setup and execution code
└── notebooks/           # Jupyter notebooks for analysis and visualization
```

## Requirements

- Python 3.8+
- Qiskit
- NumPy
- Matplotlib
- Jupyter (for notebooks)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vedantagarwal-web/grovers-project.git
cd grovers-project
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Grover Search

```python
from circuits import grover_unencoded

# Create a circuit for 3-qubit Grover search
circuit = grover_unencoded(n=3, marked="101")
```

### Error-Protected Search

```python
from circuits import grover_encoded

# Create an error-protected circuit using [[4,2,2]] code
circuit = grover_encoded(marked="11", q_queries=1)
```

## Implementation Details

### Quantum Error Detection

The [[4,2,2]] quantum error-detection code is implemented to:
- Encode 2 logical qubits into 4 physical qubits
- Detect arbitrary single-qubit errors
- Achieve up to 99.5% success probability for 2-qubit search

### Error Suppression

Three robust dynamical decoupling (DD) families are implemented:
- Universally robust (UR)
- Concatenated DD (CDD)
- Robust genetic algorithm (RGA) sequences

### Algorithmic Error Tomography

The implementation includes tools for:
- Analyzing errors accumulated during algorithm execution
- Computing error detection probabilities
- Validating error models against experimental results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use this code in your research, please cite:

```bibtex
@article{pokharel2024better,
  title={Better-than-classical Grover search via quantum error detection and suppression},
  author={Pokharel, Bibek and Lidar, Daniel A},
  journal={npj Quantum Information},
  volume={10},
  number={1},
  pages={23},
  year={2024},
  publisher={Nature Publishing Group}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This implementation is based on research supported by:
- ARO MURI grant W911NF-22-S-0007
- National Science Foundation Quantum Leap Big Idea (Grant No. OMA-1936388)
- IBM Quantum services 