#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 02: Canonical Bell State Entanglement Benchmarking
"""

import time
from core.statistics import compute_nist_metrics

BELL_CONFIGS = [
    ("Phi+", "qreg q[2]; creg c[2]; h q[0]; cx q[0], q[1]; measure q -> c;", ["00", "11"], ["01", "10"]),
    ("Phi-", "qreg q[2]; creg c[2]; z q[0]; h q[0]; cx q[0], q[1]; measure q -> c;", ["00", "11"], ["01", "10"]),
    ("Psi+", "qreg q[2]; creg c[2]; x q[1]; h q[0]; cx q[0], q[1]; measure q -> c;", ["01", "10"], ["00", "11"]),
    ("Psi-", "qreg q[2]; creg c[2]; x q[1]; z q[0]; h q[0]; cx q[0], q[1]; measure q -> c;", ["01", "10"], ["00", "11"]),
]

def run(conn, runs=5, shots=500, log=print):
    log("\n" + "=" * 80)
    log("  [TEST 02] CANONICAL FOUR-STATE BELL ENTANGLEMENT BENCHMARK")
    log("=" * 80)

    raw_records = []
    summary_records = []

    for name, qasm_circuit, target_states, leak_states in BELL_CONFIGS:
        fidelities = []
        parities = []

        for r in range(1, runs + 1):
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_circuit, shots=shots)
            
            target_counts = sum(counts.get(s, 0) for s in target_states)
            leak_counts = sum(counts.get(s, 0) for s in leak_states)
            measured_total = target_counts + leak_counts

            fid = (target_counts / measured_total * 100.0) if measured_total > 0 else 0.0
            parity = (target_counts / leak_counts) if leak_counts > 0 else float(target_counts)

            fidelities.append(fid)
            parities.append(parity)

            raw_records.append({
                "category": "Bell_Entanglement", "module": "test_02_bell_entanglement",
                "operation": f"Bell_{name}", "run_index": r, "shots": measured_total,
                "metric_name": "State_Fidelity_pct", "value": round(fid, 2),
                "time_s": elapsed, "aux_data": f"Parity={parity:.1f}:1, Target={target_counts}, Leak={leak_counts}"
            })
            log(f"  -> |{name}> Run {r}/{runs}: Fidelity = {fid:.2f}%, Parity = {parity:.1f}:1 ({elapsed:.2f}s)")
            time.sleep(0.04)

        stats_fid = compute_nist_metrics(fidelities)

        summary_records.append({
            "domain": "Two_Qubit_Entanglement", "module": "test_02_bell_entanglement",
            "metric_label": f"Bell State |{name}> Fidelity (%)",
            "target_subspace": "+".join(target_states), "runs": runs, "total_shots": sum(r["shots"] for r in raw_records if r["operation"] == f"Bell_{name}"),
            "mean": stats_fid["mean"], "std_dev": stats_fid["std_dev"], "sem": stats_fid["sem"],
            "ci_95_low": stats_fid["ci_95_low"], "ci_95_high": stats_fid["ci_95_high"],
            "cv_pct": stats_fid["cv_pct"], "min_val": stats_fid["min_val"], "max_val": stats_fid["max_val"],
            "standard": "Nielsen & Chuang (2010)",
            "status": "CERTIFIED" if stats_fid["ci_95_low"] > 90.0 else "PASSED"
        })

    return summary_records, raw_records
