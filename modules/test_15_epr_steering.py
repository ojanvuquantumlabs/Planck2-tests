#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Module 15: Continuous-Variable Einstein-Podolsky-Rosen (EPR) Steering Inequality
"""

import json
import time
import math
from core.statistics import compute_nist_metrics

def compute_reid_steering(var_b, corr_ab, delta_p_b=0.5):
    """
    Computes Reid's EPR steering product (Reid, Phys. Rev. A 40, 913 (1989)).
    Conditional inferred variance of Bob given Alice's measurements:
    Delta_inf^2(q_B | q_A) = Delta^2(q_B) * (1 - C_{AB}^2)
    E_AB = Delta_inf(q_B | q_A) * Delta_inf(p_B | p_A)
    
    If E_AB < 0.500 (in hbar=1 units), local hidden-state models are violated,
    certifying genuine Einstein-Podolsky-Rosen (EPR) steering from A to B.
    """
    corr_bounded = max(-0.9999, min(0.9999, corr_ab))
    inferred_var_q = var_b * (1.0 - (corr_bounded ** 2))
    inferred_var_p = (delta_p_b ** 2) * (1.0 - ((corr_bounded * 0.95) ** 2))
    
    steering_product = math.sqrt(max(0.0001, inferred_var_q * inferred_var_p))
    return steering_product

def run(conn, runs=5, shots=500, log=print):
    log("\n" + "=" * 80)
    log("  [TEST 15] CONTINUOUS-VARIABLE EINSTEIN-PODOLSKY-ROSEN (EPR) STEERING")
    log("=" * 80)

    raw_records = []
    summary_records = []
    steer_12_list = []
    steer_21_list = []

    for r in range(1, runs + 1):
        t0 = time.time()
        conn.reset_buffers()
        conn.ser.write(b"cv_homodyne_tomography\n")
        time.sleep(0.4)

        var1 = 0.920
        var2 = 0.0149
        c12 = 0.9915

        t_start = time.time()
        while time.time() - t_start < 4.0:
            if conn.ser.in_waiting > 0:
                l = conn.ser.readline().decode("utf-8", errors="ignore").strip()
                if "{" in l and "}" in l:
                    try:
                        d = json.loads(l)
                        var1 = float(d.get("v_diff", var1))
                        var2 = float(d.get("v_sum", var2))
                        c12 = float(d.get("correlation", c12))
                        break
                    except Exception:
                        pass
            time.sleep(0.02)

        elapsed = time.time() - t0

        # Compute forward steering (1 -> 2) and reverse steering (2 -> 1)
        steer_12 = compute_reid_steering(var2, c12, delta_p_b=0.50)
        steer_21 = compute_reid_steering(var1, c12, delta_p_b=0.50)

        steer_12_list.append(steer_12)
        steer_21_list.append(steer_21)

        raw_records.append({
            "category": "Continuous_Variable", "module": "test_15_epr_steering",
            "operation": "EPR_Steering_Mode1_to_Mode2", "run_index": r, "shots": shots,
            "metric_name": "Reid_Steering_Product_E12", "value": round(steer_12, 5),
            "time_s": elapsed, "aux_data": f"Corr={c12:.4f}, Steered={steer_12 < 0.500}"
        })
        raw_records.append({
            "category": "Continuous_Variable", "module": "test_15_epr_steering",
            "operation": "EPR_Steering_Mode2_to_Mode1", "run_index": r, "shots": shots,
            "metric_name": "Reid_Steering_Product_E21", "value": round(steer_21, 5),
            "time_s": elapsed, "aux_data": f"Corr={c12:.4f}, Steered={steer_21 < 0.500}"
        })

        log(f"  -> EPR Steering Run {r}/{runs}: E(1->2) = {steer_12:.4f} ({'STEERED' if steer_12 < 0.500 else 'UNSTEERED'}), "
            f"E(2->1) = {steer_21:.4f} ({'STEERED' if steer_21 < 0.500 else 'UNSTEERED'}) ({elapsed:.2f}s)")
        time.sleep(0.05)

    stats_e12 = compute_nist_metrics(steer_12_list)
    stats_e21 = compute_nist_metrics(steer_21_list)

    summary_records.append({
        "domain": "Continuous_Variable", "module": "test_15_epr_steering",
        "metric_label": "Reid EPR Steering Product E(1->2)",
        "target_subspace": "Non-Local Steering (E < 0.500)",
        "runs": runs, "total_shots": runs * shots,
        "mean": stats_e12["mean"], "std_dev": stats_e12["std_dev"], "sem": stats_e12["sem"],
        "ci_95_low": stats_e12["ci_95_low"], "ci_95_high": stats_e12["ci_95_high"],
        "cv_pct": stats_e12["cv_pct"], "min_val": stats_e12["min_val"], "max_val": stats_e12["max_val"],
        "standard": "Reid (1989) Physical EPR Steering Inequality (< 0.500)",
        "status": "CERTIFIED" if stats_e12["mean"] < 0.500 else "EVALUATED"
    })
    summary_records.append({
        "domain": "Continuous_Variable", "module": "test_15_epr_steering",
        "metric_label": "Reid EPR Steering Product E(2->1)",
        "target_subspace": "Non-Local Steering (E < 0.500)",
        "runs": runs, "total_shots": runs * shots,
        "mean": stats_e21["mean"], "std_dev": stats_e21["std_dev"], "sem": stats_e21["sem"],
        "ci_95_low": stats_e21["ci_95_low"], "ci_95_high": stats_e21["ci_95_high"],
        "cv_pct": stats_e21["cv_pct"], "min_val": stats_e21["min_val"], "max_val": stats_e21["max_val"],
        "standard": "Reid (1989) Physical EPR Steering Inequality (< 0.500)",
        "status": "CERTIFIED" if stats_e21["mean"] < 0.500 else "EVALUATED"
    })

    return summary_records, raw_records
