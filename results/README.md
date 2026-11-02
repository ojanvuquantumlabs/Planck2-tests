# Ojanvu Planck 2 Test Results Archive

This directory stores execution logs, atomic measurements, and statistical summaries produced by the Planck 2 Hardware Test Suite.

## Reference Dataset (`results/latest/`)

The `latest/` directory contains the official NIST-grade reference baseline dataset acquired on calibrated physical Planck 2 hardware:
- **`battery_report.json`**: Machine-readable JSON summary of all 22 test modules, containing 140 statistical summary metrics and 283,663 physical shots.
- **`statistical_summary.csv`**: Comprehensive metric table including sample size, mean, sample standard deviation ($s$), standard error of the mean (SEM), 95% confidence intervals, coefficient of variation ($CV\%$), and pass/fail certification status.
- **`raw_measurements.csv`**: Atomic run-by-run records for full statistical recreation.
- **`BATTERY_REPORT.md`**: Executive markdown report with formatted performance tables and architectural verification summaries.
- **`battery_execution.log`**: Complete execution console trace and hardware serial transaction logs.

## Timestamped Runs (`results/YYYYMMDD_HHMMSS/`)

When you run the battery suite on your own hardware (`python3 run_battery.py`), a new timestamped directory is created for each run. These local runs are ignored by git to keep your repository clean.
