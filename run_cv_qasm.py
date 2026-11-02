#!/usr/bin/env python3
"""
Run CV-QASM Qumode Circuits on Planck 2 Quantum Computer.
"""

from planck2 import Planck2

# 1. Initialize Planck 2 connection (auto-detects USB port)
qpu = Planck2()

# 2. Define your Qumode circuit (CV-QASM / Blackbird pipe syntax)
cv_circuit = """
S(0.8, 0.0) | 0
D(1.2, 0.0) | 0
R(45.0) | 0
BS(45.0) | (0, 1)
CZ | (0, 1)
MeasureHomodyne(45.0) | 0
"""

# 3. Execute on physical hardware
print("[*] Executing CV-QASM circuit on Planck 2...")
q = qpu.run_cv(cv_circuit)

print("\n" + "=" * 40)
print(f"Measured Field Quadrature q = {q:+.4f}")
print("=" * 40)
