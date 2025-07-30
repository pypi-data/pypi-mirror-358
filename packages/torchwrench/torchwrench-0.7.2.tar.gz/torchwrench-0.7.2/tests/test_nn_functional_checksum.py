#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import unittest
from unittest import TestCase

import pythonwrench as pw
import torch

from torchwrench.core.packaging import _NUMPY_AVAILABLE
from torchwrench.extras.numpy import np


class TestChecksum(TestCase):
    def test_checksum_alldiff(self) -> None:
        x = [
            torch.arange(10),
            torch.arange(10).view(2, 5),
            torch.arange(10)[None],
            [torch.arange(10)],
            torch.arange(10, dtype=torch.int16),
            list(range(10)),
            tuple(range(10)),
            set(range(10)),
            range(10),
            [],
            (),
            None,
            0,
            1,
            math.nan,
            torch.as_tensor(math.nan),
            [1, 2],
            [2, 1],
            [1, 2, 0],
            (1, 2),
            "abc",
            "",
            b"abc",
            b"",
        ]
        if _NUMPY_AVAILABLE:
            x += [
                np.arange(10),
                np.arange(10).reshape(2, 5),
                np.int64(100),
            ]

        csums = [pw.checksum_any(xi) for xi in x]
        assert pw.all_ne(csums), f"{csums=}"

    def test_large_arrays(self) -> None:
        x0 = torch.rand(10000, 100)
        x1 = torch.rand(10000, 100)
        assert pw.checksum_any(x0) != pw.checksum_any(x1)

    def test_large_arrays_numpy(self) -> None:
        if not _NUMPY_AVAILABLE:
            return None
        x0 = np.random.rand(10000, 100)
        x1 = np.random.rand(10000, 100)
        assert pw.checksum_any(x0) != pw.checksum_any(x1)

    def test_deterministic(self) -> None:
        x0 = torch.arange(10)
        x1 = torch.arange(10)
        assert id(x0) != id(x1)
        assert pw.checksum_any(x0) == pw.checksum_any(x1)

    def test_nan(self) -> None:
        # NaN pw.checksum_any are equal but nan itself can be different
        if not _NUMPY_AVAILABLE:
            return None
        x0 = math.nan
        x1 = np.nan
        assert id(x0) != id(x1)
        assert pw.checksum_any(x0) == pw.checksum_any(x1)


if __name__ == "__main__":
    unittest.main()
