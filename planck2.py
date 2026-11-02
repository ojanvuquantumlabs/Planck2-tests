"""
===============================================================================
Ojanvu Planck 2: Universal Research Python Interface
===============================================================================
Provides a clean, intuitive Python interface to execute OpenQASM (Qubits)
and CV-QASM (Qumodes) on the physical Planck 2 Quantum Computer.

Defaults to Fault-Tolerant Logical Qubits (LQ) with 3:1 Sovereign Chromatic QEC.
===============================================================================
"""

import os
import sys

# Ensure local imports work regardless of execution directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core.connection import Planck2Connection


class Planck2:
    """Universal hardware client for Planck 2 Continuous-Variable Quantum Computer."""

    def __init__(self, port: str = None, baudrate: int = 115200, timeout: float = 15.0):
        # Auto-detect port across macOS, Linux, and Windows if not explicitly passed
        resolved_port = port or os.environ.get("PLANCK2_PORT") or Planck2Connection.auto_detect_port()
        if not resolved_port:
            raise ConnectionError(
                "No Planck 2 hardware port detected! "
                "Please verify the USB connection, or pass port explicitly, "
                "e.g. qpu = Planck2(port='/dev/ttyACM0') on Linux or qpu = Planck2(port='COM3') on Windows."
            )
        self.conn = Planck2Connection(port=resolved_port, baudrate=baudrate, timeout=timeout)
        self.conn.connect()
        self.port = self.conn.port
        self.baudrate = baudrate
        # MANDATORY: Assert QEC ON at initialization.
        # Every circuit executed through this client runs on Fault-Tolerant
        # Logical Qubits (LQ) via 3:1 Sovereign Chromatic QEC by default.
        self.conn.set_qec(True)

    def set_qec(self, enabled: bool = True):
        """
        Configure Hardware Quantum Error Correction mode.
        enabled=True: Executes on Fault-Tolerant Logical Qubits (LQ) via 3:1 Chromatic QEC.
        enabled=False: Executes on raw unprotected Physical Qubits.
        """
        return self.conn.set_qec(enabled)

    def run_qasm(self, circuit: str, shots: int = 100, qec: bool = True, timeout: float = 60.0) -> dict:
        """
        Runs an OpenQASM circuit on Planck 2.
        qec=True: Runs on Fault-Tolerant Logical Qubits (LQ) via 3:1 Chromatic QEC (Default).
        qec=False: Runs on raw unprotected physical qubits.
        Returns: measurement counts dict, e.g. {'00': 100}
        """
        self.conn.set_qec(qec)
        counts, total_shots, raw_lines, elapsed = self.conn.execute_qasm(circuit, shots=shots, timeout=timeout)
        return counts

    def run_cv(self, circuit: str) -> float:
        """
        Runs a CV-QASM circuit (Qumodes) on Planck 2.
        Returns: measured continuous field quadrature q (float)
        """
        op_count, quadrature_q, raw_lines, elapsed = self.conn.execute_cv(circuit)
        return quadrature_q

    def solve_hamiltonian(self, h00: float = -10.5, h11: float = -12.2, v: float = -3.4,
                          iters: int = 15, timeout: float = 12.0) -> dict:
        """
        Executes continuous-variable molecular ground-state Hamiltonian VQE (Qumodes)
        directly on Planck 2's optical field via closed-loop parameter-shift descent.
        Returns: dict with converged energy_ha, energy_kcal, and convergence status.
        """
        data, raw = self.conn.solve_hamiltonian(h00=h00, h11=h11, v=v, iters=iters, timeout=timeout)
        return data

    def execute_ti(self, h00_a: float, h11_a: float, v_a: float,
                   h00_b: float, h11_b: float, v_b: float,
                   n_lambda: int = 11, n_samples: int = 50, timeout: float = 15.0) -> dict:
        """
        Executes continuous-variable thermodynamic integration (ΔΔG) across
        alchemical coupling windows on Planck 2's optical qumode manifold.
        Returns: dict with relative binding free energy and window integrals.
        """
        data, raw = self.conn.execute_ti(h00_a, h11_a, v_a, h00_b, h11_b, v_b,
                                         n_lambda=n_lambda, n_samples=n_samples, timeout=timeout)
        return data

    def solve_qubo(self, n_vars: int = 100, weight: float = 1.0, timeout: float = 10.0) -> dict:
        """
        Executes universal combinatorial optimization across up to 2,571 Logical Qubits
        mapped to the 7,714 qumode optical cluster.
        """
        data, raw = self.conn.solve_qubo(n_vars=n_vars, weight=weight, timeout=timeout)
        return data

    def close(self):
        """Closes hardware serial connection."""
        self.conn.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
