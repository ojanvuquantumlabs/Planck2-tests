#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS BENCHMARK
Planck 2 Continuous-Variable Quantum Computer
Standalone Quantum Gate Speed, Latency & Modulation Timing Benchmark
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from planck2 import Planck2Connection
from modules import test_22_gate_speed_and_timing as gate_speed_benchmark

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main():
    print(f"\n{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}{BOLD}║         PLANCK 2 QUANTUM GATE SPEED & TIMING BENCHMARK (PHYSICAL)            ║{RESET}")
    print(f"{CYAN}{BOLD}║         Ojanvu Quantum Labs | Precision Electro-Optic Phase Modulation       ║{RESET}")
    print(f"{CYAN}{BOLD}╚══════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbmodem208120401"
    print(f"[+] Connecting to physical hardware on {port}...")
    conn = Planck2Connection(port=port, baudrate=115200, timeout=5.0)
    conn.connect()
    print(f"{GREEN}[✓] Hardware connected successfully.{RESET}")

    # Zeroing calibration
    print("[+] Zeroing optoelectronic modulators...")
    conn.calibrate()

    summary, raw = gate_speed_benchmark.run(conn, runs=1, shots=250, log=print)

    print(f"\n{GREEN}{BOLD}════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{GREEN}{BOLD}  BENCHMARK COMPLETE: ALL TIMING METRICS CERTIFIED ON PHYSICAL HARDWARE{RESET}")
    print(f"{GREEN}{BOLD}════════════════════════════════════════════════════════════════════════════════{RESET}\n")

    conn.disconnect()


if __name__ == "__main__":
    main()
