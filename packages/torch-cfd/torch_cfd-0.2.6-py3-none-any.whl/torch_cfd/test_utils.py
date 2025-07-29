# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modifications copyright (C) 2025 S.Cao
# ported Google's Jax-CFD functional template to torch.Tensor operations

"""Shared test utilities."""

import torch
from absl.testing import parameterized

from torch_cfd import grids

# Enable CUDA deterministic mode if needed
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

class TestCase(parameterized.TestCase):
    """TestCase with assertions for grids.GridVariable."""

    def _check_and_remove_alignment_and_grid(self, *arrays):
        """Check that array-like data values and other attributes match.

        If args type is GridArray, verify their offsets and grids match.
        If args type is GridVariable, verify their offsets, grids, and bc match.

        Args:
          *arrays: one or more Array, GridArray or GridVariable, but they all be the
            same type.

        Returns:
          The data-only arrays, with other attributes removed.
        """
        # GridVariable
        is_gridvariable = [isinstance(array, grids.GridVariable) for array in arrays]
        if any(is_gridvariable):
            self.assertTrue(
                all(is_gridvariable), msg=f"arrays have mixed types: {arrays}"
            )
            try:
                grids.consistent_offset_arrays(*arrays)
            except ValueError as e:
                raise AssertionError(str(e)) from None
            try:
                grids.consistent_grid_arrays(*arrays)
            except ValueError as e:
                raise AssertionError(str(e)) from None
            arrays = tuple(array.data for array in arrays)
        return arrays

    # pylint: disable=unbalanced-tuple-unpacking
    def assertArrayEqual(self, actual, expected, **kwargs):
        actual, expected = self._check_and_remove_alignment_and_grid(actual, expected)
        rtol = torch.finfo(expected.data.dtype).eps
        atol = expected.abs().max() * rtol
        torch.testing.assert_close(actual, expected, atol=atol, rtol=rtol, **kwargs)

    def assertAllClose(self, actual, expected, **kwargs):
        actual, expected = self._check_and_remove_alignment_and_grid(actual, expected)
        torch.testing.assert_close(actual, expected, **kwargs)

    def assertNestedTuplesEqual(self, tuple1, tuple2, atol=1e-6, rtol=1e-6):
        """Assert that two nested tuples containing tensors are equal."""
        def _compare_recursive(t1, t2):
            if type(t1) != type(t2):
                return False
            
            if isinstance(t1, tuple):
                if len(t1) != len(t2):
                    return False
                return all(_compare_recursive(x, y) for x, y in zip(t1, t2))
            
            elif isinstance(t1, torch.Tensor) and isinstance(t2, torch.Tensor):
                try:
                    self.assertAllClose(t1, t2, atol=atol, rtol=rtol)
                    return True
                except AssertionError:
                    return False
            
            elif t1 is None and t2 is None:
                return True
            
            else:
                return t1 == t2
        
        self.assertTrue(_compare_recursive(tuple1, tuple2), 
                    f"Nested tuples are not equal:\n{tuple1}\nvs\n{tuple2}")

