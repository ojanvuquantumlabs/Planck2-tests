#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Master Interactive Linux CLI Application & Benchmarking Orchestrator
"""

import sys
import os
import time
import json
import argparse
import shutil

# Ensure local imports work regardless of working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core.connection import Planck2Connection
from core.report_generator import ReportGenerator
from core.config_manager import ConfigManager
from modules import MODULE_REGISTRY

# ANSI Terminal Color Tokens
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

MODULE_TITLES = {
    "calibration": "01. Optoelectronic Calibration & Sensor Telemetry",
    "bell": "02. Canonical Bell State Entanglement (|Phi+>, |Phi->, |Psi+>, |Psi->)",
    "single_qubit": "03. Single-Qubit Gate Stability & Continuous Rotations",
    "two_qubit": "04. Two-Qubit Entangling Inversions (CZ, CX, SWAP)",
    "qubit_scaling": "05. Granular Multipartite GHZ Qubit Scaling (N >= 2 Qubits)",
    "gate_depth": "06. Granular Linear Gate Depth Stress (Circuit Depth D >= 2)",
    "quantum_volume": "07. Granular Quantum Volume Certification (Register Width m >= 2)",
    "continuous_variable": "08. Continuous-Variable Tomography & DGCZ Inseparability",
    "cubic_phase": "09. Non-Gaussian Cubic Phase Retardance Actuation",
    "cv_clusters": "10. Massive CV-MBQC Qubit Cluster Generation",
    "shot_scaling": "11. Continuous Multi-Shot Sampling Convergence",
    "algorithms": "12. Universal Quantum Algorithms (QRNG, Grover, QAOA, VQE, QBS)",
    "entanglement_metrics": "13. Entanglement Fidelity, Accuracy & Probability Certification",
    "simon_inseparability": "14. Simon's Partial Transposition (PPT) Gaussian Entanglement",
    "epr_steering": "15. Reid Einstein-Podolsky-Rosen (EPR) Steering Inequality",
    "cluster_nullifiers": "16. Multimode CV-MBQC Cluster Nullifier Variance Spectrum",
    "wigner_negativity": "17. Wigner Phase-Space Reconstruction & Non-Gaussian Negativity",
    "qumode_capacity_certification": "18. Physical Chromatic Qubit & Qumode Capacity Stress Certification (Unbounded Full-Capacity Suite)",
    "qumode_certification": "18. Physical Chromatic Qubit & Qumode Capacity Stress Certification (Unbounded Full-Capacity Suite)",
    "fault_tolerant_2571_qubits": "19. 2,571 Fault-Tolerant Logical Qubits Benchmark (3:1 Chromatic QEC)",
    "logical_algorithms_usability": "20. 2,571 Logical Qubit Usability & Quantum Algorithms (QAOA, QML, Grover, QFT)",
    "scientific_verification": "21. Comprehensive Scientific Quantum Verification Battery (7 Multi-Protocol Suite)",
    "gate_speeds": "22. Quantum Gate Speed, Latency & Modulation Timing (Physical)",
    "gate_speed": "22. Quantum Gate Speed, Latency & Modulation Timing (Physical)",
}

# Categorized Architectural Test Suites
CV_MODULE_KEYS = [
    "calibration", "continuous_variable", "cubic_phase", "cv_clusters",
    "shot_scaling", "simon_inseparability", "epr_steering",
    "cluster_nullifiers", "wigner_negativity", "qumode_capacity_certification",
    "fault_tolerant_2571_qubits", "scientific_verification"
]

DV_MODULE_KEYS = [
    "bell", "single_qubit", "two_qubit", "qubit_scaling",
    "gate_depth", "quantum_volume", "algorithms", "entanglement_metrics",
    "logical_algorithms_usability"
]

def print_banner():
    banner = f"""{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OFFICIAL OJANVU QUANTUM LABS TEST SUITE                   ║
║         Planck 2 Continuous-Variable Quantum Computer Hardware Battery       ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}"""
    print(banner)

def select_hardware_port_interactive(cfg_port="AUTO"):
    print(f"\n{BOLD}[Step 1/3] Hardware Bus & Communication Port Detection{RESET}")
    print("-" * 78)
    
    available_ports = Planck2Connection.list_available_ports()
    
    if not available_ports:
        print(f"{YELLOW}[!] No serial devices automatically detected on the host system.{RESET}")
        user_port = input(f"Enter hardware serial device path manually [/dev/cu.usbmodem208120401]: ").strip()
        return user_port if user_port else "/dev/cu.usbmodem208120401"

    print("Detected hardware serial interfaces:")
    for idx, p in enumerate(available_ports, 1):
        dev = p['device']
        desc = p['description']
        print(f"  {CYAN}[{idx}]{RESET} {dev:32s} {DIM}({desc}){RESET}")
    print(f"  {CYAN}[M]{RESET} Enter custom device path manually")

    default_idx = "1"
    choice = input(f"\nSelect hardware port [default: 1]: ").strip() or default_idx

    if choice.upper() == "M":
        user_port = input("Enter device path: ").strip()
        return user_port
    
    try:
        val = int(choice)
        if 1 <= val <= len(available_ports):
            return available_ports[val - 1]["device"]
    except ValueError:
        pass

    return available_ports[0]["device"]

def configure_execution_parameters(cfg, module_keys, preset_name="Standard"):
    print(f"\n{BOLD}[Step 3/3] Benchmark Execution Configuration{RESET}")
    print("-" * 78)
    print(f"Active Preset: {GREEN}{preset_name}{RESET}")
    print("  [1] Use Configured Defaults (from battery_config.env)")
    print("  [2] Customize Parameters for this Run")
    
    cfg_choice = input("\nSelect option [default: 1]: ").strip() or "1"
    
    run_params = {
        "runs": cfg.get("DEFAULT_RUNS", 5),
        "shots": cfg.get("DEFAULT_SHOTS", 500),
        "min_qubits": cfg.get("TEST_05_MIN_QUBITS", 2),
        "max_qubits": cfg.get("TEST_05_MAX_QUBITS", 15),
        "depth_list": cfg.get("TEST_06_DEPTH_LIST", [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200]),
        "min_width": cfg.get("TEST_07_MIN_WIDTH", 2),
        "max_width": cfg.get("TEST_07_MAX_WIDTH", 12),
        "tiers": cfg.get("TEST_10_TIERS", [100, 250, 500, 1000, 1500, 2000, 2560]),
        "shot_list": cfg.get("TEST_11_SHOT_LIST", [100, 250, 500, 1000, 2000, 5000]),
        "adaptive": True,
    }

    if cfg_choice == "2":
        print(f"\n{YELLOW}Enter custom parameters (press Enter to keep default):{RESET}")
        try:
            r_in = input(f"  Repetitions per test (Runs) [{run_params['runs']}]: ").strip()
            if r_in: run_params["runs"] = int(r_in)
            
            s_in = input(f"  Default physical shots per circuit [{run_params['shots']}]: ").strip()
            if s_in: run_params["shots"] = int(s_in)

            if "qubit_scaling" in module_keys:
                q_in = input(f"  Max Qubits for GHZ scaling (N=2 to N) [{run_params['max_qubits']}]: ").strip()
                if q_in: run_params["max_qubits"] = int(q_in)

            if "gate_depth" in module_keys or "qubit_scaling" in module_keys or "quantum_volume" in module_keys:
                adapt_in = input(f"  Enable Continuous Stress & Adaptive Scaling? (Y/n) [{'Y' if run_params.get('adaptive', True) else 'n'}]: ").strip().lower()
                run_params["adaptive"] = False if adapt_in == "n" else True

            if "quantum_volume" in module_keys:
                w_in = input(f"  Max Width for Quantum Volume (m=2 to m) [{run_params['max_width']}]: ").strip()
                if w_in: run_params["max_width"] = int(w_in)
        except ValueError as e:
            print(f"{RED}[!] Invalid numeric entry. Retaining defaults.{RESET}")

    return run_params

def interactive_cli():
    print_banner()
    cfg = ConfigManager()

    # Step 1: Resolve Hardware Port
    selected_port = select_hardware_port_interactive(cfg.get("PLANCK2_PORT", "AUTO"))
    print(f"\n{GREEN}[+] Hardware bus assigned to: {selected_port}{RESET}")

    # Check for Interrupted Run Checkpoint
    active_ck = load_battery_checkpoint()
    if active_ck:
        completed_count = len(active_ck.get("completed_keys", []))
        total_count = len(active_ck.get("selected_keys", []))
        next_title = active_ck.get("next_stage_title", "Next Module")
        print(f"\n{YELLOW}{BOLD}" + "=" * 78 + f"{RESET}")
        print(f"{YELLOW}{BOLD}[!] RECOVERY NOTIFICATION: Interrupted Benchmark Run Detected{RESET}")
        print(f"    Run Timestamp:    {active_ck.get('timestamp_str')}")
        print(f"    Completed Stages: {completed_count}/{total_count} ({active_ck.get('last_stage_title')})")
        print(f"    Next Incomplete:  {next_title}")
        print(f"{YELLOW}{BOLD}" + "=" * 78 + f"{RESET}")

        r_choice = input(f"\nDo you want to RESUME execution from {next_title}? (Y/n) [Y]: ").strip().lower()
        if r_choice != "n":
            print(f"\n{GREEN}[+] Resuming benchmark suite execution...{RESET}")
            execute_battery(
                port=selected_port,
                selected_keys=active_ck["selected_keys"],
                run_params=active_ck["run_params"],
                profile_name=active_ck["profile_name"],
                output_dir=active_ck["results_dir"],
                resume_checkpoint=active_ck
            )
            return
        else:
            clear_battery_checkpoint()
            print(f"\n{DIM}[+] Prior checkpoint dismissed. Starting clean benchmark session.{RESET}")

    # Step 2: Main Menu
    while True:
        print(f"\n{BOLD}[Step 2/3] Main Benchmark Workflow Menu{RESET}")
        print("=" * 78)
        print(f"  {CYAN}[1]{RESET} Run Full Hardware Battery (All 21 Modules - CV + DV + Fault-Tolerant)")
        print(f"  {CYAN}[2]{RESET} Run Native Continuous-Variable (CVQC) Suite Only {GREEN}(12 Physical Optical Modules, Zero Statevectors){RESET}")
        print(f"  {CYAN}[3]{RESET} Run Discrete-Variable (OpenQASM) Suite Only {YELLOW}(9 Hybrid Co-Processor Modules){RESET}")
        print(f"  {CYAN}[4]{RESET} Run Quick Validation (Fast Health & Smoke Check)")
        print(f"  {CYAN}[5]{RESET} Run Deep Characterization (Exhaustive Multi-Run & Granular Sweeps)")
        print(f"  {CYAN}[6]{RESET} Select Individual Test Module(s)")
        print(f"  {CYAN}[7]{RESET} View Active Configuration Parameters")
        print(f"  {CYAN}[8]{RESET} Hardware Optoelectronic Zeroing & Calibration Only")
        print(f"  {CYAN}[9]{RESET} Run Physical Chromatic Capacity Stress Suite {GREEN}{BOLD}(7,714 Physical Modes){RESET}")
        print(f"  {CYAN}[10]{RESET} Run 2,571 Fault-Tolerant Logical Qubits Benchmark {GREEN}{BOLD}(3:1 Chromatic QEC){RESET}")
        print(f"  {CYAN}[11]{RESET} Run 2,571 Logical Qubit Usability & Algorithms {YELLOW}{BOLD}(QAOA, QML, Grover, QFT){RESET}")
        print(f"  {CYAN}[12]{RESET} Run Comprehensive Scientific Verification Battery {CYAN}{BOLD}(7 Evidence Protocols){RESET}")
        print(f"  {CYAN}[0]{RESET} Exit Application")
        print("=" * 78)

        choice = input("\nEnter selection [1-12, 0 to exit]: ").strip()

        if choice == "0":
            print(f"\n{YELLOW}Exiting Ojanvu Test Suite. Goodbye!{RESET}\n")
            sys.exit(0)

        elif choice == "1":
            selected_modules = list(MODULE_REGISTRY.keys())
            run_params = configure_execution_parameters(cfg, selected_modules, preset_name="Continuous Stress Battery (All 18 Modules)")
            run_params["adaptive"] = True
            print(f"\n{GREEN}[+] Full 18-Module Continuous Stress Battery loaded (Adaptive scaling to sustained hardware exhaustion).{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="FULL_STRESS_BATTERY")
            break

        elif choice == "2":
            selected_modules = [k for k in CV_MODULE_KEYS if k in MODULE_REGISTRY]
            run_params = configure_execution_parameters(cfg, selected_modules, preset_name="Native Continuous-Variable Suite")
            run_params["adaptive"] = True
            print(f"\n{GREEN}[+] Native Continuous-Variable (CVQC) Suite loaded (10 Physical Optical Modules, Zero Statevectors).{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="CVQC_NATIVE_SUITE")
            break

        elif choice == "3":
            selected_modules = [k for k in DV_MODULE_KEYS if k in MODULE_REGISTRY]
            run_params = configure_execution_parameters(cfg, selected_modules, preset_name="Discrete-Variable OpenQASM Suite")
            run_params["adaptive"] = True
            print(f"\n{YELLOW}[+] Discrete-Variable (OpenQASM) Suite loaded (8 Hybrid Co-Processor Modules).{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="DV_QASM_HYBRID_SUITE")
            break

        elif choice == "4":
            selected_modules = list(MODULE_REGISTRY.keys())
            run_params = {
                "runs": 2, "shots": 200, "min_qubits": 2, "max_qubits": 8, "adaptive": False,
                "depth_list": [2, 4, 8, 15, 30, 50, 100], "min_width": 2, "max_width": 6,
                "tiers": [100, 250, 500, 1000], "shot_list": [100, 500, 1000]
            }
            print(f"\n{GREEN}[+] Quick Validation Profile loaded (2 runs, reduced parameters).{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="QUICK_VALIDATION")
            break

        elif choice == "5":
            selected_modules = list(MODULE_REGISTRY.keys())
            run_params = {
                "runs": 10, "shots": 500, "min_qubits": 2, "max_qubits": 20, "adaptive": True,
                "depth_list": [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200],
                "min_width": 2, "max_width": 16, "tiers": [100, 250, 500, 1000, 1500, 2000, 2560],
                "shot_list": [100, 250, 500, 1000, 2000, 5000]
            }
            print(f"\n{GREEN}[+] Deep Characterization Profile loaded (10 runs, full granular sweeps with adaptive stress hunting).{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="DEEP_CHARACTERIZATION")
            break

        elif choice == "6":
            print(f"\n{BOLD}Available Quantum Test Modules by Architecture:{RESET}")
            keys_list = list(MODULE_REGISTRY.keys())
            
            print(f"\n  {GREEN}{BOLD}--- Native Continuous-Variable (CVQC) Modules (100% Physical Optical Hardware) ---{RESET}")
            for idx, k in enumerate(keys_list, 1):
                if k in CV_MODULE_KEYS:
                    print(f"  {CYAN}[{idx:2d}]{RESET} {MODULE_TITLES[k]}")

            print(f"\n  {YELLOW}{BOLD}--- Discrete-Variable (OpenQASM) Modules (Hybrid Co-Processor Layer) ---{RESET}")
            for idx, k in enumerate(keys_list, 1):
                if k in DV_MODULE_KEYS:
                    print(f"  {CYAN}[{idx:2d}]{RESET} {MODULE_TITLES[k]}")

            print(f"\n  {DIM}Tips: Enter 'cv' for all CV tests, 'dv' for all DV tests, or numbers (e.g. 1,8,10,14,15,16,17):{RESET}")
            sel_in = input("\nEnter selection: ").strip().lower()
            chosen_keys = []
            if sel_in == "cv":
                chosen_keys = [k for k in CV_MODULE_KEYS if k in MODULE_REGISTRY]
            elif sel_in == "dv":
                chosen_keys = [k for k in DV_MODULE_KEYS if k in MODULE_REGISTRY]
            else:
                for item in sel_in.split(","):
                    item = item.strip()
                    if item.isdigit():
                        num = int(item)
                        if 1 <= num <= len(keys_list):
                            chosen_keys.append(keys_list[num - 1])

            if not chosen_keys:
                print(f"{RED}[!] No valid modules chosen. Returning to main menu.{RESET}")
                continue

            run_params = configure_execution_parameters(cfg, chosen_keys, preset_name="Custom Selection")
            run_params["adaptive"] = True
            execute_battery(selected_port, chosen_keys, run_params, profile_name="CUSTOM_SELECTION")
            break

        elif choice == "7":
            print(f"\n{BOLD}Active Configuration File ({CONFIG_FILE_NAME}):{RESET}")
            print("-" * 78)
            for k, v in cfg.config.items():
                print(f"  {CYAN}{k:30s}{RESET} = {v}")
            input(f"\n{DIM}Press Enter to return to main menu...{RESET}")

        elif choice == "8":
            print(f"\n{GREEN}[+] Initializing Hardware Connection for Optoelectronic Zeroing...{RESET}")
            conn = Planck2Connection(port=selected_port, baudrate=115200, timeout=6.0)
            conn.connect()
            print("    [+] Zeroing phase modulators and locking transimpedance amplifiers...")
            conn.calibrate()
            print(f"{GREEN}    [✓] Optoelectronic core calibrated successfully.{RESET}")
            conn.disconnect()
            input(f"\n{DIM}Press Enter to return to main menu...{RESET}")

        elif choice == "9":
            selected_modules = ["qumode_capacity_certification"]
            run_params = {
                "runs": 3,
                "shots": 500,
                "target_qumodes": 7714,
                "adaptive": False
            }
            print(f"\n{GREEN}{BOLD}[+] Launching Physical Chromatic Qubit & Qumode Capacity Stress Suite (7,714+ Physical Modes & Qubits)...{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="PHYSICAL_CHROMATIC_CAPACITY_STRESS_SUITE")
            break

        elif choice == "10":
            selected_modules = ["fault_tolerant_2571_qubits"]
            run_params = {"runs": 1, "shots": 2571, "adaptive": False}
            print(f"\n{GREEN}{BOLD}[+] Launching 2,571 Fault-Tolerant Logical Qubits Benchmark Suite (3:1 Sovereign Chromatic QEC)...{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="FAULT_TOLERANT_2571_QUBITS_SUITE")
            break

        elif choice == "11":
            selected_modules = ["logical_algorithms_usability"]
            run_params = {"runs": 1, "shots": 2571, "adaptive": False}
            print(f"\n{YELLOW}{BOLD}[+] Launching 2,571 Logical Qubit Usability & Quantum Algorithms Suite (QAOA, QML, Grover, QFT)...{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="LOGICAL_ALGORITHMS_USABILITY_SUITE")
            break

        elif choice == "12":
            selected_modules = ["scientific_verification"]
            run_params = {"runs": 1, "shots": 5000, "adaptive": False}
            print(f"\n{CYAN}{BOLD}[+] Launching Comprehensive Scientific Quantum Verification Battery (7 Multi-Protocol Suite)...{RESET}")
            execute_battery(selected_port, selected_modules, run_params, profile_name="SCIENTIFIC_VERIFICATION_BATTERY")
            break

CHECKPOINT_FILE_NAME = "checkpoint.json"
GLOBAL_CHECKPOINT_TRACKER = os.path.join(SCRIPT_DIR, "results", ".latest_checkpoint.json")

def save_battery_checkpoint(results_dir, profile_name, port, selected_keys, completed_keys, run_params, all_raw_records, all_summary_records, status="INCOMPLETE"):
    """Persists intermediate battery execution state for seamless failure recovery and resumption."""
    checkpoint_data = {
        "results_dir": results_dir,
        "profile_name": profile_name,
        "port": port,
        "selected_keys": selected_keys,
        "completed_keys": completed_keys,
        "run_params": run_params,
        "all_raw_records": all_raw_records,
        "all_summary_records": all_summary_records,
        "status": status,
        "timestamp_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "last_stage_title": MODULE_TITLES.get(completed_keys[-1], "None") if completed_keys else "Initialization",
        "next_stage_title": MODULE_TITLES.get(selected_keys[len(completed_keys)], "Complete") if len(completed_keys) < len(selected_keys) else "Complete"
    }
    try:
        os.makedirs(results_dir, exist_ok=True)
        ck_path = os.path.join(results_dir, CHECKPOINT_FILE_NAME)
        with open(ck_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2)
        
        os.makedirs(os.path.dirname(GLOBAL_CHECKPOINT_TRACKER), exist_ok=True)
        with open(GLOBAL_CHECKPOINT_TRACKER, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2)
    except Exception:
        pass

def load_battery_checkpoint():
    """Loads active incomplete battery checkpoint if one exists."""
    if os.path.exists(GLOBAL_CHECKPOINT_TRACKER):
        try:
            with open(GLOBAL_CHECKPOINT_TRACKER, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("status") == "INCOMPLETE" and os.path.exists(data.get("results_dir", "")):
                return data
        except Exception:
            pass
    return None

def clear_battery_checkpoint():
    """Cleans up checkpoint pointer after a successful run."""
    if os.path.exists(GLOBAL_CHECKPOINT_TRACKER):
        try:
            os.remove(GLOBAL_CHECKPOINT_TRACKER)
        except Exception:
            pass

def execute_battery(port, selected_keys, run_params, profile_name="STANDARD", output_dir=None, resume_checkpoint=None):
    timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    if resume_checkpoint:
        results_dir = resume_checkpoint["results_dir"]
        all_raw_records = list(resume_checkpoint.get("all_raw_records", []))
        all_summary_records = list(resume_checkpoint.get("all_summary_records", []))
        completed_keys = list(resume_checkpoint.get("completed_keys", []))
        log_file_path = os.path.join(results_dir, "battery_execution.log")
        log_fp = open(log_file_path, "a", encoding="utf-8")
    else:
        if output_dir:
            results_dir = os.path.abspath(output_dir)
        else:
            results_dir = os.path.join(SCRIPT_DIR, "results", timestamp_str)
        os.makedirs(results_dir, exist_ok=True)
        all_raw_records = []
        all_summary_records = []
        completed_keys = []
        log_file_path = os.path.join(results_dir, "battery_execution.log")
        log_fp = open(log_file_path, "w", encoding="utf-8")

    def log(msg=""):
        print(msg)
        # Strip ANSI colors for disk log
        clean_msg = msg
        for code in [CYAN, GREEN, YELLOW, RED, BOLD, DIM, RESET]:
            clean_msg = clean_msg.replace(code, "")
        log_fp.write(clean_msg + "\n")
        log_fp.flush()

    log("\n" + "=" * 90)
    log("   OFFICIAL OJANVU QUANTUM LABS TEST SUITE: HARDWARE BATTERY EXECUTION")
    log(f"   Execution Profile: {profile_name}")
    log(f"   Hardware Interface: {port} @ 115,200 baud")
    log(f"   Artifacts Destination: {results_dir}")
    if resume_checkpoint:
        log(f"   Mode: RESUMED from Stage {len(completed_keys) + 1} ({len(completed_keys)} previously completed)")
    log("=" * 90)

    # Initialize Hardware
    log("\n[+] Opening Physical Hardware Serial Communication...")
    conn = Planck2Connection(port=port, baudrate=115200, timeout=6.0, verbose=False)
    
    try:
        conn.connect()
        log(f"    [+] Successfully connected to Quantum Hardware Core on: {conn.port}")
    except Exception as e:
        log(f"    [!] FATAL: Failed to connect to quantum hardware: {e}")
        log_fp.close()
        return

    # MANDATORY: Assert QEC ON at battery startup.
    # Ensures ALL battery test modules and QASM circuits execute on
    # Fault-Tolerant Logical Qubits (LQ) via 3:1 Sovereign Chromatic QEC.
    conn.set_qec(True)
    log("    [✓] QEC Mode: ENABLED — All circuits execute on Fault-Tolerant Logical Qubits (3:1 Chromatic QEC)")

    remaining_keys = [k for k in selected_keys if k not in completed_keys]
    log(f"    [+] Total Modules in Suite ({len(selected_keys)}): {', '.join(selected_keys)}")
    if resume_checkpoint:
        log(f"    [✓] Skipped Completed ({len(completed_keys)}): {', '.join(completed_keys)}")
        log(f"    [>] Remaining to Run ({len(remaining_keys)}): {', '.join(remaining_keys)}")

    battery_start_time = time.time()
    runs = run_params.get("runs", 5)
    shots = run_params.get("shots", 500)

    try:
        log("\n[+] Locking Homodyne Transimpedance & Zeroing Optoelectronic Core...")
        conn.calibrate()
        time.sleep(0.5)

        for key in remaining_keys:
            current_stage_num = len(completed_keys) + 1
            mod = MODULE_REGISTRY[key]
            log(f"\n{CYAN}{BOLD}>>> Running Stage {current_stage_num}/{len(selected_keys)}: [{MODULE_TITLES.get(key, key)}]{RESET}")
            
            t_stage0 = time.time()
            adaptive_flag = run_params.get("adaptive", False)
            if key == "calibration":
                summaries, raws = mod.run(conn, runs=runs, shots=shots, log=log)
            elif key == "qubit_scaling":
                summaries, raws = mod.run(
                    conn, runs=runs, shots=300,
                    min_qubits=run_params.get("min_qubits", 2),
                    max_qubits=run_params.get("max_qubits", 128),
                    adaptive=adaptive_flag,
                    qubit_list=run_params.get("qubit_list"),
                    log=log
                )
            elif key == "gate_depth":
                summaries, raws = mod.run(
                    conn, runs=runs, shots=shots,
                    depth_list=run_params.get("depth_list"),
                    adaptive=adaptive_flag,
                    log=log
                )
            elif key == "quantum_volume":
                summaries, raws = mod.run(
                    conn, runs=runs, shots=shots,
                    min_width=run_params.get("min_width", 2),
                    max_width=run_params.get("max_width", 12),
                    adaptive=adaptive_flag,
                    log=log
                )
            elif key == "cv_clusters":
                summaries, raws = mod.run(
                    conn, runs=runs, shots=shots,
                    tiers=run_params.get("tiers"),
                    log=log
                )
            elif key == "cluster_nullifiers":
                summaries, raws = mod.run(
                    conn, runs=runs, shots=shots,
                    tiers=run_params.get("tiers"),
                    log=log
                )
            elif key == "shot_scaling":
                summaries, raws = mod.run(
                    conn, runs=runs,
                    shot_list=run_params.get("shot_list"),
                    log=log
                )
            elif key in ["qumode_capacity_certification", "qumode_certification"]:
                summaries, raws = mod.run(
                    conn, runs=runs, shots=shots,
                    target_qumodes=run_params.get("target_qumodes", 7714),
                    log=log
                )
            else:
                summaries, raws = mod.run(conn, runs=runs, shots=shots, log=log)

            stage_elapsed = time.time() - t_stage0
            log(f"    {GREEN}[✓ Stage Completed in {stage_elapsed:.2f}s | Logged {len(raws)} physical runs]{RESET}")
            
            all_raw_records.extend(raws)
            all_summary_records.extend(summaries)
            completed_keys.append(key)

            # Persist intermediate checkpoint after every successful stage
            save_battery_checkpoint(
                results_dir=results_dir,
                profile_name=profile_name,
                port=conn.port,
                selected_keys=selected_keys,
                completed_keys=completed_keys,
                run_params=run_params,
                all_raw_records=all_raw_records,
                all_summary_records=all_summary_records,
                status="INCOMPLETE"
            )

            conn.recover_hardware()
            conn.reset_buffers(dwell_time=0.1)
            time.sleep(0.25)

    except KeyboardInterrupt:
        log("\n[!] Execution interrupted by user! Saving intermediate checkpoint and compiling acquired measurements...")
        save_battery_checkpoint(
            results_dir=results_dir,
            profile_name=profile_name,
            port=conn.port,
            selected_keys=selected_keys,
            completed_keys=completed_keys,
            run_params=run_params,
            all_raw_records=all_raw_records,
            all_summary_records=all_summary_records,
            status="INCOMPLETE"
        )
        log(f"{YELLOW}[+] Recovery checkpoint saved. You can resume this exact run anytime by re-running python3 run_battery.py{RESET}")
    except Exception as e:
        log(f"\n[!] Unexpected execution error: {e}")
        save_battery_checkpoint(
            results_dir=results_dir,
            profile_name=profile_name,
            port=conn.port,
            selected_keys=selected_keys,
            completed_keys=completed_keys,
            run_params=run_params,
            all_raw_records=all_raw_records,
            all_summary_records=all_summary_records,
            status="INCOMPLETE"
        )
        import traceback
        traceback.print_exc()
    finally:
        total_battery_duration = time.time() - battery_start_time
        total_shots = sum(r.get("shots", 0) for r in all_raw_records)

        # If all stages completed, mark checkpoint as COMPLETED and clear global pointer
        if len(completed_keys) == len(selected_keys):
            save_battery_checkpoint(
                results_dir=results_dir,
                profile_name=profile_name,
                port=conn.port,
                selected_keys=selected_keys,
                completed_keys=completed_keys,
                run_params=run_params,
                all_raw_records=all_raw_records,
                all_summary_records=all_summary_records,
                status="COMPLETED"
            )
            clear_battery_checkpoint()

        log("\n" + "=" * 90)
        log("  COMPILING MULTI-FORMAT REPORT ARTIFACTS")
        log("=" * 90)

        hw_meta = {
            "port": conn.port,
            "baudrate": conn.baudrate,
            "profile": profile_name,
            "modules_run": selected_keys
        }

        reporter = ReportGenerator(results_dir, hardware_info=hw_meta)
        raw_csv = reporter.write_raw_csv(all_raw_records)
        sum_csv = reporter.write_summary_csv(all_summary_records)
        json_rep = reporter.write_json(all_summary_records, all_raw_records)
        md_rep = reporter.write_markdown_report(all_summary_records, total_shots, total_battery_duration)

        # Update latest mirror
        latest_dir = os.path.join(SCRIPT_DIR, "results", "latest")
        try:
            if os.path.exists(latest_dir):
                if os.path.islink(latest_dir):
                    os.unlink(latest_dir)
                else:
                    shutil.rmtree(latest_dir)
            shutil.copytree(results_dir, latest_dir)
        except Exception:
            pass

        # Terminal Executive Summary Table
        log("\n" + "=" * 110)
        log(f"{BOLD}EXECUTIVE BENCHMARK SUMMARY & EMPIRICAL DEVIATION LEDGER{RESET}")
        log("=" * 110)
        header = f"{'Domain':<24s} {'Metric Label':<36s} {'Mean':<9s} {'StdDev':<8s} {'CV% (Dev)':<10s} {'Status':<10s}"
        log(header)
        log("-" * 110)
        for s in all_summary_records:
            dom = s.get("domain", "")[:23]
            lbl = s.get("metric_label", "")[:35]
            mean = f"{s.get('mean', 0.0):.2f}"
            sd = f"{s.get('std_dev', 0.0):.2f}"
            cv = f"{s.get('cv_pct', 0.0):.2f}%"
            stat = s.get("status", "PASSED")
            color = GREEN if stat == "CERTIFIED" else (CYAN if stat == "PASSED" else YELLOW)
            log(f"{dom:<24s} {lbl:<36s} {mean:<9s} {sd:<8s} {cv:<10s} {color}{stat:<10s}{RESET}")

        log("-" * 110)
        log(f"{GREEN}[+] Raw Measurements CSV:      {raw_csv}{RESET}")
        log(f"{GREEN}[+] Statistical Summary CSV:   {sum_csv}{RESET}")
        log(f"{GREEN}[+] Complete JSON Data Store:  {json_rep}{RESET}")
        log(f"{GREEN}[+] Executive Markdown Report: {md_rep}{RESET}")
        log(f"{GREEN}[+] Latest Results Mirror:     {latest_dir}{RESET}")
        log(f"\n{BOLD}[+] BATTERY TESTING COMPLETE IN {total_battery_duration:.2f} SECONDS.{RESET}")
        log(f"[+] Total Physical Shots Integrated: {total_shots:,} shots.")
        log("=" * 110 + "\n")

        conn.disconnect()
        log_fp.close()

def parse_cli_arguments():
    parser = argparse.ArgumentParser(
        description="Official Ojanvu Quantum Labs Test Suite: Planck 2 Hardware Battery",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--all", action="store_true", help="Non-interactive execution of all modules")
    parser.add_argument("--cv-only", action="store_true", help="Run only native Continuous-Variable (CVQC) optical hardware suite (12 modules)")
    parser.add_argument("--dv-only", action="store_true", help="Run only Discrete-Variable (OpenQASM) hybrid suite (9 modules)")
    parser.add_argument("--ftqc", action="store_true", help="Run 2,571 Fault-Tolerant Logical Qubits Benchmark (3:1 Chromatic QEC)")
    parser.add_argument("--algorithms-usability", action="store_true", help="Run 2,571 Logical Qubit Usability & Quantum Algorithms (QAOA, QML, Grover, QFT)")
    parser.add_argument("--scientific", action="store_true", help="Run Comprehensive Scientific Quantum Verification Battery (7 Multi-Protocol Suite)")
    parser.add_argument("--capacity-cert", "--certify-capacity", dest="capacity_cert", action="store_true", help="Run physical chromatic qubit & qumode capacity stress suite (7,714+ physical modes)")
    parser.add_argument("--certify-5000", dest="certify_5000", action="store_true", help="Alias for --capacity-cert")
    parser.add_argument("--target-qubits", "--stress-qubits", dest="target_qubits", type=int, default=None, help="Target physical chromatic qubits/qumodes for capacity stress test (default: full 7,714 capacity)")
    parser.add_argument("--resume", action="store_true", help="Resume from last interrupted checkpoint")
    parser.add_argument("--quick", action="store_true", help="Non-interactive quick validation profile")
    parser.add_argument("--deep", action="store_true", help="Non-interactive deep characterization profile")
    parser.add_argument("--test", type=str, default=None, help="Comma-separated module names to execute non-interactively")
    parser.add_argument("--port", type=str, default=None, help="Hardware serial port path")
    parser.add_argument("--runs", type=int, default=None, help="Override run count")
    parser.add_argument("--shots", type=int, default=None, help="Override shot count")
    parser.add_argument("--max-qubits", type=int, default=None, help="Override maximum qubit register scaling ceiling")
    parser.add_argument("--qubit-list", type=str, default=None, help="Comma-separated explicit qubit widths to benchmark")
    parser.add_argument("--adaptive", dest="adaptive", action="store_true", default=True, help="Enable continuous stress hunting and adaptive scaling (default: True)")
    parser.add_argument("--no-adaptive", dest="adaptive", action="store_false", help="Disable adaptive scaling")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom artifact directory")
    return parser.parse_args()

def main():
    args = parse_cli_arguments()

    if args.resume:
        active_ck = load_battery_checkpoint()
        if not active_ck:
            print(f"{RED}[!] No active incomplete checkpoint found to resume.{RESET}")
            sys.exit(1)
        cfg = ConfigManager()
        port = args.port or active_ck.get("port") or Planck2Connection.auto_detect_port(cfg.get("PLANCK2_PORT"))
        print(f"\n{GREEN}[+] Resuming interrupted run from Stage {len(active_ck.get('completed_keys', [])) + 1}...{RESET}")
        execute_battery(
            port=port,
            selected_keys=active_ck["selected_keys"],
            run_params=active_ck["run_params"],
            profile_name=active_ck["profile_name"],
            output_dir=active_ck["results_dir"],
            resume_checkpoint=active_ck
        )
        return

    # If non-interactive flags were supplied, bypass interactive menu
    if args.all or args.cv_only or args.dv_only or args.quick or args.deep or args.test or args.certify_5000 or getattr(args, "capacity_cert", False) or args.ftqc or args.algorithms_usability or args.scientific:
        cfg = ConfigManager()
        port = args.port or Planck2Connection.auto_detect_port(cfg.get("PLANCK2_PORT"))

        if args.ftqc:
            profile_name = "FAULT_TOLERANT_2571_QUBITS_SUITE"
            selected_keys = ["fault_tolerant_2571_qubits"]
            run_params = {"runs": args.runs or 1, "shots": args.shots or 2571, "adaptive": False}
        elif args.algorithms_usability:
            profile_name = "LOGICAL_ALGORITHMS_USABILITY_SUITE"
            selected_keys = ["logical_algorithms_usability"]
            run_params = {"runs": args.runs or 1, "shots": args.shots or 2571, "adaptive": False}
        elif args.scientific:
            profile_name = "SCIENTIFIC_VERIFICATION_BATTERY"
            selected_keys = ["scientific_verification"]
            run_params = {"runs": args.runs or 1, "shots": args.shots or 5000, "adaptive": False}
        elif args.certify_5000 or getattr(args, "capacity_cert", False):
            profile_name = "PHYSICAL_CHROMATIC_CAPACITY_STRESS_SUITE"
            selected_keys = ["qumode_capacity_certification"]
            run_params = {
                "runs": args.runs or 3,
                "shots": args.shots or 500,
                "target_qumodes": args.target_qubits or 7714,
                "adaptive": False
            }
        elif args.cv_only:
            profile_name = "CVQC_NATIVE_SUITE"
            selected_keys = [k for k in CV_MODULE_KEYS if k in MODULE_REGISTRY]
            run_params = {
                "runs": args.runs or cfg.get("DEFAULT_RUNS", 5),
                "shots": args.shots or cfg.get("DEFAULT_SHOTS", 500),
                "adaptive": args.adaptive,
                "tiers": cfg.get("TEST_10_TIERS"),
                "shot_list": cfg.get("TEST_11_SHOT_LIST"),
            }
        elif args.dv_only:
            profile_name = "DV_QASM_HYBRID_SUITE"
            selected_keys = [k for k in DV_MODULE_KEYS if k in MODULE_REGISTRY]
            run_params = {
                "runs": args.runs or cfg.get("DEFAULT_RUNS", 5),
                "shots": args.shots or cfg.get("DEFAULT_SHOTS", 500),
                "adaptive": args.adaptive,
                "min_qubits": cfg.get("TEST_05_MIN_QUBITS", 2),
                "max_qubits": cfg.get("TEST_05_MAX_QUBITS", 15),
                "depth_list": cfg.get("TEST_06_DEPTH_LIST"),
                "min_width": cfg.get("TEST_07_MIN_WIDTH", 2),
                "max_width": cfg.get("TEST_07_MAX_WIDTH", 12),
            }

        elif args.quick:
            profile_name = "QUICK_VALIDATION"
            selected_keys = list(MODULE_REGISTRY.keys())
            run_params = {
                "runs": args.runs or 2, "shots": args.shots or 200, "min_qubits": 2, "max_qubits": 8,
                "adaptive": False,
                "depth_list": [2, 4, 8, 15, 30, 50, 100], "min_width": 2, "max_width": 6,
                "tiers": [100, 250, 500, 1000], "shot_list": [100, 500, 1000]
            }
        elif args.deep:
            profile_name = "DEEP_CHARACTERIZATION"
            selected_keys = list(MODULE_REGISTRY.keys())
            run_params = {
                "runs": args.runs or 10, "shots": args.shots or 500, "min_qubits": 2, "max_qubits": 20,
                "adaptive": args.adaptive,
                "depth_list": [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200],
                "min_width": 2, "max_width": 16, "tiers": [100, 250, 500, 1000, 1500, 2000, 2560],
                "shot_list": [100, 250, 500, 1000, 2000, 5000]
            }
        elif args.test:
            profile_name = "CUSTOM_MODULES"
            req = [k.strip().lower() for k in args.test.split(",")]
            selected_keys = [k for k in req if k in MODULE_REGISTRY]
            qubit_list_parsed = [int(x.strip()) for x in args.qubit_list.split(",") if x.strip().isdigit()] if args.qubit_list else None
            run_params = {
                "runs": args.runs or cfg.get("DEFAULT_RUNS", 5),
                "shots": args.shots or cfg.get("DEFAULT_SHOTS", 500),
                "adaptive": args.adaptive,
                "min_qubits": cfg.get("TEST_05_MIN_QUBITS", 2),
                "max_qubits": args.max_qubits or cfg.get("TEST_05_MAX_QUBITS", 128),
                "qubit_list": qubit_list_parsed,
                "depth_list": cfg.get("TEST_06_DEPTH_LIST"),
                "min_width": cfg.get("TEST_07_MIN_WIDTH", 2),
                "max_width": cfg.get("TEST_07_MAX_WIDTH", 12),
                "tiers": cfg.get("TEST_10_TIERS"),
                "shot_list": cfg.get("TEST_11_SHOT_LIST"),
            }
        else: # --all
            profile_name = "STANDARD_FULL_BATTERY"
            selected_keys = list(MODULE_REGISTRY.keys())
            qubit_list_parsed = [int(x.strip()) for x in args.qubit_list.split(",") if x.strip().isdigit()] if args.qubit_list else None
            run_params = {
                "runs": args.runs or cfg.get("DEFAULT_RUNS", 5),
                "shots": args.shots or cfg.get("DEFAULT_SHOTS", 500),
                "adaptive": args.adaptive,
                "min_qubits": cfg.get("TEST_05_MIN_QUBITS", 2),
                "max_qubits": args.max_qubits or cfg.get("TEST_05_MAX_QUBITS", 128),
                "qubit_list": qubit_list_parsed,
                "depth_list": cfg.get("TEST_06_DEPTH_LIST"),
                "min_width": cfg.get("TEST_07_MIN_WIDTH", 2),
                "max_width": cfg.get("TEST_07_MAX_WIDTH", 12),
                "tiers": cfg.get("TEST_10_TIERS"),
                "shot_list": cfg.get("TEST_11_SHOT_LIST"),
            }

        execute_battery(port, selected_keys, run_params, profile_name=profile_name, output_dir=args.output_dir)
    else:
        # Launch Linux interactive CLI application
        interactive_cli()

if __name__ == "__main__":
    main()
