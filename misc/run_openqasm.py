#!/usr/bin/env python3
"""
Run OpenQASM Qubit Circuits on Planck 2 Quantum Computer.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planck2 import Planck2

# 1. Initialize Planck 2 connection (auto-detects USB port)
qpu = Planck2()

# 2. Define your Qubit circuit (OpenQASM 2.0 / 3.0)
bell_state = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
"""

# 3. Execute on physical hardware
print("[*] Executing OpenQASM circuit on Planck 2...")
counts = qpu.run_qasm(bell_state, shots=1024)

print("\n" + "=" * 40)
print(f"Measurement Result: {counts}")
print("=" * 40)
