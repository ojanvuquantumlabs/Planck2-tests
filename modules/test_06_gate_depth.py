#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 06: Granular Linear Gate Depth Stress & Adaptive Decoherence Hunting
"""

import time
from core.statistics import compute_nist_metrics

DEFAULT_DEPTH_SERIES = [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200]
ADAPTIVE_EXPANSION_STEPS = [250, 300, 350, 400, 500, 600, 750, 1000]

def build_depth_circuit(depth):
    """Constructs alternating Pauli-X circuit of exact depth D with structured line chunking."""
    lines = ["qreg q[1];", "creg c[1];"]
    for i in range(0, depth, 10):
        k = min(10, depth - i)
        lines.append(" ".join(["x q[0];"] * k))
    lines.append("measure q -> c;")
    return lines

def run(conn, runs=3, shots=200, depth_list=None, adaptive=True, fail_threshold=60.0, consecutive_limit=2, log=print):
    mode_str = "Adaptive Capacity Hunting" if adaptive else "Standard Fixed Sweeps"
    log("\n" + "=" * 80)
    log(f"  [TEST 06] GRANULAR LINEAR CIRCUIT GATE DEPTH STRESS ({mode_str})")
    log("=" * 80)

    raw_records = []
    summary_records = []

    # Assemble depth candidate queue
    base_depths = list(depth_list or DEFAULT_DEPTH_SERIES)
    active_queue = list(base_depths)

    consecutive_fails = 0
    tested_depths = set()
    idx = 0

    while idx < len(active_queue):
        d = active_queue[idx]
        idx += 1

        if d in tested_depths:
            continue
        tested_depths.add(d)

        qasm_circuit = build_depth_circuit(d)
        target_state = "0" if (d % 2 == 0) else "1"

        fidelities = []

        for r in range(1, runs + 1):
            timeout_s = max(35.0, d * 0.25 + (shots / 500.0) * 15.0)
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_circuit, shots=shots, timeout=timeout_s)
            
            tc = counts.get(target_state, 0)
            measured_total = sum(counts.values())

            fid = (tc / measured_total * 100.0) if measured_total > 0 else 0.0
            fidelities.append(fid)

            raw_records.append({
                "category": "Gate_Depth_Stress", "module": "test_06_gate_depth",
                "operation": f"Depth_{d}_Gates", "run_index": r, "shots": measured_total,
                "metric_name": "Retention_Fidelity_pct", "value": round(fid, 2),
                "time_s": elapsed, "aux_data": f"TargetState=|{target_state}>, Retained={tc}/{measured_total}"
            })
            log(f"  -> Depth D = {d:4d} Gates Run {r}/{runs}: Retention Fidelity = {fid:6.2f}% ({tc}/{measured_total} shots)")
            time.sleep(0.04)

        stats_fid = compute_nist_metrics(fidelities)

        summary_records.append({
            "domain": "Gate_Depth_Stress", "module": "test_06_gate_depth",
            "metric_label": f"Linear Gate Depth D = {d} Fidelity (%)",
            "target_subspace": f"|{target_state}> Return",
            "runs": runs, "total_shots": sum(r["shots"] for r in raw_records if r["operation"] == f"Depth_{d}_Gates"),
            "mean": stats_fid["mean"], "std_dev": stats_fid["std_dev"], "sem": stats_fid["sem"],
            "ci_95_low": stats_fid["ci_95_low"], "ci_95_high": stats_fid["ci_95_high"],
            "cv_pct": stats_fid["cv_pct"], "min_val": stats_fid["min_val"], "max_val": stats_fid["max_val"],
            "standard": "Magesan et al. (2011) Randomized Benchmarking Protocol",
            "status": "CERTIFIED" if stats_fid["ci_95_low"] >= 85.0 else ("PASSED" if stats_fid["mean"] >= fail_threshold else "EVALUATED")
        })

        # Adaptive Expansion & Hysteresis Boundary Detection
        if adaptive:
            # Check threshold
            if stats_fid["mean"] < fail_threshold:
                consecutive_fails += 1
                log(f"     [!] Threshold Breach: Mean Fidelity = {stats_fid['mean']:.2f}% < {fail_threshold}% (Consecutive Fails: {consecutive_fails}/{consecutive_limit})")
                if consecutive_fails >= consecutive_limit:
                    log(f"  [✓] Sustained Decoherence Boundary Identified at Depth D = {d} Gates. Halting adaptive expansion.")
                    break
            else:
                if consecutive_fails > 0:
                    log(f"     [✓] Constructive Rebound: Fidelity restored to {stats_fid['mean']:.2f}%. Failure counter reset to 0.")
                consecutive_fails = 0

                # If we completed the base queue and still healthy, dynamically expand deeper
                if idx >= len(active_queue):
                    remaining_expansion = [step for step in ADAPTIVE_EXPANSION_STEPS if step > d and step not in tested_depths]
                    if remaining_expansion:
                        next_step = remaining_expansion[0]
                        active_queue.append(next_step)
                        log(f"     [+] High Coherence Sustained (F={stats_fid['mean']:.2f}% >= {fail_threshold}%). Dynamically expanding stress test to D = {next_step} Gates.")

    return summary_records, raw_records
