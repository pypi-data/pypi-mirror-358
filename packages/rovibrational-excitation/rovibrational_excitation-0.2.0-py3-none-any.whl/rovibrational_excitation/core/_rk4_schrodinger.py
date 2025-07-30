# _rk4_schrodinger.py  ----------------------------------------------
"""
4-th order Runge–Kutta propagator
=================================
* backend="numpy"  →  CPU  (NumPy / Numba)
* backend="cupy"   →  GPU  (CuPy RawKernel)

電場配列は奇数・偶数どちらの長さでも OK。
"""

from __future__ import annotations
import numpy as np
from typing import Literal, Tuple

# ------------------------------------------------------------------ #
# 0.  電場ヘルパ：3-tuple 配列 & step 数を返す                       #
# ------------------------------------------------------------------ #
def _field_to_triplets(field: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    奇数長 → そのまま
    偶数長 → 末尾 1 点をバッサリ捨てる
    """
    if field.ndim != 1 or field.size < 3:
        raise ValueError("E-field must be 1-D with length ≥3")

    steps = (field.size - 1) // 2    # 必ず整数
    ex1 = field[0:-2:2]
    ex2 = field[1:-1:2]
    ex4 = field[2::2]
    return np.column_stack((ex1, ex2, ex4)).astype(np.float64, copy=False), steps


# ================================================================== #
# 1.  CPU (NumPy / Numba)                                            #
# ================================================================== #
try:
    from numba import njit
except ImportError:             # numba 不在でも動くダミー
    def njit(*args, **kwargs):  # type: ignore
        def deco(f): return f
        return deco

@njit(
    "c16[:, :](c16[:, :], c16[:, :], c16[:, :],"
    "f8[:, :], f8[:, :],"
    "c16[:], f8, i8, i8, b1, b1)",
    fastmath=True, cache=True,
)
def _rk4_cpu(H0, mux, muy,
             Ex3, Ey3,
             psi0, dt, steps, stride,
             record, renorm):
    psi = psi0.copy()
    dim = psi.size
    n_out = steps // stride + 1 if record else 1
    out = np.empty((n_out, dim), np.complex128)
    out[0] = psi
    idx = 1
    buf = np.empty_like(psi)
    k1 = np.empty_like(psi)
    k2 = np.empty_like(psi)
    k3 = np.empty_like(psi)
    k4 = np.empty_like(psi)

    for s in range(steps):
        ex1, ex2, ex4 = Ex3[s]
        ey1, ey2, ey4 = Ey3[s]
        H1 = H0 + mux*ex1 + muy*ey1
        H2 = H0 + mux*ex2 + muy*ey2   # =H3
        H4 = H0 + mux*ex4 + muy*ey4
        k1[:] = -1j * (H1 @ psi)
        buf[:] = psi + 0.5*dt*k1
        k2[:] = -1j * (H2 @ buf)
        buf[:] = psi + 0.5*dt*k2
        k3[:] = -1j * (H2 @ buf)
        buf[:] = psi + dt*k3
        k4[:] = -1j * (H4 @ buf)
        psi += (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        if renorm:
            psi *= 1/np.sqrt((psi.conj()@psi).real)
        if record and ((s+1) % stride == 0):
            out[idx] = psi
            idx += 1
    if not record:
        out[0] = psi
    return out

# ================================================================== #
# 2.  GPU (CuPy RawKernel)                                           #
# ================================================================== #
try:
    import cupy as cp
except ImportError:
    cp = None

_KERNEL_SRC_TEMPLATE = r"""
extern "C" __global__
void rk4_loop(const cuDoubleComplex* __restrict__ H0,
              const cuDoubleComplex* __restrict__ mux,
              const cuDoubleComplex* __restrict__ muy,
              const double*  __restrict__ Ex3,
              const double*  __restrict__ Ey3,
              cuDoubleComplex* __restrict__ psi)
{{
    const int DIM   = {dim};
    const int STEPS = {steps};
    const double dt = {dt};

    extern __shared__ cuDoubleComplex sh[];
    cuDoubleComplex* k1  = sh;
    cuDoubleComplex* k2  = k1  + DIM;
    cuDoubleComplex* k3  = k2  + DIM;
    cuDoubleComplex* k4  = k3  + DIM;
    cuDoubleComplex* buf = k4  + DIM;

    const int row = threadIdx.x;
    if (row < DIM) buf[row] = psi[row];
    __syncthreads();

#define MATVEC(Hmat, ex, ey, dst)                                   \
    if (row < DIM) {{                                               \
        cuDoubleComplex acc = make_cuDoubleComplex(0.0, 0.0);       \
        for (int col = 0; col < DIM; ++col) {{                      \
            cuDoubleComplex hij = Hmat[row*DIM+col];                \
            cuDoubleComplex mx  = mux[row*DIM+col];                 \
            cuDoubleComplex my  = muy[row*DIM+col];                 \
            hij = cuCadd(hij,                                       \
                  cuCadd(make_cuDoubleComplex(mx.x*ex, mx.y*ex),    \
                        make_cuDoubleComplex(my.x*ey, my.y*ey)));    \
            acc = cuCadd(acc, cuCmul(hij, buf[col]));               \
        }}                                                          \
        dst[row] = cuCmul(make_cuDoubleComplex(0.0,-1.0), acc);     \
    }}                                                              \
    __syncthreads();

    for (int s = 0; s < STEPS; ++s) {{
        const double ex1 = Ex3[3*s],   ex2 = Ex3[3*s+1], ex4 = Ex3[3*s+2];
        const double ey1 = Ey3[3*s],   ey2 = Ey3[3*s+1], ey4 = Ey3[3*s+2];

        MATVEC(H0, ex1, ey1, k1)

        if (row < DIM) buf[row] = cuCadd(buf[row],
                 make_cuDoubleComplex(0.5*dt*k1[row].x, 0.5*dt*k1[row].y));
        __syncthreads();

        MATVEC(H0, ex2, ey2, k2)

        if (row < DIM) buf[row] = cuCadd(cuCsub(buf[row],
                 make_cuDoubleComplex(0.5*dt*k1[row].x, 0.5*dt*k1[row].y)),
                 make_cuDoubleComplex(0.5*dt*k2[row].x, 0.5*dt*k2[row].y));
        __syncthreads();

        MATVEC(H0, ex2, ey2, k3)

        if (row < DIM) buf[row] = cuCadd(cuCsub(buf[row],
                 make_cuDoubleComplex(0.5*dt*k2[row].x, 0.5*dt*k2[row].y)),
                 make_cuDoubleComplex(dt*k3[row].x, dt*k3[row].y));
        __syncthreads();

        MATVEC(H0, ex4, ey4, k4)

        if (row < DIM) {{
            cuDoubleComplex inc = cuCadd(k1[row],
                 cuCadd(k4[row], cuCadd(k2[row], k2[row])));
            inc = cuCadd(inc, cuCadd(k3[row], k3[row])); // +2k3
            inc = make_cuDoubleComplex((dt/6.0)*inc.x, (dt/6.0)*inc.y);
            buf[row] = cuCadd(buf[row], inc);
        }}
        __syncthreads();
    }}

    if (row < DIM) psi[row] = buf[row];
}}
"""  # noqa: E501 (long CUDA string)

def _rk4_gpu(H0, mux, muy,
             Ex3, Ey3,
             psi0, dt: float, steps: int):
    if cp is None:
        raise RuntimeError("backend='cupy' but CuPy is not installed")
    dim = H0.shape[0]
    src = _KERNEL_SRC_TEMPLATE.format(dim=dim, steps=steps, dt=dt)
    mod = cp.RawModule(code=src, options=("-std=c++17",),
                       name_expressions=("rk4_loop",))
    kern = mod.get_function("rk4_loop")

    H0_d  = cp.asarray(H0)
    mux_d = cp.asarray(mux)
    muy_d = cp.asarray(muy)
    Ex3_d = cp.asarray(Ex3)
    Ey3_d = cp.asarray(Ey3)
    psi_d = cp.asarray(psi0)

    shm = dim * 5 * 16  # k1..k4+buf  (complex128=16B)
    kern((1,), (dim,), (H0_d, mux_d, muy_d, Ex3_d, Ey3_d, psi_d),
         shared_mem=shm)
    return psi_d.get()[None, :]

# ------------------------------------------------------------------ #
# 3.  公開 API                                                       #
# ------------------------------------------------------------------ #
def rk4_schrodinger(
    H0: np.ndarray,
    mux: np.ndarray, muy: np.ndarray,
    E_x: np.ndarray, E_y: np.ndarray,
    psi0: np.ndarray,
    dt: float,
    *,
    return_traj: bool = False,
    renorm: bool = False,
    stride: int = 1,
    backend: Literal["numpy", "cupy"] = "numpy",
) -> np.ndarray:
    """
    TDSE propagator (4th-order RK).

    Returns
    -------
    psi_traj : (n_sample, dim) complex128
        return_traj=False → shape (1, dim)
    """
    Ex3, steps = _field_to_triplets(np.asarray(E_x))
    Ey3, _     = _field_to_triplets(np.asarray(E_y))
    psi0 = np.asarray(psi0, np.complex128).ravel()

    if backend == "cupy":
        return _rk4_gpu(
            H0, mux, muy,
            Ex3, Ey3,
            psi0, float(dt), steps)

    return _rk4_cpu(
        np.ascontiguousarray(H0,  np.complex128),
        np.ascontiguousarray(mux, np.complex128),
        np.ascontiguousarray(muy, np.complex128),
        Ex3, Ey3,
        psi0, float(dt), steps, stride,
        return_traj, renorm)
