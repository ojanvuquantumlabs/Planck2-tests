"""
Ojanvu Planck 2 Testing Battery Modules Package
Universal Continuous-Variable and Fault-Tolerant Quantum Computing Test Suites
"""
from . import test_01_calibration
from . import test_02_bell_entanglement
from . import test_03_single_qubit
from . import test_04_two_qubit
from . import test_05_qubit_scaling
from . import test_06_gate_depth
from . import test_07_quantum_volume
from . import test_08_continuous_variable
from . import test_09_non_gaussian_phase
from . import test_10_cv_clusters
from . import test_11_shot_scaling
from . import test_12_quantum_algorithms
from . import test_13_entanglement_metrics
from . import test_14_simon_inseparability
from . import test_15_epr_steering
from . import test_16_cluster_nullifiers
from . import test_17_wigner_negativity
from . import test_18_qumode_capacity_certification
from . import test_19_fault_tolerant_2571_qubits
from . import test_20_logical_algorithms_usability
from . import test_21_scientific_verification
from . import test_22_gate_speed_and_timing

MODULE_REGISTRY = {
    "calibration": test_01_calibration,
    "bell": test_02_bell_entanglement,
    "single_qubit": test_03_single_qubit,
    "two_qubit": test_04_two_qubit,
    "qubit_scaling": test_05_qubit_scaling,
    "gate_depth": test_06_gate_depth,
    "quantum_volume": test_07_quantum_volume,
    "continuous_variable": test_08_continuous_variable,
    "cubic_phase": test_09_non_gaussian_phase,
    "cv_clusters": test_10_cv_clusters,
    "shot_scaling": test_11_shot_scaling,
    "algorithms": test_12_quantum_algorithms,
    "entanglement_metrics": test_13_entanglement_metrics,
    "simon_inseparability": test_14_simon_inseparability,
    "epr_steering": test_15_epr_steering,
    "cluster_nullifiers": test_16_cluster_nullifiers,
    "wigner_negativity": test_17_wigner_negativity,
    "qumode_capacity_certification": test_18_qumode_capacity_certification,
    "qumode_certification": test_18_qumode_capacity_certification,
    "fault_tolerant_2571_qubits": test_19_fault_tolerant_2571_qubits,
    "logical_algorithms_usability": test_20_logical_algorithms_usability,
    "scientific_verification": test_21_scientific_verification,
    "gate_speeds": test_22_gate_speed_and_timing,
    "gate_speed": test_22_gate_speed_and_timing,
}

__all__ = [
    "MODULE_REGISTRY",
    "test_01_calibration",
    "test_02_bell_entanglement",
    "test_03_single_qubit",
    "test_04_two_qubit",
    "test_05_qubit_scaling",
    "test_06_gate_depth",
    "test_07_quantum_volume",
    "test_08_continuous_variable",
    "test_09_non_gaussian_phase",
    "test_10_cv_clusters",
    "test_11_shot_scaling",
    "test_12_quantum_algorithms",
    "test_13_entanglement_metrics",
    "test_14_simon_inseparability",
    "test_15_epr_steering",
    "test_16_cluster_nullifiers",
    "test_17_wigner_negativity",
    "test_18_qumode_capacity_certification",
    "test_19_fault_tolerant_2571_qubits",
    "test_20_logical_algorithms_usability",
    "test_21_scientific_verification",
    "test_22_gate_speed_and_timing",
]
