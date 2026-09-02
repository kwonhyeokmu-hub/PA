import numpy as np

from src.vectors import normalize, skew

def rot_x(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
      [1.0, 0.0, 0.0],
      [0.0,   c,  -s],
      [0.0,   s,   c]

    ])


def rot_y(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [ c,  0.0, s],
        [0.0, 1.0, 0.0],
        [-s, 0.0, c]
    ])         

def rot_z(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([[c, -s, 0.0],
                     [s,   c, 0.0],
                     [0.0, 0.0, 1.0]])

def rodrigues(axis, theta):

    k = normalize(axis)

    K = skew(k)

    return (
        np.eye(3)
        + np.sin(theta) * K
        + (1.0 -np.cos(theta)) * (K @ K)
    )

def orthogonality_error(R):
    R = np.asarray(R, dtype=float)

    I = np.eye(R.shape[1])
    E = R.T @ R - I

    return np.sqrt(np.sum(E * E))

def is_rotation(R, tol=1e-9):
    R = np.asarray(R, dtype=float)

    if R. shape != (3, 3):
        return False

    orthogonal = orthogonality_error(R) <= tol

    from src.vectors import det
    proper = abs(det(R) - 1.0) <= tol

    return orthogonal and proper

def gram_schmidt(A):
    A = np.array(A, dtype=float, copy=True)

    n_cols = A.shape[1]

    Q = np.zeros_like(A)

    for j in range(n_cols):

        v = A[:,j].copy()

        for i in range(j):

            v -= (Q[:, i] @ v) * Q[:, i]

        nv = np.sqrt(v @ v)

        if nv <= 1e-12:
             raise ValueError(
             f"{j}번 열이 앞선 열들에 종속이라 직교화할 수 없습니다."
                )

        Q[:, j] = v/ nv


    return Q
        



    
    