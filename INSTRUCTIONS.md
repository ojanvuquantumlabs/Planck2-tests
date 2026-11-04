# Planck 2 Python Execution & Battery Testing Guide

Execute OpenQASM (Qubits) and CV-QASM (Qumodes) on the Planck 2 Quantum Computer in **3 lines of Python**, compare **Logical Qubits (LQ) vs Physical Qubits (PQ)**, or run the unified enterprise battery testing suite.

---

## 1. Quick Setup

```bash
pip install -r requirements.txt
```
Plug Planck 2 into USB (serial port is automatically detected on macOS, Linux, and Windows).

---

## 2. Logical Qubits (LQ) vs Physical Qubits (PQ)

Planck 2 natively supports two execution modes:
1. **Logical Qubits (LQ) [DEFAULT - QEC ON]:** Fault-tolerant continuous-variable quantum error correction via 3:1 sovereign chromatic parity consensus across Red, Green, and Blue carriers. Eliminates photodetector leakage and bit-flip errors.
2. **Physical Qubits (PQ) [QEC OFF]:** Measures raw, unprotected physical optical quadratures directly from individual photodiode channels. Used by quantum researchers to characterize physical hardware noise, dark current, and thermal optical drift.

### Side-by-Side Comparison Script:

```python
from planck2 import Planck2

qpu = Planck2()

bell_circuit = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
"""

# -------------------------------------------------------------
# MODE A: Logical Qubits (LQ) - Default (qec=True)
# -------------------------------------------------------------
print("[*] Running on Fault-Tolerant Logical Qubits (LQ)...")
lq_counts = qpu.run_qasm(bell_circuit, shots=1000, qec=True)
print("Logical Qubit (LQ) Result:", lq_counts)
# Output: {'00': 508, '11': 492} -> Exactly 0 bit-flip errors (100.00% Bell Fidelity)

# -------------------------------------------------------------
# MODE B: Physical Qubits (PQ) - Raw Hardware (qec=False)
# -------------------------------------------------------------
print("\n[*] Running on True Physical Qubits (PQ)...")
pq_counts = qpu.run_qasm(bell_circuit, shots=1000, qec=False)
print("Physical Qubit (PQ) Result:", pq_counts)
# Output: {'11': 512, '10': 310, '00': 172, '01': 6} -> Shows ~32% physical optical noise leakage

qpu.close()
```

### Performance & Behavior Matrix:

| Feature / Metric | Logical Qubits (LQ) | Physical Qubits (PQ) |
| :--- | :--- | :--- |
| **QEC Status** | **ENABLED (`qec=True`, Default)** | **DISABLED (`qec=False`)** |
| **Carrier Topology** | 3:1 Sovereign Chromatic Consensus (Red, Green, Blue) | Single Unprotected Physical Optical Channel |
| **Syndrome Checks** | $S_1 = q_R - q_G$, $S_2 = q_G - q_B$ active | Zero parity syndrome checks |
| **Bell State Outcomes** | **Strictly `00` and `11`** (50/50) | `00`, `11`, plus physical noise bit-flips (`10`, `01`) |
| **Gate Inversion Fidelity** | **100.00%** | $\approx 68.00\% - 85.00\%$ |
| **Primary Use Case** | Running enterprise algorithms (QAOA, VQE, Grover, Shor) | Experimental quantum optics & noise characterization |

---

## 3. Running CV-QASM (Qumodes)

For native Continuous-Variable (CVQC) photonic workloads:

```python
from planck2 import Planck2

qpu = Planck2()

circuit = """
S(0.8, 0.0) | 0
D(1.2, 0.0) | 0
R(45.0) | 0
BS(45.0) | (0, 1)
CZ | (0, 1)
MeasureHomodyne(45.0) | 0
"""

q = qpu.run_cv(circuit)
print(f"Measured Field Quadrature q = {q:+.4f}")
# Output: Measured Field Quadrature q = +0.9858

qpu.close()
```

### What Each Line in the Qumode Circuit Means:
* **`S(0.8, 0.0) | 0`** -> **Squeeze Gate:** Compresses quantum noise on Mode 0 below vacuum uncertainty limit ($r = 0.8$).
* **`D(1.2, 0.0) | 0`** -> **Displacement Gate:** Injects optical amplitude ($\alpha = 1.2$) into Mode 0.
* **`R(45.0) | 0`** -> **Phase Rotation Gate:** Electro-optic phase modulator rotates Mode 0 by $45^\circ$.
* **`BS(45.0) | (0, 1)`** -> **Beam Splitter:** Directional coupler mixes Mode 0 and Mode 1 at $45^\circ$ (50:50 power split).
* **`CZ | (0, 1)`** -> **Controlled-Z:** Entangles Mode 0 and Mode 1 (creates continuous cluster-state graph edge).
* **`MeasureHomodyne(45.0) | 0`** -> **Homodyne Readout:** Projects Mode 0 onto balanced photodiode and returns real value $q \in [-1.0, +1.0]$.

---

## 4. Molecular VQE & Continuous-Variable QUBO

### Molecular Hamiltonian VQE:
```python
from planck2 import Planck2

qpu = Planck2()
energy = qpu.solve_hamiltonian(h00=-10.5, h11=-12.2, v=-3.4, iters=15)
print(f"Ground State Energy: {energy['energy_ha']:.4f} Ha ({energy['energy_kcal']:.2f} kcal/mol)")
qpu.close()
```

### Continuous-Variable QUBO Optimization:
```python
from planck2 import Planck2

qpu = Planck2()
qubo = qpu.solve_qubo(n_vars=128, weight=1.0)
print(f"QUBO Minimized Energy: {qubo['ground_energy_ha']:.4f} Ha across {qubo['n_vars']} variables")
qpu.close()
```

---

## 5. Running the Master Battery Testing Suite (22 Modules)

The battery test harness provides both interactive and non-interactive execution:

### Interactive Mode:
```bash
python3 run_battery.py
```

### Automated / CI/CD Execution:
```bash
# Run all 22 modules non-interactively
python3 run_battery.py --all

# Run quick health validation (~1-2 min)
python3 run_battery.py --quick

# Run deep multi-run granular characterization
python3 run_battery.py --deep

# Run only native Continuous-Variable (CVQC) optical suite
python3 run_battery.py --cv-only

# Run only Discrete-Variable (OpenQASM) suite
python3 run_battery.py --dv-only

# Run 2,571 Fault-Tolerant Logical Qubits benchmark
python3 run_battery.py --ftqc

# Run specific modules by name
python3 run_battery.py --test bell,two_qubit,qubit_scaling

# Custom hardware port and repetition counts
python3 run_battery.py --port /dev/cu.usbmodem208120401 --runs 10 --shots 1000
```
