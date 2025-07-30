#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

import torchwrench as tw
from torchwrench import nn


class TestCollate(TestCase):
    def test_advanced_example_1(self) -> None:
        pipe = nn.Sequential(
            nn.AsTensor(),
            nn.Flatten(),
            nn.Unsqueeze(dim=0),
            nn.Topk(k=2, dim=-1, return_indices=False),
            nn.Shuffled(dims=(0, 1)),
            nn.Sort(dim=-1, descending=True, return_indices=False, return_values=True),
            nn.PadAndCropDim(3),
        )

        x = [[1, 2], [3, 4]]
        expected = tw.as_tensor([[4, 3, 0]])
        assert (pipe(x) == expected).all()


if __name__ == "__main__":
    unittest.main()
