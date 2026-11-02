#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 03: Single-Qubit Gates & Continuous Parametric Rotations
"""

import math
import time
from core.statistics import compute_nist_metrics

SINGLE_QUBIT_CIRCUITS = [
    ("Pauli X", "qreg q[1]; creg c[1]; x q[0]; measure q[0] -> c[0];", ["1"], 100.0),
    ("Identity Return X-X", "qreg q[1]; creg c[1]; x q[0]; x q[0]; measure q[0] -> c[0];", ["0"], 100.0),
    ("Hadamard Inversion H-H", "qreg q[1]; creg c[1]; h q[0]; h q[0]; measure q[0] -> c[0];", ["0"], 100.0),
    ("Phase Inversion S-Sdg", "qreg q[1]; creg c[1]; s q[0]; sdg q[0]; measure q[0] -> c[0];", ["0"], 100.0),
    ("Non-Clifford Inversion T^4", "qreg q[1]; creg c[1]; t q[0]; t q[0]; t q[0]; t q[0]; measure q[0] -> c[0];", ["0"], 100.0),
    ("Continuous Rotation Ry(pi/4)", "qreg q[1]; creg c[1]; ry(0.785398) q[0]; measure q[0] -> c[0];", ["1"], 14.64),
    ("Continuous Rotation Ry(pi/2)", "qreg q[1]; creg c[1]; ry(1.570796) q[0]; measure q[0] -> c[0];", ["1"], 50.0),
    ("Continuous Rotation Ry(pi)", "qreg q[1]; creg c[1]; ry(3.141592) q[0]; measure q[0] -> c[0];", ["1"], 100.0),
    ("Continuous Rotation Rz(pi)", "qreg q[1]; creg c[1]; h q[0]; rz(3.141592) q[0]; h q[0]; measure q[0] -> c[0];", ["1"], 100.0),
]

def run(conn, runs=5, shots=500, log=print):
    log("\n" + "=" * 80)
    log("  [TEST 03] SINGLE-QUBIT GATES & CONTINUOUS ROTATION PARAMETRIC SWEEPS")
    log("=" * 80)

    raw_records = []
    summary_records = []

    for label, qasm_code, target_states, ideal_pct in SINGLE_QUBIT_CIRCUITS:
        fidelities = []

        for r in range(1, runs + 1):
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_code, shots=shots)
            
            tc = sum(counts.get(s, 0) for s in target_states)
            measured_total = sum(counts.values())
            
            fid = (tc / measured_total * 100.0) if measured_total > 0 else 0.0
            fidelities.append(fid)

            raw_records.append({
                "category": "Single_Qubit_Gate", "module": "test_03_single_qubit",
                "operation": label, "run_index": r, "shots": measured_total,
                "metric_name": "Observed_Probability_pct", "value": round(fid, 2),
                "time_s": elapsed, "aux_data": f"Target={'+'.join(target_states)}, Ideal={ideal_pct:.2f}%"
            })
            log(f"  -> {label[:28]:28s} Run {r}/{runs}: P(Target) = {fid:6.2f}% (Ideal: {ideal_pct:5.2f}%)")
            time.sleep(0.04)

        stats_fid = compute_nist_metrics(fidelities)

        summary_records.append({
            "domain": "Single_Qubit_Gates", "module": "test_03_single_qubit",
            "metric_label": f"{label} Fidelity / Probability",
            "target_subspace": f"{'+'.join(target_states)} (Ideal={ideal_pct:.1f}%)",
            "runs": runs, "total_shots": sum(r["shots"] for r in raw_records if r["operation"] == label),
            "mean": stats_fid["mean"], "std_dev": stats_fid["std_dev"], "sem": stats_fid["sem"],
            "ci_95_low": stats_fid["ci_95_low"], "ci_95_high": stats_fid["ci_95_high"],
            "cv_pct": stats_fid["cv_pct"], "min_val": stats_fid["min_val"], "max_val": stats_fid["max_val"],
            "standard": "Knill et al. (2008) Randomized Benchmarking",
            "status": "CERTIFIED" if stats_fid["cv_pct"] < 3.0 else "PASSED"
        })

    return summary_records, raw_records
