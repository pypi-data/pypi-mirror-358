"""
rovibrational_excitation/core/propagator.py
------------------------------------------
* axes="xy"  → Ex ↔ μ_x,  Ey ↔ μ_y   (デフォルト)
* axes="zx"  → Ex ↔ μ_z,  Ey ↔ μ_x
"""

from __future__ import annotations
from typing import Iterable, Tuple, Union, Optional, TYPE_CHECKING

import numpy as np

# ---------------------------------------------------------------------
# optional CuPy
try:
    import cupy as _cp                   # noqa: N811
except ImportError:
    _cp = None                           # type: ignore[assignment]

# ---------------------------------------------------------------------
# type-hints
if TYPE_CHECKING:
    Array = Union[np.ndarray, "_cp.ndarray"]
    from .electric_field import ElectricField
    from rovibrational_excitation.dipole.linmol.cache import LinMolDipoleMatrix
else:
    Array = np.ndarray  # runtime dummy

# ---------------------------------------------------------------------
# constants / helpers
_DIRAC_HBAR = 6.62607015e-019 / (2*np.pi)  # J fs

def _cm_to_rad_phz(mu: Array) -> Array:
    """μ (C·m) → rad / (PHz/(V·m⁻¹))."""
    return mu / (_DIRAC_HBAR)      # divide once; xp 対応は呼び出し側で

def _backend(name: str):
    if name == "cupy":
        if _cp is None:
            raise RuntimeError("CuPy backend requested but CuPy not installed")
        return _cp
    return np

def _pick_mu(dip, axis: str) -> Array:
    attr = f"mu_{axis}"
    if not hasattr(dip, attr):
        raise AttributeError(f"{type(dip).__name__} has no attribute '{attr}'")
    return getattr(dip, attr)

# ---------------------------------------------------------------------
def _prepare_args(
    H0: Array,
    E: "ElectricField",
    dip: "LinMolDipoleMatrix",
    *,
    axes: str = "xy",
    dt: Optional[float] = None,
) -> Tuple[Array, Array, Array, Array, Array, float, int]:
    """
    共通前処理

    Returns (順序は旧バージョンと互換):
        H0, μ_a, μ_b, Ex, Ey, dt, steps
        └─ μ_a: Ex に対応 / μ_b: Ey に対応
    """
    axes = axes.lower()
    if len(axes) != 2 or any(a not in "xyz" for a in axes):
        raise ValueError("axes must be like 'xy', 'zx', ...")

    ax0, ax1 = axes
    xp = _cp if _cp is not None else np

    dt_half = E.dt if dt is None else dt / 2

    Ex, Ey  = E.Efield[:, 0], E.Efield[:, 1]
    
    # stepsを計算
    steps = (len(Ex) - 1) // 2

    # スパース行列対応: スパース行列の場合はそのまま使用
    mu_a_raw = _pick_mu(dip, ax0)
    mu_b_raw = _pick_mu(dip, ax1)
    
    try:
        import scipy.sparse as sp
        if sp.issparse(mu_a_raw):
            mu_a = _cm_to_rad_phz(mu_a_raw)  # スパース行列の場合はそのまま
        else:
            mu_a = xp.asarray(_cm_to_rad_phz(mu_a_raw))
        if sp.issparse(mu_b_raw):
            mu_b = _cm_to_rad_phz(mu_b_raw)  # スパース行列の場合はそのまま
        else:
            mu_b = xp.asarray(_cm_to_rad_phz(mu_b_raw))
    except ImportError:
        mu_a = xp.asarray(_cm_to_rad_phz(mu_a_raw))
        mu_b = xp.asarray(_cm_to_rad_phz(mu_b_raw))

    return xp.asarray(H0), mu_a, mu_b, xp.asarray(Ex), xp.asarray(Ey), dt_half * 2, steps

# ---------------------------------------------------------------------
# RK4 kernels
from ._rk4_lvne        import rk4_lvne_traj, rk4_lvne
from ._rk4_schrodinger import rk4_schrodinger
from ._splitop_schrodinger import splitop_schrodinger

# ---------------------------------------------------------------------
def schrodinger_propagation(
    H0: Array,
    Efield: "ElectricField",
    dipole_matrix: "LinMolDipoleMatrix",
    psi0: Array,
    *,
    axes: str = "xy",
    return_traj: bool = True,
    return_time_psi: bool = False,
    sample_stride: int = 1,
    backend: str = "numpy",
) -> Array:
    xp = _backend(backend)
    H0_, mu_a, mu_b, Ex, Ey, dt, steps = _prepare_args(
        H0, Efield, dipole_matrix, axes=axes
    )
    # ---------------------------------------------------------
    # 0) まず split-operator が適用できるか試す
    #    （ElectricField に「一定偏光＋実スカラー場」が
    #      保持されている場合だけ使用）
    # ---------------------------------------------------------
    try:
        Escalar, pol = Efield.get_scalar_and_pol()          # ← ElectricField で追加した util

        traj_split = splitop_schrodinger(
            H0_,
            mu_a, mu_b,                                    # μ_x, μ_y
            pol,                                           # (2,) complex
            Escalar,                                       # (N,) real
            xp.asarray(psi0), dt,
            steps=(len(Escalar)-1)//2,
            sample_stride=sample_stride,
            backend=backend,
        )
        
        # 形状を調整
        result = traj_split.squeeze()
        if result.ndim == 1:
            result = result.reshape(1, -1)
        
        if return_traj:
            if return_time_psi:
                # resultがtupleの場合はshapeアクセスできないので修正
                if isinstance(result, tuple):
                    # すでにtupleになっている場合はそのまま返す
                    return result
                time_psi = xp.arange(0,
                                     result.shape[0]*dt*sample_stride,
                                     dt*sample_stride)
                return time_psi, result
            return result
        else:
            return result[-1:].reshape((1, len(psi0)))

    except ValueError:
        # 偏光が時間依存 → 旧来の RK4 へフォールバック
        pass
    
    rk4_args = (H0_, mu_a, mu_b, Ex, Ey, xp.asarray(psi0), dt)
    
    if return_traj:
        psi_traj = rk4_schrodinger(
            *rk4_args, return_traj=return_traj, stride=sample_stride
            )
        if return_time_psi:
            dt_psi = dt * sample_stride
            len_traj = psi_traj.shape[0]
            time_psi = xp.arange(0, len_traj*dt_psi, dt_psi)
            return time_psi, psi_traj
        else:
            return psi_traj
    else:
        result = rk4_schrodinger(*rk4_args)
        return result.reshape((1, len(psi0)))

# ---------------------------------------------------------------------
def mixed_state_propagation(
    H0: Array,
    Efield: "ElectricField",
    psi0_array: Iterable[Array],
    dipole_matrix: "LinMolDipoleMatrix",
    *,
    axes: str = "xy",
    return_traj: bool = True,
    return_time_rho: bool = False,
    sample_stride: int = 1,
    backend: str = "numpy",
) -> Array:
    xp = _backend(backend)
    dim = psi0_array[0].shape[0]
    steps_out = (len(Efield.tlist) // 2) // sample_stride + 1
    rho_out = xp.zeros((steps_out, dim, dim), dtype=xp.complex128) if return_traj else xp.zeros((dim, dim), dtype=xp.complex128)

    for psi0 in psi0_array:
        result = schrodinger_propagation(
            H0, Efield, dipole_matrix, psi0,
            axes=axes, return_traj=return_traj,
            return_time_psi=False,  # time情報は不要
            sample_stride=sample_stride, backend=backend
        )
        
        # resultがtupleの場合の処理
        if isinstance(result, tuple):
            psi_t = result[1]
        else:
            psi_t = result
            
        if return_traj:
            rho_out += xp.einsum("ti, tj -> tij", psi_t, psi_t.conj())
        else:
            rho_out += psi_t[0] @ psi_t[0].conj().T
            
    if return_traj:
        if return_time_rho:
            dt_rho = Efield.dt_state * sample_stride
            steps = Efield.steps_state
            time_psi = xp.arange(0, (steps+1)*dt_rho, dt_rho)
            return time_psi, rho_out
        else:
            return rho_out
    else:
        return rho_out

# ---------------------------------------------------------------------
def liouville_propagation(
    H0: Array,
    Efield: "ElectricField",
    dipole_matrix: "LinMolDipoleMatrix",
    rho0: Array,
    *,
    axes: str = "xy",
    return_traj: bool = True,
    sample_stride: int = 1,
    backend: str = "numpy",
) -> Array:
    xp = _backend(backend)
    H0_, mu_a, mu_b, Ex, Ey, dt, steps = _prepare_args(
        H0, Efield, dipole_matrix, axes=axes
    )

    rk4_args = (H0_, mu_a, mu_b, Ex, Ey, xp.asarray(rho0), dt, steps)
    rk4 = rk4_lvne_traj if return_traj else rk4_lvne
    return rk4(*rk4_args, sample_stride) if return_traj else rk4(*rk4_args)
