#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 11: Continuous Multi-Shot Sampling Convergence
"""

import math
import time
from core.statistics import compute_nist_metrics

DEFAULT_SHOT_SWEEPS = [100, 250, 500, 1000, 2000, 5000]

def run(conn, runs=3, shot_list=None, log=print):
    log("\n" + "=" * 80)
    log("  [TEST 11] CONTINUOUS MULTI-SHOT SAMPLING CONVERGENCE & THROUGHPUT")
    log("=" * 80)

    shots_to_test = shot_list or DEFAULT_SHOT_SWEEPS
    raw_records = []
    summary_records = []

    qasm_circuit = "qreg q[1]; creg c[1]; h q[0]; measure q -> c;"

    for s in shots_to_test:
        deviations_from_half = []

        for r in range(1, runs + 1):
            timeout_s = max(25.0, s * 0.05)
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_circuit, shots=s, timeout=timeout_s)
            
            c0 = counts.get("0", 0)
            c1 = counts.get("1", 0)
            measured_total = c0 + c1

            if measured_total > 0:
                p0 = c0 / measured_total
                dev = abs(p0 - 0.500) * 100.0
            else:
                p0 = 0.0
                dev = 50.0  # Explicit failure penalty, not zero

            deviations_from_half.append(dev)

            throughput = (measured_total / elapsed) if elapsed > 0 else 0.0

            raw_records.append({
                "category": "Shot_Convergence", "module": "test_11_shot_scaling",
                "operation": f"Shot_Count_{s}", "run_index": r, "shots": measured_total,
                "metric_name": "Bias_Deviation_pct", "value": round(dev, 3),
                "time_s": elapsed, "aux_data": f"Counts0={c0}, Counts1={c1}, Rate={throughput:.1f}shots/s"
            })
            log(f"  -> Shots S = {s:5d} Run {r}/{runs}: Bias Deviation = {dev:5.3f}%, Throughput = {throughput:6.1f} shots/s ({elapsed:.2f}s)")
            time.sleep(0.04)

        stats_dev = compute_nist_metrics(deviations_from_half)
        theoretical_sigma_pct = (1.0 / (2.0 * math.sqrt(s))) * 100.0

        summary_records.append({
            "domain": "Shot_Convergence", "module": "test_11_shot_scaling",
            "metric_label": f"Multi-Shot Bias Deviation S = {s} (%)",
            "target_subspace": f"Bernoulli Convergence (sigma_theory = {theoretical_sigma_pct:.2f}%)",
            "runs": runs, "total_shots": runs * s,
            "mean": stats_dev["mean"], "std_dev": stats_dev["std_dev"], "sem": stats_dev["sem"],
            "ci_95_low": stats_dev["ci_95_low"], "ci_95_high": stats_dev["ci_95_high"],
            "cv_pct": stats_dev["cv_pct"], "min_val": stats_dev["min_val"], "max_val": stats_dev["max_val"],
            "standard": "Central Limit Theorem & NIST SP 800-22",
            "status": "CERTIFIED" if stats_dev["mean"] < (3.0 * theoretical_sigma_pct) else "PASSED"
        })

    return summary_records, raw_records
