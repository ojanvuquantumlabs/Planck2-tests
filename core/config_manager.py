#!/usr/bin/env python3
"""
OFFICIAL OJANVU QUANTUM LABS TEST SUITE
Planck 2 Continuous-Variable Quantum Computer Hardware Battery
Configuration Manager & Environment Loader
"""

import os

CONFIG_FILE_NAME = "battery_config.env"

DEFAULT_CONFIG = {
    "PLANCK2_PORT": "AUTO",
    "PLANCK2_BAUDRATE": 115200,
    "PLANCK2_TIMEOUT_SEC": 6.0,
    "DEFAULT_RUNS": 5,
    "DEFAULT_SHOTS": 500,

    # Test 01
    "TEST_01_RUNS": 5,
    "TEST_01_SHOTS": 500,
    "TEST_01_EXTINCTION_TARGET_DB": 30.0,
    "TEST_01_DARK_OFFSET_MAX_MV": 5.0,

    # Test 02
    "TEST_02_RUNS": 5,
    "TEST_02_SHOTS": 500,

    # Test 03
    "TEST_03_RUNS": 5,
    "TEST_03_SHOTS": 500,

    # Test 04
    "TEST_04_RUNS": 5,
    "TEST_04_SHOTS": 500,

    # Test 05
    "TEST_05_RUNS": 5,
    "TEST_05_SHOTS": 300,
    "TEST_05_MIN_QUBITS": 2,
    "TEST_05_MAX_QUBITS": 15,

    # Test 06
    "TEST_06_RUNS": 3,
    "TEST_06_SHOTS": 200,
    "TEST_06_DEPTH_LIST": [2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200],

    # Test 07
    "TEST_07_RUNS": 3,
    "TEST_07_SHOTS": 500,
    "TEST_07_MIN_WIDTH": 2,
    "TEST_07_MAX_WIDTH": 12,

    # Test 08
    "TEST_08_RUNS": 5,
    "TEST_08_SHOTS": 500,

    # Test 09
    "TEST_09_RUNS": 5,
    "TEST_09_SHOTS": 500,

    # Test 10
    "TEST_10_RUNS": 3,
    "TEST_10_SHOTS": 500,
    "TEST_10_TIERS": [100, 250, 500, 1000, 1500, 2000, 2560],

    # Test 11
    "TEST_11_RUNS": 3,
    "TEST_11_SHOT_LIST": [100, 250, 500, 1000, 2000, 5000],

    # Test 12
    "TEST_12_RUNS": 5,
    "TEST_12_SHOTS": 500,
}

class ConfigManager:
    def __init__(self, root_dir=None):
        self.root_dir = root_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.root_dir, CONFIG_FILE_NAME)
        self.config = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        """Loads configuration from .env file with type casting."""
        if not os.path.exists(self.config_path):
            return self.config

        with open(self.config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()

                if k in self.config:
                    orig = DEFAULT_CONFIG[k]
                    if isinstance(orig, int):
                        try:
                            self.config[k] = int(v)
                        except ValueError:
                            pass
                    elif isinstance(orig, float):
                        try:
                            self.config[k] = float(v)
                        except ValueError:
                            pass
                    elif isinstance(orig, list):
                        try:
                            self.config[k] = [int(x.strip()) for x in v.split(",") if x.strip().isdigit()]
                        except Exception:
                            pass
                    else:
                        self.config[k] = v
                else:
                    self.config[k] = v

        return self.config

    def get(self, key, fallback=None):
        return self.config.get(key, fallback if fallback is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.config[key] = value

    def save(self):
        """Saves active configuration back to the .env file."""
        lines = [
            "# =============================================================================",
            "# OFFICIAL OJANVU QUANTUM LABS TEST SUITE CONFIGURATION",
            "# Planck 2 Continuous-Variable Quantum Computer Hardware Battery",
            "# =============================================================================",
            "",
            "# Serial & Hardware Interface Settings",
            f"PLANCK2_PORT={self.config.get('PLANCK2_PORT', 'AUTO')}",
            f"PLANCK2_BAUDRATE={self.config.get('PLANCK2_BAUDRATE', 115200)}",
            f"PLANCK2_TIMEOUT_SEC={self.config.get('PLANCK2_TIMEOUT_SEC', 6.0)}",
            "",
            "# Global Execution Defaults",
            f"DEFAULT_RUNS={self.config.get('DEFAULT_RUNS', 5)}",
            f"DEFAULT_SHOTS={self.config.get('DEFAULT_SHOTS', 500)}",
            "",
            "# Module 01",
            f"TEST_01_RUNS={self.config.get('TEST_01_RUNS', 5)}",
            f"TEST_01_SHOTS={self.config.get('TEST_01_SHOTS', 500)}",
            f"TEST_01_EXTINCTION_TARGET_DB={self.config.get('TEST_01_EXTINCTION_TARGET_DB', 30.0)}",
            f"TEST_01_DARK_OFFSET_MAX_MV={self.config.get('TEST_01_DARK_OFFSET_MAX_MV', 5.0)}",
            "",
            "# Module 02",
            f"TEST_02_RUNS={self.config.get('TEST_02_RUNS', 5)}",
            f"TEST_02_SHOTS={self.config.get('TEST_02_SHOTS', 500)}",
            "",
            "# Module 03",
            f"TEST_03_RUNS={self.config.get('TEST_03_RUNS', 5)}",
            f"TEST_03_SHOTS={self.config.get('TEST_03_SHOTS', 500)}",
            "",
            "# Module 04",
            f"TEST_04_RUNS={self.config.get('TEST_04_RUNS', 5)}",
            f"TEST_04_SHOTS={self.config.get('TEST_04_SHOTS', 500)}",
            "",
            "# Module 05",
            f"TEST_05_RUNS={self.config.get('TEST_05_RUNS', 5)}",
            f"TEST_05_SHOTS={self.config.get('TEST_05_SHOTS', 300)}",
            f"TEST_05_MIN_QUBITS={self.config.get('TEST_05_MIN_QUBITS', 2)}",
            f"TEST_05_MAX_QUBITS={self.config.get('TEST_05_MAX_QUBITS', 15)}",
            "",
            "# Module 06",
            f"TEST_06_RUNS={self.config.get('TEST_06_RUNS', 3)}",
            f"TEST_06_SHOTS={self.config.get('TEST_06_SHOTS', 200)}",
            f"TEST_06_DEPTH_LIST={','.join(str(x) for x in self.config.get('TEST_06_DEPTH_LIST', []))}",
            "",
            "# Module 07",
            f"TEST_07_RUNS={self.config.get('TEST_07_RUNS', 3)}",
            f"TEST_07_SHOTS={self.config.get('TEST_07_SHOTS', 500)}",
            f"TEST_07_MIN_WIDTH={self.config.get('TEST_07_MIN_WIDTH', 2)}",
            f"TEST_07_MAX_WIDTH={self.config.get('TEST_07_MAX_WIDTH', 12)}",
            "",
            "# Module 08",
            f"TEST_08_RUNS={self.config.get('TEST_08_RUNS', 5)}",
            f"TEST_08_SHOTS={self.config.get('TEST_08_SHOTS', 500)}",
            "",
            "# Module 09",
            f"TEST_09_RUNS={self.config.get('TEST_09_RUNS', 5)}",
            f"TEST_09_SHOTS={self.config.get('TEST_09_SHOTS', 500)}",
            "",
            "# Module 10",
            f"TEST_10_RUNS={self.config.get('TEST_10_RUNS', 3)}",
            f"TEST_10_SHOTS={self.config.get('TEST_10_SHOTS', 500)}",
            f"TEST_10_TIERS={','.join(str(x) for x in self.config.get('TEST_10_TIERS', []))}",
            "",
            "# Module 11",
            f"TEST_11_RUNS={self.config.get('TEST_11_RUNS', 3)}",
            f"TEST_11_SHOT_LIST={','.join(str(x) for x in self.config.get('TEST_11_SHOT_LIST', []))}",
            "",
            "# Module 12",
            f"TEST_12_RUNS={self.config.get('TEST_12_RUNS', 5)}",
            f"TEST_12_SHOTS={self.config.get('TEST_12_SHOTS', 500)}",
            ""
        ]
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
