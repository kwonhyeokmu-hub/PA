import numpy as np
import pytest

from src.rotation import (
	gram_schmidt,
	is_rotation,
	orthogonality_error,
	rot_x,
	rot_y,
	rot_z,
)


from src.vectors import det

ROT_FUNCS = [rot_x, rot_y, rot_z]

ANGLES = [
    	0.0,
	np.pi / 6,
	np.pi / 4,
	np.pi / 2,
	2.0,
	np.pi,
	-1.234,
]

@pytest.mark.parametrize("rot_func", ROT_FUNCS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(rot_func, theta):
	R = rot_func(theta)

	for i in range(3):
         assert np.isclose(
            np.sqrt(R[:, i] @ R[:, i]), 
            1.0
		)
for i in range(3):
	for j in range(i + 1, 3):
		assert np.isclose(
			R[:, i] @ R[:, j], 
			0.0
			 ), f"{i},{j}번 열이 직교하지 않음"

@pytest.mark.parametrize("rot_func", ROT_FUNCS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(rot_func, theta):
	R = rot_func(theta)

	assert np.isclose(det(R), 1.0)

@pytest.mark.parametrize("rot_func", ROT_FUNCS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(rot_func, theta):
	R = rot_func(theta)

	assert np.allclose(
		np.linalg.inv(R),
	    R.T)

def test_gram_schmidt_restores_orthogonality():
	A = np.array([
		[1.0, 0.01, 0.02],
		[0.0, 1.0, 0.01],
		[0.0, 0.0, 1.0],
	])

	Q = gram_schmidt(A)

	assert orthogonality_error(Q) < 1e-12
	assert np.isclose(det(Q), 1.0)
	assert is_rotation(Q)
   


