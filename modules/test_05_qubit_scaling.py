#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 05: Granular Multipartite GHZ Qubit Scaling & Adaptive Capacity Hunting
"""

import time
from core.statistics import compute_nist_metrics

def build_ghz_circuit(n):
    """Constructs OpenQASM 2.0 circuit for an n-qubit GHZ state."""
    lines = [f"qreg q[{n}]; creg c[{n}];", "h q[0];"]
    for i in range(n - 1):
        lines.append(f"cx q[{i}], q[{i+1}];")
    lines.append("measure q -> c;")
    return " ".join(lines)

def run(conn, runs=5, shots=300, min_qubits=2, max_qubits=128, adaptive=True, dispersion_threshold=40.0, consecutive_limit=2, qubit_list=None, log=print):
    mode_str = "Adaptive Scaling" if adaptive else "Standard Fixed Sweeps"
    log("\n" + "=" * 80)
    log(f"  [TEST 05] GRANULAR MULTIPARTITE GHZ QUBIT SCALING ({mode_str}: N >= {min_qubits} Qubits)")
    log("=" * 80)

    raw_records = []
    summary_records = []

    consecutive_fails = 0
    
    # Target list generation
    if qubit_list is not None and len(qubit_list) > 0:
        targets = [int(x) for x in qubit_list if int(x) >= 2]
    else:
        hard_qubit_ceiling = max(max_qubits, 30) if adaptive else max_qubits
        targets = []
        n_curr = min_qubits
        while n_curr <= hard_qubit_ceiling:
            targets.append(n_curr)
            if not adaptive:
                n_curr += 1
            else:
                if n_curr < 16:
                    n_curr += 1
                elif n_curr < 30:
                    n_curr += 2
                elif n_curr < 60:
                    n_curr += 5
                elif n_curr < 120:
                    n_curr += 10
                else:
                    n_curr += 25

    for n in targets:
        qasm_circuit = build_ghz_circuit(n)
        t0 = "0" * n
        t1 = "1" * n
        dim_str = f"2^{n}" if n > 30 else f"{2**n}"

        fidelities = []

        for r in range(1, runs + 1):
            timeout_s = max(35.0, min(120.0, n * 2.5 + (shots / 500.0) * 15.0))
            counts, total_s, raw_lines, elapsed = conn.execute_qasm(qasm_circuit, shots=shots, timeout=timeout_s)
            
            c0 = counts.get(t0, 0)
            c1 = counts.get(t1, 0)
            target_counts = c0 + c1
            measured_total = sum(counts.values())

            fid = (target_counts / measured_total * 100.0) if measured_total > 0 else 0.0
            fidelities.append(fid)

            raw_records.append({
                "category": "GHZ_Scaling", "module": "test_05_qubit_scaling",
                "operation": f"GHZ_{n}_Qubits", "run_index": r, "shots": measured_total,
                "metric_name": "GHZ_Fidelity_pct", "value": round(fid, 2),
                "time_s": elapsed, "aux_data": f"HilbertDim={dim_str}, TargetCounts={target_counts}/{measured_total}"
            })
            log(f"  -> GHZ N = {n:3d} Qubits ({dim_str:>8s} Dim) Run {r}/{runs}: Fidelity = {fid:6.2f}% ({elapsed:.2f}s)")
            time.sleep(0.04)

        stats_fid = compute_nist_metrics(fidelities)

        threshold = 50.0 if n <= 10 else (25.0 if n <= 14 else 10.0)
        status = "CERTIFIED" if stats_fid["ci_95_low"] >= 50.0 else ("PASSED" if stats_fid["mean"] > threshold else "EVALUATED")

        summary_records.append({
            "domain": "Multipartite_GHZ", "module": "test_05_qubit_scaling",
            "metric_label": f"{n}-Qubit GHZ State Fidelity ({dim_str} Dim)",
            "target_subspace": f"|0^{n}> + |1^{n}>",
            "runs": runs, "total_shots": sum(r["shots"] for r in raw_records if r["operation"] == f"GHZ_{n}_Qubits"),
            "mean": stats_fid["mean"], "std_dev": stats_fid["std_dev"], "sem": stats_fid["sem"],
            "ci_95_low": stats_fid["ci_95_low"], "ci_95_high": stats_fid["ci_95_high"],
            "cv_pct": stats_fid["cv_pct"], "min_val": stats_fid["min_val"], "max_val": stats_fid["max_val"],
            "standard": "Greenberger, Horne, Zeilinger (1989)",
            "status": status
        })

        # Adaptive Hysteresis Check
        if adaptive:
            if stats_fid["mean"] < dispersion_threshold:
                consecutive_fails += 1
                log(f"     [!] Multi-Qubit Dispersion: Fidelity = {stats_fid['mean']:.2f}% < {dispersion_threshold}% (Consecutive: {consecutive_fails}/{consecutive_limit})")
                if consecutive_fails >= consecutive_limit:
                    log(f"  [✓] Sustained Register Boundary Reached at N = {n} Qubits ({dim_str} Dimensions). Halting scaling.")
                    break
            else:
                if consecutive_fails > 0:
                    log(f"     [✓] Constructive Subspace Rebound: Fidelity recovered to {stats_fid['mean']:.2f}%. Resetting counter.")
                consecutive_fails = 0
                if n >= 15:
                    log(f"     [+] Register Coherence Maintained (F={stats_fid['mean']:.2f}%). Advancing capacity stress testing.")

    return summary_records, raw_records
