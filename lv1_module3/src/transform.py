import numpy as np
from src.vectors import gauss_eliminate


def make_T(R,t):
    R = np.asarray(R, dtype=float)
    t = np.asarray(t, dtype=float).reshape(3)

    T = np.eye(4)

    T[:3, :3] = R
    T[:3, 3] = t

    return T

def inv_T(T):
    T = np.asarray(T, dtype=float)

    R = T[:3, :3]
    t = T[:3, 3]

    R_inv = R.T
    t_inv = -R_inv @ t

    return make_T(R_inv, t_inv)

def to_homogeneous(v, w):
    v = np.asarray(v, dtype=float)

    if v.ndim == 1:
        return np.append(v, w)

    w_col = np.full((v.shape[0], 1), w)
    return np.hstack([v, w_col]) 

   
def transform_point(T, p):
    T = np.asarray(T,dtype=float)
    p_h = to_homogeneous(p, 1.0)

    result = T @ p_h
    return result[:3]

def transform_direction(T,v):
    T = np.asarray(T, dtype=float)
    v_h = to_homogeneous(v, 0.0)

    result = T @ v_h
    return result[:3]

def transform_points(T, points):
    T = np.asarray(T, dtype=float)
    points = np.asarray(points, dtype = float)

    ones = np.ones((points.shape[0], 1))
    points_h = np.hstack([points, ones]) 

    result_h =(T @ points_h.T).T
    return result_h[:, :3]

def inv_T_batch(Ts):
    Ts = np.asarray(Ts, dtype=float)

    R = Ts[:, :3, :3]
    t = Ts[:, :3, 3]

    R_inv = np.swapaxes(R, 1, 2)
    t_inv = -np.einsum("nij,nj->ni", R_inv, t)
    Tout = np.tile(np.eye(4), (Ts.shape[0], 1, 1))

    Tout[:, :3, :3] = R_inv
    Tout[:, :3, 3] = t_inv

    return Tout

def least_squares_normal_equation(A, b):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)

    ATA = A.T @ A
    ATb = A.T @ b

    x, _ = gauss_eliminate(ATA, ATb)

    residual = b - A @ x

    return x, residual

def rmse(residual):
    residual =np.asarray(residual, dtype=float)
    return np.sqrt(np.mean(residual ** 2))