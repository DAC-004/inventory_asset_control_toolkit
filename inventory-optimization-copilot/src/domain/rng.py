"""Deterministic random number generation across Python, NumPy, and Faker."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
from faker import Faker

from config.workbook_config import RANDOM_SEED


@dataclass
class SeededRNG:
    """Bundle seeded random generators for reproducible data."""

    seed: int
    python: random.Random
    numpy: np.random.Generator
    faker: Faker

    @classmethod
    def create(cls, seed: int | None = None) -> SeededRNG:
        seed_value = seed if seed is not None else RANDOM_SEED
        py_rng = random.Random(seed_value)
        np_rng = np.random.default_rng(seed_value)
        faker = Faker()
        faker.seed_instance(seed_value)
        return cls(seed=seed_value, python=py_rng, numpy=np_rng, faker=faker)

    def choice(self, seq: list) -> object:
        return self.python.choice(seq)

    def randint(self, low: int, high: int) -> int:
        return self.python.randint(low, high)

    def uniform(self, low: float, high: float) -> float:
        return self.python.uniform(low, high)

    def shuffle(self, seq: list) -> None:
        self.python.shuffle(seq)

    def pattern_index(self, key: str, modulo: int) -> int:
        """Deterministic index from a string key."""
        return sum(ord(c) for c in key) % modulo
