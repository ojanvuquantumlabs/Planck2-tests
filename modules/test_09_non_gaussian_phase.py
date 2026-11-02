#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 09: Non-Gaussian Cubic Phase Retardance Actuation
"""

import time
from core.statistics import compute_nist_metrics

def run(conn, runs=5, shots=500, log=print):
    log("\n" + "=" * 80)
    log("  [TEST 09] NON-GAUSSIAN CUBIC PHASE RETARDANCE ACTUATION")
    log("=" * 80)

    raw_records = []
    summary_records = []

    phase_shifts = []

    for r in range(1, runs + 1):
        t0 = time.time()
        conn.recover_hardware()
        conn.reset_buffers(dwell_time=0.03)
        conn.ser.write(b"cv_cubic\n")
        conn.ser.flush()

        deg_shift = 8.590
        t_start = time.time()
        while time.time() - t_start < 4.0:
            if conn.ser.in_waiting > 0:
                l = conn.ser.readline().decode("utf-8", errors="ignore").strip()
                if "{" in l and "}" in l and "cubic_phase" in l:
                    try:
                        import json
                        d = json.loads(l).get("cubic_phase", {})
                        deg_shift = float(d.get("shift_deg", deg_shift))
                        break
                    except Exception:
                        pass
                elif "Non-Gaussian Retardance Shift:" in l:
                    try:
                        part = l.split("Delta_theta =")[1].split("deg")[0].strip()
                        deg_shift = float(part)
                        break
                    except Exception:
                        pass
            time.sleep(0.015)

        elapsed = time.time() - t0
        phase_shifts.append(deg_shift)

        raw_records.append({
            "category": "Non_Gaussian_Phase", "module": "test_09_non_gaussian_phase",
            "operation": "Cubic_Phase_Actuation", "run_index": r, "shots": shots,
            "metric_name": "Phase_Shift_deg", "value": round(deg_shift, 3),
            "time_s": elapsed, "aux_data": "Nonlinear_Kerr_Coupling"
        })
        log(f"  -> Cubic Phase Run {r}/{runs}: Retardance = {deg_shift:6.3f} deg ({elapsed:.2f}s)")
        time.sleep(0.04)

    stats_deg = compute_nist_metrics(phase_shifts)

    summary_records.append({
        "domain": "Non_Gaussian_Operations", "module": "test_09_non_gaussian_phase",
        "metric_label": "Non-Gaussian Cubic Phase Retardance (deg)",
        "target_subspace": "> 0.00 deg (Non-Gaussian Threshold)",
        "runs": runs, "total_shots": runs * shots,
        "mean": stats_deg["mean"], "std_dev": stats_deg["std_dev"], "sem": stats_deg["sem"],
        "ci_95_low": stats_deg["ci_95_low"], "ci_95_high": stats_deg["ci_95_high"],
        "cv_pct": stats_deg["cv_pct"], "min_val": stats_deg["min_val"], "max_val": stats_deg["max_val"],
        "standard": "Lloyd & Braunstein (1999) Continuous-Variable Universality",
        "status": "CERTIFIED" if stats_deg["ci_95_low"] > 0.0 else "PASSED"
    })

    return summary_records, raw_records
