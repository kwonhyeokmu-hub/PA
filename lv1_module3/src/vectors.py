import numpy as np

def dot(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    return np.sum(a*b)

def norm(v):
    v= np.asarray(v, dtype=float)

    return np.sqrt(dot(v,v))


def normalize(v, eps=1e-12):
    v = np.asarray(v, dtype=float)
    
    length = norm(v)

    if length <= eps:
        raise ValueError(
            f"영백터는 정규화할 수 없습니다."
            f"(|v|={length:.3e} <= eps={eps:1e})."
            "방향이 정의되지 않으므로 호출부에서 예외를 처리하세요."
        )

    return v/ length

def angle_between(a, b, degrees=True):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    na = norm(a)
    nb = norm(b)

    if na <= 1e-12 or nb <= 1e-12:
        raise ValueError("영벡터와의 사이각은 정의되지 않습니다.")

    cos_theta = dot(a,b) / (na * nb)

    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    theta = np.arccos(cos_theta)

    if degrees:
        return np. degrees(theta)

    return theta

def project(a, b, eps=1e-12):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    denominator = dot(b,b)

    if denominator <= eps:
        raise ValueError("영백터 방향으로 정사영할 수 없습니다.")

    scale = dot(a, b) / denominator

    return scale * b


def reject(a,b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    
    return a - project(a,b)

def skew(a):
    a= np.asarray(a, dtype=float)
    
    return np.array([
        [0.0, -a[2], a[1]],
        [a[2], 0.0, -a[0]],
        [-a[1], a[0], 0.0]
    ])

def cross(a,b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    
    return skew(a) @ b

def plane_normal(p1, p2, p3, eps=1e-12):
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    p3 = np.asarray(p3, dtype=float)

    u = p2 - p1
    v = p3 - p1

    n= cross(u,v)

    if norm(n) <= eps:
        raise ValueError(
            "세 점이 일직선이라 평면이 하나로 정해지지 않습니다."
        )

    return normalize(n, eps=eps)
    
def row_echelon(A, eps=1e-12):
    U = np.array(A, dtype=float, copy=True)


    rows, cols =  U.shape
    
    pivot_row = 0
    pivots = []
    swaps = 0

    for col in range(cols):

        if pivot_row >= rows:
            break

        best_row =  pivot_row + np.argmax(
            np.abs(U[pivot_row:,col])
        )

        if abs(U[best_row, col]) <= eps:
            continue

        if best_row != pivot_row:
            U[[pivot_row, best_row]] = U[[best_row, pivot_row]]
            swaps += 1

        for r in range(pivot_row + 1, rows):
            
            factor = U[r,col] / U[pivot_row, col]
            
            U[r] =  U[r] - factor * U[pivot_row]

        pivots.append(col)
        
        pivot_row += 1

    U[np.abs(U) < eps] = 0.0

    return U, pivots, swaps

def rank(A, eps=1e-12):
    U, pivots, swaps = row_echelon(A, eps=eps)
                                  
    return len(pivots)

def det(A, eps=1e-12):
    A =  np.asarray(A, dtype=float)

    if A.ndim != 2 or A. shape[0] != A.shape[1]:
        raise ValueError("행렬식은 정사각행렬에서만 정의됩니다.")

    U, pivots, swaps = row_echelon(A, eps=eps)

    d = 1.0

    for i in range(U.shape[0]):
        d *= U[i, i]

    if swaps % 2 == 1:
        d = -d

    return float(d)

def gauss_eliminate(A, b, pivoting=True, verbose=False):
    A = np.array(A, dtype=float, copy=True)
    b = np.asarray(b, dtype=float).reshape(-1)

    n = A.shape[0]

    M = np.hstack([
        A,
        b.reshape(-1, 1)
    ])

    steps = [M.copy()]

    if verbose:
        print("[초기] 첨가행렬 [A|b]")
        print(np.array2string(
            M,
            precision=4,
            suppress_small=True
        ))

    for col in range(n):

        if pivoting:
            candidate = col + int(
                np.argmax(np.abs(M[col:, col]))
            )
            if candidate != col:
                M[[col, candidate]] = M[[candidate, col]]
                steps.append(M.copy())

                if verbose:
                    print(
                        f"\n[{col + 1}단계-b] "
                        f"행 {col} <-> 행 {candidate} 교환"
                    )
                    print(np.array2string(
                        M,
                        precision=4,
                        suppress_small=True
                    ))

        pivot = M[col, col] 

        if pivot == 0.0:
            raise ZeroDivisionError(
                f"{col}번 피벗이 0 입니다. 해가 유일하지 않습니다."
            )
        for r in range(col + 1, n):
            factor = M[r, col] / pivot

            M[r, col:] -= factor * M[col, col:]
            M[r, col] = 0.0

        steps.append(M.copy())

        if verbose:
            print(
                f"\n[{col + 1}]단계-a] "
                f"{col}열 아래를 0으로 소거"
            )
            print(np.array2string(
                M,
                precision=4,
                suppress_small=True
            ))

    x = np.zeros(n)

    for i in range(n - 1, -1, -1):
        x[i] = (
            M[i, n]
            - M[i, i + 1:n] @ x[i + 1:n]
        ) / M[i, i]

    if verbose:
        print(
            "\n[후진대입] x =",
            np.array2string(
                x,
                precision=6,
                suppress_small=True
            )
        )
    return x, steps


def inverse_gauss_jordan(A, eps=1e-12):
    A = np.array(A, dtype=float, copy=True)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(
            "역행렬은 정사각행렬에서만 정의됩니다."
        )

    n = A.shape[0]

    M = np.hstack([
        A,
        np.eye(n)
    ])

    for col in range(n):
        candidate = col + int(
            np.argmax(np.abs(M[col:, col]))
        )
        if abs(M[candidate, col]) <= eps:
            raise ValueError(
                "역행렬이 존재하지 않습니다."
            )

        if candidate != col:
            M[[col, candidate]] = M[[candidate, col]]

        pivot = M[col, col]
        M[col] = M[col] / pivot

        for r in range(n):
            if r == col:
                continue

            factor = M[r, col]
            M[r] = M[r] - factor * M[col]

    return M[:, n:]

  

                    
