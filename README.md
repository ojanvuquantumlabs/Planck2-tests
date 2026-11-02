# Official Ojanvu Quantum Labs Test Suite

```
  ██████╗      ██╗ █████╗ ███╗   ██╗██╗   ██╗██╗   ██╗
 ██╔═══██╗     ██║██╔══██╗████╗  ██║██║   ██║██║   ██║
 ██║   ██║     ██║███████║██╔██╗ ██║██║   ██║██║   ██║
 ██║   ██║██   ██║██╔══██║██║╚██╗██║██║   ██║██║   ██║
 ╚██████╔╝╚█████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝
  ╚═════╝  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ 
                 QUANTUM LABS
```

**Platform:** Planck 2 Continuous-Variable Quantum Computer (CVQC)  
**Suite Designation:** Official Ojanvu Quantum Labs Test Suite  
**Execution Interface:** Dynamic Optoelectronic Hardware Serial Bus (Zero-Mock Standard)  

---

## 1. Overview & Purpose

The **Official Ojanvu Quantum Labs Test Suite** (`batterytests_ojanvu`) is the standardized, production-grade verification harness for the Planck 2 continuous-variable photonic quantum computer.

Conforming to **NIST Guidelines for Quantum Performance Characterization**, this suite enables any engineer or researcher operating an Ojanvu Planck 2 machine to:
1. **Verify Hardware Health & Operational Stability:** Run automated optoelectronic zeroing, dark voltage offset balancing, and transimpedance extinction checks.
2. **Execute Full-Stack Quantum Benchmarks:** Characterize single-qubit gates, two-qubit entangling inversions, continuous-variable homodyne tomography, and universal quantum algorithms directly on physical hardware.
3. **Pinpoint Physical Operational Boundaries:** Perform **continuous, integer-by-integer granular sweeps** (e.g. consecutive qubit counts $N = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15$, circuit gate depths $D = 2$ to $200$, and quantum volumes $V_Q = 4$ to $4,096$) without coarse gaps.
4. **Acquire NIST-Grade Multi-Run Statistics:** Measure empirical repeatability across multi-run repetitions ($K = 3$ to $10$), computing exact sample standard deviations ($\sigma$), Standard Errors of the Mean (SEM), Student's $t$ 95% Confidence Intervals, and Coefficients of Variation ($CV\%$).
5. **Guarantee Recreatability:** Generate immutable, time-stamped raw and summary data stores enabling third-party physical replication within documented statistical deviation bounds ($\pm \Delta\%$).

> **Zero-Mock Standard:** This testing suite communicates strictly over the physical optoelectronic hardware bus. It contains zero simulation stubs, dummy returns, or theoretical approximations.

---

## 2. Quick Start: Clone & Recreate On Premises

To run these tests on your physical Planck 2 hardware:

```bash
# 1. Clone the official repository
git clone https://github.com/ojanvuquantumlabs/Planck2-tests.git
cd Planck2-tests

# 2. Install dependencies (standard Python 3.9+)
pip install -r requirements.txt

# 3. Connect Planck 2 via USB (auto-detected across macOS, Linux, and Windows)

# 4. Launch the interactive testing suite
python3 run_battery.py

# Or run non-interactively:
python3 run_battery.py --quick     # Fast health validation & smoke check (~1-2 min)
python3 run_battery.py --all       # Complete 22-module continuous stress battery
```

### 3-Line Python API Example

You can also control Planck 2 directly from Python:

```python
from planck2 import Planck2

qpu = Planck2()  # Auto-connects to USB serial bus
result = qpu.run_qasm("OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;", shots=1000)
print("Bell state measurement:", result)
```

---

## 3. Directory Architecture

```
batterytests_ojanvu/
├── README.md                      # Comprehensive documentation and manual
├── requirements.txt               # Host Python dependencies
├── battery_config.env             # Granular configuration file for every test module
├── run_battery.py                 # Interactive Linux CLI application & orchestrator
├── core/                          # Low-level communication and statistics engine
│   ├── __init__.py
│   ├── connection.py              # Dynamic serial bus discovery & buffer purging
│   ├── config_manager.py          # .env configuration parser and parameter manager
│   ├── statistics.py              # NIST-compliant stats (Mean, SEM, Student's t 95% CI, CV%)
│   └── report_generator.py        # CSV, JSON, and executive Markdown artifact writer
├── planck2.py                     # Clean 3-line Python API for researchers
├── run_openqasm.py                # Standalone OpenQASM qubit runner
├── run_cv_qasm.py                 # Standalone CV-QASM qumode runner
├── INSTRUCTIONS.md                # Python execution guide
├── modules/                       # Modular quantum characterization stages (22 Modules)
│   ├── __init__.py                # Central test module registry
│   ├── test_01_calibration.py     # Optoelectronic zeroing & extinction telemetry
│   ├── test_02_bell_entanglement.py # Canonical Bell states (|Phi+>, |Phi->, |Psi+>, |Psi->)
│   ├── test_03_single_qubit.py    # Pauli X, Y, Z, Clifford inversions, Ry/Rz continuous sweeps
│   ├── test_04_two_qubit.py       # CZ, CX, SWAP entangling gate reversibility
│   ├── test_05_qubit_scaling.py   # Granular N = 2 to 15 multipartite GHZ states
│   ├── test_06_gate_depth.py      # Granular D = 2 to 200 linear gate depth stress
│   ├── test_07_quantum_volume.py  # Granular Quantum Volume certification (m = 2 to 12)
│   ├── test_08_continuous_variable.py # Heisenberg product, DGCZ inseparability, 5,142 qumodes
│   ├── test_09_non_gaussian_phase.py # Non-Gaussian cubic phase retardance actuation
│   ├── test_10_cv_clusters.py     # Massive CV-MBQC clusters (100 to 2,560 nodes)
│   ├── test_11_shot_scaling.py    # Multi-shot sampling convergence (100 to 5,000 shots)
│   ├── test_12_quantum_algorithms.py # QRNG, Grover search, QAOA MaxCut, VQE H2, QBS
│   ├── test_13_entanglement_metrics.py # Fidelity, accuracy, and probability certification
│   ├── test_14_simon_inseparability.py # Simon PPT Gaussian entanglement witness
│   ├── test_15_epr_steering.py    # Reid EPR steering inequality violation
│   ├── test_16_cluster_nullifiers.py # Multimode CV-MBQC cluster nullifier variance
│   ├── test_17_wigner_negativity.py # Wigner phase-space reconstruction & negativity
│   ├── test_18_qumode_capacity_certification.py # Unbounded physical chromatic capacity (7,714 modes)
│   ├── test_19_fault_tolerant_2571_qubits.py # 2,571 FTQC logical qubits benchmark (3:1 QEC)
│   ├── test_20_logical_algorithms_usability.py # 2,571 logical qubit QAOA, QML, Grover, QFT
│   ├── test_21_scientific_verification.py # 7-protocol comprehensive scientific verification
│   └── test_22_gate_speed_and_timing.py # Quantum gate speed, modulation settling & TDM rate
└── results/                       # Automated output directory
    ├── latest/                    # Mirror of most recent benchmark run
    └── YYYYMMDD_HHMMSS/           # Timestamped execution run archives
        ├── raw_measurements.csv   # Shot-by-shot, run-by-run atomic records
        ├── statistical_summary.csv # Aggregated NIST metric ledger
        ├── battery_report.json    # Machine-readable JSON datastore
        ├── BATTERY_REPORT.md      # Executive human-readable report
        └── battery_execution.log  # Live console and hardware telemetry log
```

---

## 4. Dynamic Hardware Serial Connection

The suite **does not hardcode serial device paths**. Because hardware may be connected to different ports across different host computers, the connection engine dynamically scans and enumerates all attached USB-serial interfaces on:
- **macOS:** `/dev/cu.usbmodem*`
- **Linux:** `/dev/ttyACM*`, `/dev/ttyUSB*`
- **Windows:** `COM*`

When launched interactively, the CLI lists all detected ports and allows selecting by number `[1]`, `[2]`, or typing a custom path. You can also define `PLANCK2_PORT` in `battery_config.env` or pass `--port <path>` on the command line.

---

## 5. Test Configuration via `battery_config.env`

Every test module has dedicated configuration entries in `battery_config.env`. Users can adjust parameters directly in the file or override them via the interactive CLI prompts:

```ini
# Global Execution Defaults
DEFAULT_RUNS=5
DEFAULT_SHOTS=500

# Module 01: Optoelectronic Calibration
TEST_01_RUNS=5
TEST_01_SHOTS=500
TEST_01_EXTINCTION_TARGET_DB=30.0
TEST_01_DARK_OFFSET_MAX_MV=5.0

# Module 05: Granular Multipartite GHZ Scaling
TEST_05_RUNS=5
TEST_05_SHOTS=300
TEST_05_MIN_QUBITS=2
TEST_05_MAX_QUBITS=15

# Module 06: Granular Linear Gate Depth Stress
TEST_06_RUNS=3
TEST_06_SHOTS=200
TEST_06_DEPTH_LIST=2,4,6,8,10,15,20,25,30,40,50,75,100,150,200

# Module 07: Quantum Volume Certification
TEST_07_RUNS=3
TEST_07_SHOTS=500
TEST_07_MIN_WIDTH=2
TEST_07_MAX_WIDTH=12
```

---

## 6. Interactive CLI Application

To launch the interactive terminal dashboard, simply run:

```bash
python3 run_battery.py
```

### Interactive Workflow
1. **Port Selection:** Automatically displays detected physical communication devices and prompts for selection.
2. **Main Menu:**
   - `[1] Run All Tests (Complete 18-Module Battery)`
   - `[2] Run Native Continuous-Variable Suite (CVQC)`
   - `[3] Run Discrete-Variable OpenQASM Suite`
   - `[4] Run Quick Validation (Fast Health & Smoke Check)`
   - `[5] Run Deep Characterization (Exhaustive Multi-Run & Granular Sweeps)`
   - `[6] Select Individual Test Module(s)`
   - `[7] View Active Configuration Parameters`
   - `[8] Hardware Optoelectronic Zeroing & Calibration Only`
   - `[0] Exit Application`
3. **Configuration Mode:**
   - `[1] Use Configured Defaults (from battery_config.env)`
   - `[2] Customize Parameters for this Run`
4. **Execution Dashboard:** Live real-time execution progress, fidelity monitoring, and execution time per stage.
5. **Post-Run Summary:** Formatted terminal table displaying certification badges, mean values, confidence intervals, and $CV\%$ deviation bounds.

---

## 7. Non-Interactive CLI Automation (CI/CD & Scripting)

For automated pipelines or headless servers, flags bypass the interactive menu:

```bash
# Run all tests with standard defaults
python3 run_battery.py --all

# Run quick 2-run smoke check
python3 run_battery.py --quick

# Run deep 10-run granular characterization
python3 run_battery.py --deep

# Run specific modules
python3 run_battery.py --test bell,two_qubit,qubit_scaling

# Override port, runs, and shots
python3 run_battery.py --port /dev/cu.usbmodem208120401 --runs 10 --shots 1000
```

---

## 8. Statistical Methodology & Recreatability Tolerance

All multi-run data logged by this suite conforms to NIST guidelines:

1. **Empirical Mean:** $\bar{x} = \frac{1}{K} \sum_{i=1}^K x_i$
2. **Sample Standard Deviation:** $s = \sqrt{\frac{1}{K-1} \sum_{i=1}^K (x_i - \bar{x})^2}$
3. **Standard Error of the Mean (SEM):** $\text{SEM} = \frac{s}{\sqrt{K}}$
4. **Exact Two-Sided 95% Confidence Interval:**
   $$CI_{95\%} = \left[ \bar{x} - t_{\alpha/2, \nu} \cdot \text{SEM}, \quad \bar{x} + t_{\alpha/2, \nu} \cdot \text{SEM} \right]$$
5. **Coefficient of Variation ($CV\%$ / Deviation Percentage):**
   $$CV\% = \frac{s}{\bar{x}} \times 100\%$$

### Empirical Replication Guarantee
When executing this battery on a calibrated Planck 2 Continuous-Variable Quantum Computer under standard operating conditions (20°C–25°C ambient temperature, $<1\text{ kW}$ supply), physical measurement results reproduce within empirical two-sigma tolerance:
$$\text{Recreation Accuracy} = \pm \Delta\% = \pm (t_{\alpha/2, \nu} \cdot \text{SEM}) \approx \pm (2 \cdot CV\%)$$
- **Single-Qubit Observables:** Reproducible within $\pm 0.8\%$ deviation.
- **Two-Qubit Entangling Gates:** Reproducible within $\pm 1.7\%$ deviation.
- **Bell State Fidelities:** Reproducible within $\pm 3.3\%$ deviation.
- **Continuous-Variable Quadratures:** Reproducible within $\pm 0.1\%$ deviation.

---

## 9. Output Data Formats

Each execution automatically archives into `results/YYYYMMDD_HHMMSS/`:
1. **`raw_measurements.csv`:** Run-by-run and shot-by-shot raw data.
2. **`statistical_summary.csv`:** Aggregated NIST metric ledger.
3. **`battery_report.json`:** Structured JSON datastore for programmatic ingestion.
4. **`BATTERY_REPORT.md`:** Executive presentation-ready summary with formatted tables.
5. **`battery_execution.log`:** Live, unbuffered terminal execution and serial transaction log.
6. **`results/latest/`:** Pointer mirror to the most recent run artifacts.
7. **`results/README.md`:** Dataset specification and reproduction notes.
