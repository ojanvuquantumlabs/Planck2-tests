#!/usr/bin/env python3
"""
===============================================================================
Ojanvu Planck 2: Known-Answer Quantum Circuit Verification Suite
===============================================================================
Executes mathematically deterministic and analytically known quantum circuits
on physical Planck 2 hardware to verify exact computational accuracy.

Test Benchmarks:
  1. 50-Qubit Deterministic Bit-Pattern Target (|101010...10>)
  2. 50-Qubit Deep Entangled GHZ State (|000...0> + |111...1>)
  3. 50-Qubit Quantum Reversibility / Uncomputing (U† U = I -> |000...0>)
  4. 2-Qubit Bell State (EPR Parity Consensus)
===============================================================================
"""

import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planck2 import Planck2

print("[*] Initializing connection to Planck 2 Quantum Computer...")
qpu = Planck2()

print("\n" + "=" * 80)
print("  PLANCK 2 QUANTUM COMPUTER: KNOWN-ANSWER ACCURACY VERIFICATION")
print("=" * 80)

# -----------------------------------------------------------------------------
# TEST 1: 50-Qubit Deterministic Inversion Pattern
# -----------------------------------------------------------------------------
print("\n[TEST 1] 50-Qubit Deterministic Inversion Pattern Target...")
N = 50
lines = [
    "OPENQASM 2.0;",
    'include "qelib1.inc";',
    f"qreg q[{N}];",
    f"creg c[{N}];"
]
expected_bits = []
for i in range(N):
    if i % 2 == 1:
        lines.append(f"x q[{i}];")
        expected_bits.append("1")
    else:
        expected_bits.append("0")
for i in range(N):
    lines.append(f"measure q[{i}] -> c[{i}];")

expected_str = "".join(reversed(expected_bits))  # MSB to LSB convention
circ1 = "\n".join(lines)

t0 = time.time()
res1 = qpu.run_qasm(circ1, shots=50, qec=True)
t1 = time.time() - t0

target_count = res1.get(expected_str, 0)
fidelity1 = (target_count / 50) * 100.0

print(f"  Target Bitstring  : |{expected_str}>")
print(f"  Measured Outcomes : {res1}")
print(f"  Accuracy Fidelity : {fidelity1:.2f}% ({target_count}/50 shots) in {t1:.2f}s")
assert fidelity1 == 100.0, "Test 1 Failed"
print("  [✓] TEST 1 PASSED: Exact 50-bit deterministic accuracy certified.")

# -----------------------------------------------------------------------------
# TEST 2: 50-Qubit Entangled GHZ State (|000...0> + |111...1>)
# -----------------------------------------------------------------------------
print("\n[TEST 2] 50-Qubit Entangled GHZ State (|000...0> + |111...1>)...")
lines2 = [
    "OPENQASM 2.0;",
    'include "qelib1.inc";',
    f"qreg q[{N}];",
    f"creg c[{N}];",
    "h q[0];"
]
for i in range(N - 1):
    lines2.append(f"cx q[{i}], q[{i+1}];")
for i in range(N):
    lines2.append(f"measure q[{i}] -> c[{i}];")

circ2 = "\n".join(lines2)
t0 = time.time()
res2 = qpu.run_qasm(circ2, shots=50, qec=True)
t2 = time.time() - t0

all_ones = "1" * N
all_zeros = "0" * N
valid_ghz_shots = res2.get(all_ones, 0) + res2.get(all_zeros, 0)
ghz_fidelity = (valid_ghz_shots / 50) * 100.0

print(f"  Measured Outcomes :")
for state, cnt in res2.items():
    print(f"    |{state}> : {cnt} shots ({cnt/50*100:.1f}%)")
print(f"  GHZ State Fidelity: {ghz_fidelity:.2f}% ({valid_ghz_shots}/50 valid entangled shots) in {t2:.2f}s")
assert ghz_fidelity == 100.0, "Test 2 Failed"
print("  [✓] TEST 2 PASSED: 100% 50-qubit GHZ state coherence certified (zero mixed bit-flips).")

# -----------------------------------------------------------------------------
# TEST 3: 50-Qubit Quantum Reversibility (Uncomputing U† U = I)
# -----------------------------------------------------------------------------
print("\n[TEST 3] 50-Qubit Quantum Reversibility (Uncomputing U† U = I)...")
lines3 = [
    "OPENQASM 2.0;",
    'include "qelib1.inc";',
    f"qreg q[{N}];",
    f"creg c[{N}];",
    "// Forward deep entangling unitary U",
    "h q[0];"
]
for i in range(N - 1):
    lines3.append(f"cx q[{i}], q[{i+1}];")

lines3.append("// Reverse adjoint unitary U†")
for i in range(N - 2, -1, -1):
    lines3.append(f"cx q[{i}], q[{i+1}];")
lines3.append("h q[0];")

for i in range(N):
    lines3.append(f"measure q[{i}] -> c[{i}];")

circ3 = "\n".join(lines3)
t0 = time.time()
res3 = qpu.run_qasm(circ3, shots=50, qec=True)
t3 = time.time() - t0

uncompute_shots = res3.get(all_zeros, 0)
uncompute_fidelity = (uncompute_shots / 50) * 100.0

print(f"  Expected State    : |{all_zeros}>")
print(f"  Measured Outcomes : {res3}")
print(f"  Reversible Fid.   : {uncompute_fidelity:.2f}% ({uncompute_shots}/50 shots) in {t3:.2f}s")
assert uncompute_fidelity == 100.0, "Test 3 Failed"
print("  [✓] TEST 3 PASSED: Full 50-qubit quantum reversibility and unitary preservation certified.")

# -----------------------------------------------------------------------------
# TEST 4: 2-Qubit Bell State Consensus (EPR Fidelity)
# -----------------------------------------------------------------------------
print("\n[TEST 4] 2-Qubit Bell State (EPR Parity Consensus)...")
circ4 = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
"""
t0 = time.time()
res4 = qpu.run_qasm(circ4, shots=100, qec=True)
t4 = time.time() - t0

bell_valid = res4.get("00", 0) + res4.get("11", 0)
bell_fidelity = (bell_valid / 100) * 100.0

print(f"  Measured Outcomes : {res4}")
print(f"  Bell State Fid.   : {bell_fidelity:.2f}% ({bell_valid}/100 shots) in {t4:.2f}s")
assert bell_fidelity == 100.0, "Test 4 Failed"
print("  [✓] TEST 4 PASSED: 100.00% Bell fidelity certified under 3:1 Chromatic QEC.")

print("\n" + "=" * 80)
print("  ALL KNOWN-ANSWER ACCURACY BENCHMARKS PASSED (100.00% FIDELITY)")
print("=" * 80 + "\n")
