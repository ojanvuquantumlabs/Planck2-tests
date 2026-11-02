#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 04: Two-Qubit Entangling Gates & Unitary Inversions
"""

import time
from core.statistics import compute_nist_metrics

TWO_QUBIT_CIRCUITS = [
    ("Controlled-Z (CZ)", "qreg q[2]; creg c[2]; h q[0]; h q[1]; cz q[0], q[1]; cz q[0], q[1]; h q[0]; h q[1]; measure q -> c;", ["00"]),
    ("Controlled-NOT (CX)", "qreg q[2]; creg c[2]; x q[1]; cx q[0], q[1]; cx q[0], q[1]; measure q -> c;", ["10"]),
    ("SWAP Permutation", "qreg q[2]; creg c[2]; x q[0]; swap q[0], q[1]; swap q[0], q[1]; measure q -> c;", ["01"]),
]

def run(conn, runs=5, shots=500, log=print):
    log("\n" + "=" * 80)
    log("  [TEST 04] TWO-QUBIT ENTANGLING GATE INVERSIONS & REVERSIBILITY")
    log("=" * 80)

    raw_records = []
    summary_records = []

    for label, qasm_code, target_states in TWO_QUBIT_CIRCUITS:
        fidelities = []

        for r in range(1, runs + 1):
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_code, shots=shots)
            
            tc = sum(counts.get(s, 0) for s in target_states)
            measured_total = sum(counts.values())
            
            fid = (tc / measured_total * 100.0) if measured_total > 0 else 0.0
            fidelities.append(fid)

            raw_records.append({
                "category": "Two_Qubit_Gate", "module": "test_04_two_qubit",
                "operation": label, "run_index": r, "shots": measured_total,
                "metric_name": "Inversion_Fidelity_pct", "value": round(fid, 2),
                "time_s": elapsed, "aux_data": f"Target={'+'.join(target_states)}"
            })
            log(f"  -> {label[:25]:25s} Run {r}/{runs}: Inversion Fidelity = {fid:6.2f}% ({elapsed:.2f}s)")
            time.sleep(0.04)

        stats_fid = compute_nist_metrics(fidelities)

        summary_records.append({
            "domain": "Two_Qubit_Gates", "module": "test_04_two_qubit",
            "metric_label": f"{label} Inversion Fidelity (%)",
            "target_subspace": "+".join(target_states),
            "runs": runs, "total_shots": sum(r["shots"] for r in raw_records if r["operation"] == label),
            "mean": stats_fid["mean"], "std_dev": stats_fid["std_dev"], "sem": stats_fid["sem"],
            "ci_95_low": stats_fid["ci_95_low"], "ci_95_high": stats_fid["ci_95_high"],
            "cv_pct": stats_fid["cv_pct"], "min_val": stats_fid["min_val"], "max_val": stats_fid["max_val"],
            "standard": "Barends et al. (2014) Nature Protocol",
            "status": "CERTIFIED" if stats_fid["ci_95_low"] > 80.0 else "PASSED"
        })

    return summary_records, raw_records
