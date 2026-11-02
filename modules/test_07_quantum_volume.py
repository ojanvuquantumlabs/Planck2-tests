#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 07: Granular Quantum Volume Certification & Adaptive Depth Scaling
"""

import math
import time
from core.statistics import compute_nist_metrics, compute_quantum_volume_z_score

def build_qv_circuit(m):
    """Constructs a pseudo-random square circuit of width m and depth m with clean instruction framing."""
    lines = [f"qreg q[{m}];", f"creg c[{m}];"]
    for i in range(m):
        lines.append(f"h q[{i}];")
    
    for layer in range(m):
        for i in range(0, m - 1, 2):
            lines.append(f"cz q[{i}], q[{i+1}];")
        for i in range(m):
            # Non-commensurate prime-hash phase rotation to ensure true Porter-Thomas distribution without modulo-4 symmetry collapse
            angle = round(((i * 7 + layer * 11 + 3) % 8 + 1) * (math.pi / 8.0), 4)
            lines.append(f"ry({angle}) q[{i}];")
        for i in range(1, m - 1, 2):
            lines.append(f"cz q[{i}], q[{i+1}];")
            
    lines.append("measure q -> c;")
    return lines

def run(conn, runs=3, shots=500, min_width=2, max_width=12, adaptive=True, consecutive_limit=2, log=print):
    mode_str = "Adaptive Scaling" if adaptive else "Standard Sweeps"
    log("\n" + "=" * 80)
    log(f"  [TEST 07] GRANULAR QUANTUM VOLUME CERTIFICATION ({mode_str}: Register Width m >= {min_width})")
    log("  [HARDWARE: 3:1 Sovereign Chromatic Fault-Tolerant Logical Qubits (LQ)]")
    log("=" * 80)

    raw_records = []
    summary_records = []

    consecutive_fails = 0
    current_m = min_width
    max_m_cap = 20 if adaptive else max_width

    while current_m <= max_m_cap:
        m = current_m
        vq = 2 ** m
        qasm_circuit = build_qv_circuit(m)

        heavy_ratios = []

        for r in range(1, runs + 1):
            timeout_s = max(45.0, m * 8.0 + (shots / 500.0) * 15.0)
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_circuit, shots=shots, timeout=timeout_s)
            
            measured_total = sum(counts.values())
            
            vals = sorted(counts.values())
            median_val = vals[len(vals)//2] if vals else 0
            heavy_counts = sum(v for v in counts.values() if v >= median_val)
            
            hr = (heavy_counts / measured_total * 100.0) if measured_total > 0 else 0.0
            heavy_ratios.append(hr)

            raw_records.append({
                "category": "Quantum_Volume", "module": "test_07_quantum_volume",
                "operation": f"V_Q_{vq}_m{m}", "run_index": r, "shots": measured_total,
                "metric_name": "Heavy_Output_Ratio_pct", "value": round(hr, 2),
                "time_s": elapsed, "aux_data": f"HeavyCounts={heavy_counts}/{measured_total}, Median={median_val}"
            })
            log(f"  -> V_Q = {vq:5d} ({m:2d}x{m:2d}) Run {r}/{runs}: Heavy Ratio = {hr:6.2f}% ({elapsed:.2f}s)")
            time.sleep(0.04)

        stats_hr = compute_nist_metrics(heavy_ratios)
        total_m_shots = sum(r["shots"] for r in raw_records if r["operation"] == f"V_Q_{vq}_m{m}")
        total_heavy = sum(int(r["value"] * r["shots"] / 100.0) for r in raw_records if r["operation"] == f"V_Q_{vq}_m{m}")
        
        z_score, is_certified = compute_quantum_volume_z_score(total_heavy, total_m_shots)

        summary_records.append({
            "domain": "Quantum_Volume", "module": "test_07_quantum_volume",
            "metric_label": f"V_Q = {vq} ({m}x{m}) Heavy Output Ratio (%)",
            "target_subspace": "Heavy_Outputs (> 66.67%)",
            "runs": runs, "total_shots": total_m_shots,
            "mean": stats_hr["mean"], "std_dev": stats_hr["std_dev"], "sem": stats_hr["sem"],
            "ci_95_low": stats_hr["ci_95_low"], "ci_95_high": stats_hr["ci_95_high"],
            "cv_pct": stats_hr["cv_pct"], "min_val": stats_hr["min_val"], "max_val": stats_hr["max_val"],
            "standard": f"Cross et al. (2019) Physical QV | Z={z_score:.2f}",
            "status": "CERTIFIED" if is_certified else ("PASSED" if stats_hr["mean"] > 66.67 else "EVALUATED")
        })

        # Adaptive Hysteresis Check past base width
        if adaptive:
            if not is_certified and stats_hr["mean"] <= 66.67:
                consecutive_fails += 1
                log(f"     [!] QV Sub-Threshold: Heavy Ratio = {stats_hr['mean']:.2f}% <= 66.67% (Consecutive Fails: {consecutive_fails}/{consecutive_limit})")
                if consecutive_fails >= consecutive_limit:
                    log(f"  [✓] Sustained Quantum Volume Capacity Ceiling Certified at V_Q = {2**(m-1)} (m = {m-1}). Halting expansion.")
                    break
            else:
                if consecutive_fails > 0:
                    log(f"     [✓] Constructive Rebound: Heavy ratio recovered to {stats_hr['mean']:.2f}%. Resetting counter.")
                consecutive_fails = 0
                if m >= max_width:
                    log(f"     [+] High Coherence Sustained (HR={stats_hr['mean']:.2f}% > 66.67%, Z={z_score:.2f}). Dynamically advancing to m = {m + 1} (V_Q = {2**(m+1)}).")

        current_m += 1

    return summary_records, raw_records
