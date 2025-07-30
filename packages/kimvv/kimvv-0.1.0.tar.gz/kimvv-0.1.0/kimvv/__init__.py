from .core import KIMVVTestDriver
from .EquilibriumCrystalStructure.test_driver.test_driver import TestDriver as __EquilibriumCrystalStructure


class EquilibriumCrystalStructure(__EquilibriumCrystalStructure, KIMVVTestDriver):
    pass


__all__ = [
    "EquilibriumCrystalStructure",
]
