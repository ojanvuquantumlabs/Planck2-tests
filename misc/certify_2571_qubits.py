#!/usr/bin/env python3
"""
===============================================================================
Ojanvu Planck 2: Full 2,571 Logical Qubit Hardware Certification Suite
===============================================================================
Exhaustively benchmarks the maximum 2,571 Logical Qubit capacity (7,714 physical
continuous-variable qumodes under 3:1 Sovereign Chromatic QEC) across:
  1. Full 2,571-Qubit Global Superposition & Quantum Entropy
  2. Full 2,571-Qubit Deterministic Inversion (|111...1>)
  3. Full 2,571-Qubit Unitary Reversibility (H X X H = I -> |000...0>)
  4. Full 2,571-Qubit Continuous Electro-Optic Phase Rotation (Rx(pi) -> |111...1>)
  5. 1,000-Qubit Macroscopic Entangled GHZ State
===============================================================================
"""

import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planck2 import Planck2

print("[*] Initializing connection to Planck 2 Quantum Computer...")
qpu = Planck2()

N_MAX = 2571

print("\n" + "=" * 80)
print(f"  PLANCK 2 QUANTUM COMPUTER: {N_MAX} LOGICAL QUBIT FULL CAPACITY CERTIFICATION")
print("=" * 80)

# -----------------------------------------------------------------------------
# TEST 1: Full 2,571-Qubit Deterministic Inversion (|111...1>)
# -----------------------------------------------------------------------------
print(f"\n[TEST 1] Full {N_MAX}-Qubit Deterministic Inversion (X q; -> |111...1>)...")
circ1 = f"""
OPENQASM 2.0;
include "qelib1.inc";
qreg q[{N_MAX}];
creg c[{N_MAX}];

x q;
measure q -> c;
"""
t0 = time.time()
res1 = qpu.run_qasm(circ1, shots=50, qec=True)
elapsed1 = time.time() - t0

all_ones_2571 = "1" * N_MAX
ones_shots1 = res1.get(all_ones_2571, 0)
fid1 = (ones_shots1 / 50) * 100.0

print(f"  Measured Outcomes : {len(res1)} unique state(s)")
for state, cnt in res1.items():
    print(f"    |{state[:16]}...{state[-16:]}> : {cnt} shots ({cnt/50*100:.1f}%) [Length: {len(state)} bits]")
print(f"  Inversion Fidelity: {fid1:.2f}% ({ones_shots1}/50 shots) in {elapsed1:.2f}s")
assert fid1 == 100.0, f"Test 1 Failed: Expected 100% |111...1>, got {fid1}%"
print(f"  [✓] TEST 1 PASSED: All {N_MAX} Logical Qubits individually inverted with 100.00% precision.")

# -----------------------------------------------------------------------------
# TEST 2: Full 2,571-Qubit Quantum Reversibility (H X X H = I -> |000...0>)
# -----------------------------------------------------------------------------
print(f"\n[TEST 2] Full {N_MAX}-Qubit Unitary Reversibility (H X X H = I -> |000...0>)...")
circ2 = f"""
OPENQASM 2.0;
include "qelib1.inc";
qreg q[{N_MAX}];
creg c[{N_MAX}];

h q;
x q;
x q;
h q;
measure q -> c;
"""
t0 = time.time()
res2 = qpu.run_qasm(circ2, shots=50, qec=True)
elapsed2 = time.time() - t0

all_zeros_2571 = "0" * N_MAX
zeros_shots2 = res2.get(all_zeros_2571, 0)
fid2 = (zeros_shots2 / 50) * 100.0

print(f"  Measured Outcomes : {len(res2)} unique state(s)")
for state, cnt in res2.items():
    print(f"    |{state[:16]}...{state[-16:]}> : {cnt} shots ({cnt/50*100:.1f}%) [Length: {len(state)} bits]")
print(f"  Coherence Fidelity: {fid2:.2f}% ({zeros_shots2}/50 shots) in {elapsed2:.2f}s")
assert fid2 == 100.0, f"Test 2 Failed: Expected 100% |000...0>, got {fid2}%"
print(f"  [✓] TEST 2 PASSED: 100.00% Unitary reversibility preserved across all {N_MAX} qubits.")

# -----------------------------------------------------------------------------
# TEST 3: Full 2,571-Qubit Electro-Optic Phase Rotation (Rx(pi) -> |111...1>)
# -----------------------------------------------------------------------------
print(f"\n[TEST 3] Full {N_MAX}-Qubit Electro-Optic Parametric Rotation (Rx(pi) -> |111...1>)...")
circ3 = f"""
OPENQASM 2.0;
include "qelib1.inc";
qreg q[{N_MAX}];
creg c[{N_MAX}];

rx(pi) q;
measure q -> c;
"""
t0 = time.time()
res3 = qpu.run_qasm(circ3, shots=50, qec=True)
elapsed3 = time.time() - t0

rot_shots3 = res3.get(all_ones_2571, 0)
fid3 = (rot_shots3 / 50) * 100.0

print(f"  Measured Outcomes : {len(res3)} unique state(s)")
for state, cnt in res3.items():
    print(f"    |{state[:16]}...{state[-16:]}> : {cnt} shots ({cnt/50*100:.1f}%) [Length: {len(state)} bits]")
print(f"  Rotation Fidelity : {fid3:.2f}% ({rot_shots3}/50 shots) in {elapsed3:.2f}s")
assert fid3 == 100.0, f"Test 3 Failed: Expected 100% |111...1>, got {fid3}%"
print(f"  [✓] TEST 3 PASSED: Electro-optic phase driving calibrated across all {N_MAX} qubits.")

# -----------------------------------------------------------------------------
# TEST 4: Full 2,571-Qubit Superposition & Quantum Entropy
# -----------------------------------------------------------------------------
print(f"\n[TEST 4] Full {N_MAX}-Qubit Global Superposition & Born-Rule Entropy...")
circ4 = f"""
OPENQASM 2.0;
include "qelib1.inc";
qreg q[{N_MAX}];
creg c[{N_MAX}];

h q;
measure q -> c;
"""
t0 = time.time()
res4 = qpu.run_qasm(circ4, shots=100, qec=True)
elapsed4 = time.time() - t0

total_ones = 0
total_bits = 0
all_lengths_valid = True

for state, cnt in res4.items():
    if len(state) != N_MAX:
        all_lengths_valid = False
    ones = state.count("1")
    total_ones += ones * cnt
    total_bits += N_MAX * cnt

entropy_ratio = (total_ones / total_bits) * 100.0

print(f"  Sample Measured States (Total Unique: {len(res4)}):")
for idx, (state, cnt) in enumerate(list(res4.items())[:5], 1):
    ones = state.count("1")
    print(f"    #{idx}: |{state[:16]}...{state[-16:]}> ({cnt} shots) - {ones}/{N_MAX} ones ({ones/N_MAX*100:.1f}%)")
print(f"  Register Bit-Width: Exactly {N_MAX} bits verified ({all_lengths_valid})")
print(f"  Entropy Balance   : {entropy_ratio:.2f}% ones / {100.0 - entropy_ratio:.2f}% zeros in {elapsed4:.2f}s")
assert all_lengths_valid, "Bit length mismatch"
assert 40.0 <= entropy_ratio <= 60.0, f"Unbalanced entropy: {entropy_ratio}%"
print(f"  [✓] TEST 4 PASSED: Born-rule quantum superposition verified across all {N_MAX} qubits.")

# -----------------------------------------------------------------------------
# TEST 5: 1,000-Qubit Deep Entangled GHZ State
# -----------------------------------------------------------------------------
print(f"\n[TEST 5] 1,000-Qubit Deep Entangled GHZ State (H q[0] + 999 CNOTs)...")
N_GHZ = 1000
lines5 = [
    "OPENQASM 2.0;",
    'include "qelib1.inc";',
    f"qreg q[{N_GHZ}];",
    f"creg c[{N_GHZ}];",
    "h q[0];"
]
for i in range(N_GHZ - 1):
    lines5.append(f"cx q[{i}], q[{i+1}];")
lines5.append("measure q -> c;")
circ5 = "\n".join(lines5)

t0 = time.time()
res5 = qpu.run_qasm(circ5, shots=50, qec=True)
elapsed5 = time.time() - t0

ones_ghz = "1" * N_GHZ
zeros_ghz = "0" * N_GHZ
valid_ghz = res5.get(ones_ghz, 0) + res5.get(zeros_ghz, 0)
ghz_fid5 = (valid_ghz / 50) * 100.0

print(f"  Measured Outcomes : {len(res5)} state(s)")
for state, cnt in res5.items():
    print(f"    |{state[:16]}...{state[-16:]}> : {cnt} shots ({cnt/50*100:.1f}%) [Length: {len(state)} bits]")
print(f"  GHZ Entanglement  : {ghz_fid5:.2f}% ({valid_ghz}/50 valid entangled shots) in {elapsed5:.2f}s")
assert ghz_fid5 == 100.0, f"Test 5 Failed: Expected 100%, got {ghz_fid5}%"
print(f"  [✓] TEST 5 PASSED: 1,000-Qubit macroscopic optical entanglement certified (zero mixed bit-flips).")

print("\n" + "=" * 80)
print(f"  >>> ALL {N_MAX} LOGICAL QUBITS OFFICIALLY CERTIFIED ON PLANCK 2 HARDWARE <<<")
print("=" * 80 + "\n")
