from collections.abc import Callable
from tests.conftest import prototype_numpyAllClose, prototype_numpyArrayEqual, uniformTestFailureMessage, standardizedEqualTo
from typing import Any
import numpy
import pytest
import scipy.signal.windows as SciPy
import torch
from Z0Z_tools import (
	cosineWings,
	cosineWingsTensor,
	equalPower,
	equalPowerTensor,
	halfsine,
	halfsineTensor,
	tukey,
	tukeyTensor,
)

@pytest.mark.parametrize("ratioTaper", [0.0, 0.1, 0.5, 1.0])
def test_cosineWingsArray(ratioTaper: float, lengthWindow: int) -> None:
	"""
	Verify that cosineWings creates the correct array shape and
	test the special case of ratioTaper=0.0 => an array of ones.
	"""
	arrayWindow = cosineWings(lengthWindow, ratioTaper=ratioTaper)
	assert arrayWindow.shape == (lengthWindow,), \
		uniformTestFailureMessage((lengthWindow,), arrayWindow.shape, "cosineWings shape check")
	if ratioTaper == 0.0:
		# Expect an all-ones array
		prototype_numpyArrayEqual(numpy.ones(lengthWindow), cosineWings, lengthWindow, ratioTaper=0.0)

@pytest.mark.parametrize("ratioTaper", [0.0, 0.1, 0.5, 1.0])
def test_equalPowerArray(ratioTaper: float, lengthWindow: int) -> None:
	"""
	Verify that equalPower creates the correct array shape and
	test the special case of ratioTaper=0.0 => an array of ones.
	"""
	arrayWindow = equalPower(lengthWindow, ratioTaper=ratioTaper)
	assert arrayWindow.shape == (lengthWindow,), \
		uniformTestFailureMessage((lengthWindow,), arrayWindow.shape, "equalPower shape check")
	if ratioTaper == 0.0:
		# Expect an all-ones array
		prototype_numpyArrayEqual(numpy.ones(lengthWindow), equalPower, lengthWindow, ratioTaper=0.0)

def test_halfsineArray(lengthWindow: int) -> None:
	"""
	Verify halfsine's shape and that all values are between 0 and 1.
	"""
	arrayWindow = halfsine(lengthWindow)
	assert arrayWindow.shape == (lengthWindow,), \
		uniformTestFailureMessage((lengthWindow,), arrayWindow.shape, "halfsine shape check")
	assert numpy.all(arrayWindow >= 0), \
		"halfsine should yield non-negative coefficients"
	assert numpy.all(arrayWindow <= 1), \
		"halfsine should yield coefficients no greater than 1"

def test_halfsine_edge_value(lengthWindow: int) -> None:
	"""
	Verify the edge value calculation for halfsine using the known formula.
	"""
	arrayWindow = halfsine(lengthWindow)
	expectedEdgeValue = numpy.sin(numpy.pi * 0.5 / lengthWindow)
	assert numpy.allclose(arrayWindow[0], expectedEdgeValue), \
		uniformTestFailureMessage(expectedEdgeValue, arrayWindow[0], "halfsine edge value")

@pytest.mark.parametrize("ratioTaper", [0.0, 0.1, 0.5, 1.0])
def test_tukeyArray(ratioTaper: float, lengthWindow: int) -> None:
	"""
	Verify the shape of Tukey windowing function.
	"""
	arrayWindow = tukey(lengthWindow, ratioTaper=ratioTaper)
	assert arrayWindow.shape == (lengthWindow,), \
		uniformTestFailureMessage((lengthWindow,), arrayWindow.shape, "tukey shape check")

def test_tukey_backward_compatibility() -> None:
	"""
	Verify backward compatibility of tukey's alpha parameter by comparing
	an explicitly set alpha=0.5 with ratioTaper=0.5 from the signature.
	"""
	arrayExpected = tukey(10, ratioTaper=0.5)
	prototype_numpyAllClose(arrayExpected, None, None, tukey, 10, alpha=0.5)

def test_tukey_special_cases(lengthWindow: int) -> None:
	"""
	Verify special cases of tukey windowing function.
	ratioTaper=0.0 => rectangular window
	ratioTaper=1.0 => Hann window
	"""
	prototype_numpyArrayEqual(
		numpy.ones(lengthWindow), tukey, lengthWindow, ratioTaper=0.0
	)
	prototype_numpyAllClose(
		SciPy.hann(lengthWindow), None, None,
		tukey, lengthWindow, ratioTaper=1.0
	)

@pytest.mark.parametrize("functionWindowingInvalid", [cosineWings, equalPower])
def test_invalidTaperRatio(functionWindowingInvalid: Callable[..., numpy.ndarray[tuple[int], numpy.dtype[numpy.float64]]]) -> None:
	"""
	Verify error handling for invalid taper ratios in cosineWings and equalPower.
	"""
	with pytest.raises(ValueError):
		functionWindowingInvalid(256, ratioTaper=-0.1)
	with pytest.raises(ValueError):
		functionWindowingInvalid(256, ratioTaper=1.1)

"""
Section: Tests for PyTorch tensor variants of windowing functions
"""

def prototype_tensorEquivalent(functionNdarrayOriginal: Callable[..., numpy.ndarray], functionTensorTarget: Callable[..., torch.Tensor], device: str, *arguments: Any, **keywordArguments: Any) -> None:
	"""
	Template for tests that verify tensor-based functions produce the same results as their numpy counterparts.
	"""
	ndarray = functionNdarrayOriginal(*arguments, **keywordArguments)
	tensor = functionTensorTarget(*arguments, device=torch.device(device), **keywordArguments)

	assert tensor.device.type == device, \
		uniformTestFailureMessage(device, tensor.device.type, f"{functionTensorTarget.__name__} device check")
	assert tensor.dtype == torch.float32, \
		uniformTestFailureMessage(torch.float32, tensor.dtype, f"{functionTensorTarget.__name__} dtype check")
	assert tensor.shape == torch.Size([ndarray.shape[0]]), \
		uniformTestFailureMessage(ndarray.shape, tensor.shape, f"{functionTensorTarget.__name__} shape check")

	# Convert tensor to numpy for comparison with original array
	tensorAsNumpy = tensor.cpu().numpy()
	assert numpy.allclose(ndarray, tensorAsNumpy), \
		uniformTestFailureMessage("Arrays to match", "Arrays don't match", f"{functionTensorTarget.__name__} vs {functionNdarrayOriginal.__name__}")

def test_windowing_tensors_equivalence(device: str, lengthWindow: int) -> None:
	"""
	Verify all tensor-based windowing functions produce equivalent results to their numpy counterparts.
	"""
	# Test cosineWingsTensor
	prototype_tensorEquivalent(cosineWings, cosineWingsTensor, device, lengthWindow, ratioTaper=0.5)

	# Test equalPowerTensor
	prototype_tensorEquivalent(equalPower, equalPowerTensor, device, lengthWindow, ratioTaper=0.3)

	# Test halfsineTensor
	prototype_tensorEquivalent(halfsine, halfsineTensor, device, lengthWindow)

	# Test tukeyTensor
	prototype_tensorEquivalent(tukey, tukeyTensor, device, lengthWindow, ratioTaper=0.7)

def test_tensor_special_cases(device: str) -> None:
	"""
	Verify special cases in tensor-based windowing functions.
	"""
	# Test zero taper for cosineWingsTensor (should be all ones)
	cosineWingsTensorResult = cosineWingsTensor(256, ratioTaper=0.0, device=torch.device(device))
	assert torch.allclose(cosineWingsTensorResult, torch.ones(256, device=torch.device(device), dtype=torch.float32)), \
		"cosineWingsTensor with ratioTaper=0.0 should produce all ones"

	# Test tukeyTensor with alpha parameter (backward compatibility)
	tukeyNormal = tukeyTensor(256, ratioTaper=0.5, device=torch.device(device))
	tukeyAlpha = tukeyTensor(256, alpha=0.5, device=torch.device(device))
	assert torch.allclose(tukeyNormal, tukeyAlpha), \
		"tukeyTensor should handle alpha parameter the same as ratioTaper"
