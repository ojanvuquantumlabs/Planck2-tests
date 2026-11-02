#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
NIST-Compliant Statistical Analysis Engine
"""

import math
import statistics

# Precomputed two-sided Student's t critical values for 95% confidence (alpha = 0.05)
STUDENT_T_TABLE = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    30: 2.042,
    50: 2.009,
    100: 1.984
}

def get_student_t_critical(degrees_of_freedom):
    """Returns the two-sided 95% Student's t critical value."""
    if degrees_of_freedom <= 0:
        return 1.960
    if degrees_of_freedom in STUDENT_T_TABLE:
        return STUDENT_T_TABLE[degrees_of_freedom]
    if degrees_of_freedom > 100:
        return 1.960
    # Linear interpolation for values between keys
    keys = sorted(STUDENT_T_TABLE.keys())
    for i in range(len(keys) - 1):
        k1, k2 = keys[i], keys[i + 1]
        if k1 <= degrees_of_freedom <= k2:
            frac = (degrees_of_freedom - k1) / (k2 - k1)
            return STUDENT_T_TABLE[k1] + frac * (STUDENT_T_TABLE[k2] - STUDENT_T_TABLE[k1])
    return 1.960

def compute_nist_metrics(data_series):
    """
    Computes complete NIST-compliant statistical metrics for a numeric data series.
    Returns:
        dict containing mean, std_dev, sem, ci_low, ci_high, cv_pct, min_val, max_val, n
    """
    n = len(data_series)
    if n == 0:
        return {
            "n": 0, "mean": 0.0, "std_dev": 0.0, "sem": 0.0,
            "ci_95_low": 0.0, "ci_95_high": 0.0, "cv_pct": 0.0,
            "min_val": 0.0, "max_val": 0.0
        }
    
    mean = statistics.mean(data_series)
    std_dev = statistics.stdev(data_series) if n > 1 else 0.0
    sem = std_dev / math.sqrt(n) if n > 1 else 0.0
    
    df = n - 1
    t_val = get_student_t_critical(df) if df > 0 else 1.960
    
    ci_low = mean - t_val * sem
    ci_high = mean + t_val * sem
    cv_pct = (std_dev / abs(mean) * 100.0) if mean != 0 else 0.0
    
    return {
        "n": n,
        "mean": mean,
        "std_dev": std_dev,
        "sem": sem,
        "ci_95_low": ci_low,
        "ci_95_high": ci_high,
        "cv_pct": cv_pct,
        "min_val": min(data_series),
        "max_val": max(data_series)
    }

def compute_quantum_volume_z_score(heavy_counts, total_shots, threshold=2.0/3.0):
    """
    Computes Z-score for Quantum Volume certification (Cross et al., 2019).
    H_0: p <= 2/3 vs H_1: p > 2/3.
    """
    if total_shots <= 0:
        return 0.0, False
    p_obs = heavy_counts / total_shots
    sigma = math.sqrt(threshold * (1.0 - threshold) / total_shots)
    z_score = (p_obs - threshold) / sigma if sigma > 0 else 0.0
    is_certified = (z_score > 2.0) and (p_obs > threshold)
    return z_score, is_certified
