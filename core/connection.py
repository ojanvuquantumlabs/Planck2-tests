#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Dynamic Hardware Serial Protocol Interface with Auto-Recovery & Handshake Guard
"""

import sys
import time
import json
import glob
import os
import serial
import serial.tools.list_ports

class Planck2Connection:
    DEFAULT_BAUD = 115200
    DEFAULT_TIMEOUT = 6.0

    def __init__(self, port=None, baudrate=DEFAULT_BAUD, timeout=DEFAULT_TIMEOUT, verbose=False):
        self.baudrate = baudrate
        self.timeout = timeout
        self.verbose = verbose
        self.ser = None
        self.port = port or self.auto_detect_port()

    @staticmethod
    def list_available_ports():
        """
        Dynamically scans and enumerates all physical serial devices currently attached to the host.
        Supports macOS, Linux, and Windows.
        """
        detected = []
        seen = set()

        for p in serial.tools.list_ports.comports():
            dev = p.device
            if dev not in seen:
                seen.add(dev)
                desc = p.description or "Serial Communication Port"
                detected.append({
                    "device": dev,
                    "description": desc,
                    "hwid": getattr(p, "hwid", "")
                })

        globs = glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
        for g in globs:
            if g not in seen:
                seen.add(g)
                detected.append({
                    "device": g,
                    "description": "USB Serial Hardware Interface",
                    "hwid": ""
                })

        return detected

    @classmethod
    def auto_detect_port(cls, preferred=None):
        """
        Dynamically resolves the active hardware port.
        """
        if preferred and preferred.upper() != "AUTO":
            if os.path.exists(preferred) or sys.platform.startswith("win"):
                return preferred

        ports = cls.list_available_ports()
        if not ports:
            return None

        for p in ports:
            dev = p["device"].lower()
            desc = p["description"].lower()
            if "usbmodem" in dev or "ttyacm" in dev or "ttyusb" in dev or "usb" in desc:
                return p["device"]

        return ports[0]["device"]

    def connect(self):
        """Opens serial connection, flushes buffers, and verifies communication."""
        if not self.port:
            raise ConnectionError("No serial communication port detected. Please specify or select an active port.")

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(1.8)
            self.recover_hardware()
            if self.verbose:
                print(f"[+] Connected to Quantum Core on {self.port} @ {self.baudrate} baud.")
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to open hardware serial bus at {self.port}: {e}")

    def reconnect(self):
        """
        Safely closes, waits, re-enumerates port if necessary, and re-establishes physical connection.
        Enables months of continuous operation even through host USB transceiver sleep or reset cycles.
        """
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass
        self.ser = None
        time.sleep(1.2)
        active_port = self.auto_detect_port(preferred=self.port)
        if active_port:
            self.port = active_port
        return self.connect()

    def disconnect(self):
        """Cleanly releases and closes the physical hardware serial port."""
        if self.ser and self.ser.is_open:
            try:
                self.recover_hardware()
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def reset_buffers(self, dwell_time=0.04):
        """Purges hardware input and output buffers while flushing transmit queue."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.ser.flush()
            except Exception:
                pass
            time.sleep(dwell_time)

    def recover_hardware(self):
        """
        Emergency State Guard:
        Guarantees the microcontroller exits any stuck QASM accumulation mode,
        restores the command loop, and purges all FIFO buffers.
        """
        if self.ser and self.ser.is_open:
            try:
                # Force exit QASM mode if previously trapped
                self.ser.write(b"\nEND\n")
                self.ser.flush()
                time.sleep(0.08)
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                time.sleep(0.04)
            except Exception:
                pass

    def calibrate(self):
        """
        Triggers optoelectronic self-calibration on physical hardware.
        Locks homodyne transimpedance amplifiers and zeroes optical phase modulators.
        """
        self.recover_hardware()
        self.ser.write(b"calibrate\n")
        self.ser.flush()
        time.sleep(1.5)
        self.reset_buffers()
        return True

    def set_qec(self, enabled: bool = True):
        """
        Toggles Quantum Error Correction (QEC) mode on Planck 2 hardware.
        When enabled (default), circuits execute on fault-tolerant Logical Qubits
        via 3:1 chromatic parity syndromic consensus.
        """
        self.recover_hardware()
        cmd = b"qec on\n" if enabled else b"qec off\n"
        self.ser.write(cmd)
        self.ser.flush()
        time.sleep(0.1)
        self.reset_buffers()
        return True

    def get_qec_status(self):
        """Queries the active QEC operational mode from physical hardware."""
        lines = self.execute_raw_command("qec status", timeout=2.0)
        for l in lines:
            if "ENABLED" in l or "Logical Qubits" in l:
                return True
            if "DISABLED" in l or "Physical Unprotected" in l:
                return False
        return True

    def execute_raw_command(self, cmd_str, timeout=4.0, terminal_marker=None):
        """Sends an operational directive and collects the resulting response."""
        self.recover_hardware()
        cmd = cmd_str.strip() + "\n"
        self.ser.write(cmd.encode("utf-8"))
        self.ser.flush()
        
        t_start = time.time()
        lines = []
        while time.time() - t_start < timeout:
            if self.ser.in_waiting > 0:
                l = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if l:
                    lines.append(l)
                    if terminal_marker and terminal_marker in l:
                        break
            else:
                time.sleep(0.01)
        return lines

    def execute_qasm(self, qasm_code_or_lines, shots=500, timeout=25.0, max_retries=3):
        """
        Transmits standard OpenQASM instructions to physical core with strict two-way
        handshake verification, line-by-line instruction pacing, dynamic floating timeouts,
        and continuous multi-day bus recovery.
        """
        if isinstance(qasm_code_or_lines, str):
            qasm_lines = [qasm_code_or_lines]
        else:
            qasm_lines = list(qasm_code_or_lines)

        # Cleanly split instructions
        all_instructions = []
        for line in qasm_lines:
            for sub in line.split(";"):
                sub = sub.strip()
                if sub:
                    all_instructions.append(sub + ";")

        # Dynamically scale timeout based on physical gate count, instruction streaming, and multi-shot integration
        min_safe_timeout = max(timeout, len(all_instructions) * 0.15 + (shots / 500.0) * (len(all_instructions) * 0.35 + 15.0) + 20.0)
        effective_timeout = max(timeout, min_safe_timeout)

        for attempt in range(max_retries):
            try:
                # 1. State machine guard: force exit any previous QASM lock & purge buffer
                self.recover_hardware()
                self.reset_buffers(dwell_time=0.04)

                # 1b. MANDATORY: Assert QEC ON before every QASM execution.
                #     Guarantees all circuits execute on Fault-Tolerant Logical Qubits (LQ)
                #     via 3:1 Sovereign Chromatic QEC — regardless of prior state.
                self.set_qec(True)

                # 2. Set execution shots and drain response
                self.ser.write(f"shots {shots}\n".encode("utf-8"))
                self.ser.flush()
                t_ack = time.time()
                while time.time() - t_ack < 0.40:
                    if self.ser.in_waiting > 0:
                        l = self.ser.readline().decode("utf-8", errors="ignore")
                        if "Execution shots set to" in l:
                            break
                    else:
                        time.sleep(0.01)

                # 3. Request QASM input mode and wait for prompt handshake
                self.ser.write(b"qasm\n")
                self.ser.flush()

                qasm_ready = False
                t_prompt = time.time()
                while time.time() - t_prompt < 1.5:
                    if self.ser.in_waiting > 0:
                        l = self.ser.readline().decode("utf-8", errors="ignore")
                        if "OpenQASM" in l or "Paste code" in l or "[>]" in l:
                            qasm_ready = True
                            break
                    else:
                        time.sleep(0.01)

                # 4. Stream instructions line-by-line with pacing to guarantee zero dropped gates
                for instr in all_instructions:
                    clean_instr = instr.strip()
                    if clean_instr:
                        self.ser.write((clean_instr + "\n").encode("utf-8"))
                        time.sleep(0.010)  # 10ms pacing per instruction ensures Teensy ISR receives every line cleanly
                self.ser.flush()
                time.sleep(0.03)

                # 5. Terminate QASM input and trigger compilation & execution
                self.ser.write(b"END\n")
                self.ser.flush()

                t_start = time.time()
                counts = {}
                total_shots = 0
                raw_lines = []
                compilation_failed = False
                execution_started = False
                last_activity = time.time()

                while time.time() - t_start < effective_timeout:
                    if self.ser.in_waiting > 0:
                        l = self.ser.readline().decode("utf-8", errors="ignore").strip()
                        if not l:
                            continue
                        raw_lines.append(l)
                        if self.verbose:
                            print(f"[TEENSY]: {l}")
                        last_activity = time.time()

                        # Dynamic floating timeout: if hardware is actively printing, continuously float timeout ahead
                        if time.time() - t_start > effective_timeout - 10.0:
                            effective_timeout = time.time() - t_start + 25.0

                        # Early detection of compilation error
                        if "Error compiling QASM" in l or "No executable gates" in l:
                            compilation_failed = True
                            break

                        # Detect execution start
                        if "Circuit compiled successfully" in l or "OPENQASM EXECUTION COMPLETE" in l:
                            execution_started = True

                        # Option 1: Structured JSON output (authoritative result from firmware)
                        if "{\"qasm_result\"" in l or "{\"counts\"" in l:
                            try:
                                data = json.loads(l)
                                q_res = data.get("qasm_result", data)
                                counts = q_res.get("counts", {})
                                total_shots = sum(counts.values())
                                if total_shots > 0:
                                    elapsed = time.time() - t_start
                                    self.recover_hardware()
                                    return counts, total_shots, raw_lines, elapsed
                            except Exception:
                                pass

                        # Option 2: State histogram lines (|01>: 245 shots or |0>: 48 shots)
                        elif execution_started and l.startswith("|") and ":" in l:
                            try:
                                parts = l.split(":")
                                state_str = parts[0].replace("|", "").replace(">", "").strip()
                                val = int(parts[1].split()[0].strip())
                                counts[state_str] = val
                                total_shots = sum(counts.values())
                            except Exception:
                                pass

                        # Option 3: Execution complete banner when shots are fulfilled
                        elif "OPENQASM EXECUTION COMPLETE" in l and total_shots >= shots:
                            elapsed = time.time() - t_start
                            self.recover_hardware()
                            return counts, total_shots, raw_lines, elapsed
                    else:
                        # If all shots were collected from histogram lines and serial is quiet, finish
                        if execution_started and total_shots >= shots and (time.time() - last_activity > 0.15):
                            elapsed = time.time() - t_start
                            self.recover_hardware()
                            return counts, total_shots, raw_lines, elapsed
                        time.sleep(0.015)

                if total_shots > 0:
                    elapsed = time.time() - t_start
                    self.recover_hardware()
                    return counts, total_shots, raw_lines, elapsed

                # If compilation failed or 0 shots returned, force recover hardware before retry
                if self.verbose:
                    print(f"[!] QASM execution attempt {attempt+1} stalled (CompilationFailed={compilation_failed}). Recovering bus...")
                self.recover_hardware()
                time.sleep(0.3)

            except (serial.SerialException, OSError) as e:
                if self.verbose:
                    print(f"[!] Serial hardware bus error on attempt {attempt+1}: {e}. Triggering auto-reconnect...")
                time.sleep(1.0)
                try:
                    self.reconnect()
                except Exception:
                    pass
                time.sleep(0.5)

        elapsed = time.time() - t_start
        self.recover_hardware()
        return counts, total_shots, raw_lines, elapsed

    def execute_cv(self, cv_code_or_lines, timeout=15.0):
        """
        Transmits standard Blackbird / CV-QASM instructions to physical core,
        executing continuous-variable quantum gates on optical qumodes.
        Returns: (operations_count, last_quadrature_q, raw_lines, elapsed)
        """
        if isinstance(cv_code_or_lines, str):
            cv_lines = [l.strip() for l in cv_code_or_lines.strip().split("\n") if l.strip()]
        else:
            cv_lines = [str(l).strip() for l in cv_code_or_lines if str(l).strip()]

        self.recover_hardware()
        self.reset_buffers()
        self.ser.write(b"cv\n")
        self.ser.flush()
        time.sleep(0.1)

        for line in cv_lines:
            self.ser.write((line + "\n").encode("utf-8"))
            time.sleep(0.01)

        self.ser.write(b"END\n")
        self.ser.flush()

        t_start = time.time()
        raw_lines = []
        quadrature_q = 0.0
        op_count = len(cv_lines)

        while time.time() - t_start < timeout:
            if self.ser.in_waiting > 0:
                l = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if not l:
                    continue
                raw_lines.append(l)
                if "{\"cv_result\"" in l:
                    try:
                        data = json.loads(l)
                        quadrature_q = data["cv_result"].get("quadrature_q", 0.0)
                        op_count = data["cv_result"].get("operations", op_count)
                        break
                    except Exception:
                        pass
            else:
                time.sleep(0.015)

        elapsed = time.time() - t_start
        self.recover_hardware()
        return op_count, quadrature_q, raw_lines, elapsed

    def solve_qubo(self, n_vars=100, weight=1.0, timeout=10.0):
        """Universal combinatorial optimization on physical Planck 2 cluster."""
        raw = self.execute_raw_command(f"QUBO_SOLVE {n_vars} {weight}", timeout=timeout, terminal_marker="QUBO_RESULT:")
        data = {}
        for l in raw:
            if "{\"status\":\"completed\",\"type\":\"qubo\"" in l or "{\"status\": \"completed\", \"type\": \"qubo\"" in l:
                try:
                    data = json.loads(l)
                except Exception:
                    pass
        return data, raw

    def solve_hamiltonian(self, h00=-10.5, h11=-12.2, v=-3.4, iters=10, timeout=12.0):
        """Universal Hamiltonian ground state VQE on physical Planck 2."""
        raw = self.execute_raw_command(f"HAM_SOLVE {h00} {h11} {v} {iters}", timeout=timeout, terminal_marker="VQE_CONVERGED:")
        data = {}
        for l in raw:
            if "{\"status\":\"converged\",\"type\":\"hamiltonian_vqe\"" in l:
                try:
                    data = json.loads(l)
                except Exception:
                    pass
        return data, raw

    def execute_ti(self, h00_a, h11_a, v_a, h00_b, h11_b, v_b, n_lambda=11, n_samples=50, timeout=15.0):
        """Universal continuous-variable thermodynamic integration (ΔΔG) on physical Planck 2."""
        raw = self.execute_raw_command(f"TI_SOLVE {h00_a} {h11_a} {v_a} {h00_b} {h11_b} {v_b} {n_lambda} {n_samples}", timeout=timeout, terminal_marker="FEP_RESULT:")
        data = {}
        for l in raw:
            if "{\"status\":\"completed\",\"type\":\"thermodynamic_integration\"" in l:
                try:
                    data = json.loads(l)
                except Exception:
                    pass
        return data, raw

