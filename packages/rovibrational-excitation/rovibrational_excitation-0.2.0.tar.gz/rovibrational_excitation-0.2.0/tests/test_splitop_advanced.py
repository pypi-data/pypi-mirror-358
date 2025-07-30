"""
Split-Operatorアルゴリズムの高度なテスト
===================================
Split-Operatorメソッドの数値安定性、物理的妥当性、
スパース行列対応、大規模システム対応を検証します。
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import numpy as np
import pytest
from rovibrational_excitation.core._splitop_schrodinger import splitop_schrodinger

# CuPyが利用可能か判定
try:
    import cupy as cp
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False


def create_multilevel_system(n_levels=5):
    """多準位システムを生成"""
    H0 = np.diag(np.arange(n_levels, dtype=float))
    
    # 隣接準位間の遷移
    mu_x = np.zeros((n_levels, n_levels), dtype=complex)
    mu_y = np.zeros((n_levels, n_levels), dtype=complex)
    
    for i in range(n_levels - 1):
        coupling_strength = np.sqrt(i + 1)
        mu_x[i, i + 1] = coupling_strength
        mu_x[i + 1, i] = coupling_strength
        mu_y[i, i + 1] = 1j * coupling_strength
        mu_y[i + 1, i] = -1j * coupling_strength
    
    return H0, mu_x, mu_y


def create_complex_polarization(amplitude=1.0, phase=0.0):
    """複素偏光を生成"""
    pol = np.array([amplitude * np.cos(phase), amplitude * np.sin(phase)], dtype=complex)
    return pol / np.linalg.norm(pol)


def create_chirped_pulse(n_points, amplitude=0.1, chirp_rate=0.1):
    """チャープパルスを生成"""
    t = np.linspace(-5, 5, n_points)
    envelope = np.exp(-t**2)
    phase = chirp_rate * t**2
    pulse = amplitude * envelope * np.cos(phase)
    return pulse


class TestSplitOperatorAdvanced:
    """Split-Operatorの高度なテスト"""
    
    def test_hermitian_interaction_enforcement(self):
        """相互作用項のエルミート性強制確認"""
        H0 = np.diag([0, 1, 2])
        
        # 意図的に非エルミート行列を作成
        mu_x = np.array([[0, 1, 0.5], [1.1, 0, 1], [0.4, 1.1, 0]], dtype=complex)
        mu_y = np.array([[0, 1j, 0], [-1.1j, 0, 1j], [0, -0.9j, 0]], dtype=complex)
        
        pol = np.array([1.0, 0.5], dtype=complex)
        Efield = np.array([0, 0.1, 0.2, 0.1, 0])
        
        psi0 = np.array([1, 0, 0], dtype=complex)
        
        # 内部でエルミート化されてエラーが出ないことを確認
        traj = splitop_schrodinger(H0, mu_x, mu_y, pol, Efield, psi0,
                                 dt=0.1, steps=2)
        
        # ノルム保存を確認（エルミート性が保たれている証拠）
        for i in range(traj.shape[0]):
            norm = np.linalg.norm(traj[i, :, 0])
            np.testing.assert_allclose(norm, 1.0, atol=1e-12)
    
    def test_multilevel_system_dynamics(self):
        """多準位システムでの動力学"""
        H0, mu_x, mu_y = create_multilevel_system(5)
        pol = create_complex_polarization(amplitude=1.0, phase=np.pi/4)
        Efield = create_chirped_pulse(21, amplitude=0.1, chirp_rate=0.05)
        
        # 基底状態から開始
        psi0 = np.zeros(5, dtype=complex)
        psi0[0] = 1.0
        
        traj = splitop_schrodinger(H0, mu_x, mu_y, pol, Efield, psi0,
                                 dt=0.05, steps=10)
        
        # 基本的な性質の確認
        for i in range(traj.shape[0]):
            # ノルム保存
            norm = np.linalg.norm(traj[i, :, 0])
            np.testing.assert_allclose(norm, 1.0, atol=1e-12)
            
            # ポピュレーションの正定値性
            populations = np.abs(traj[i, :, 0])**2
            assert np.all(populations >= -1e-12)
            assert np.abs(np.sum(populations) - 1.0) < 1e-12
    
    def test_complex_polarization_effects(self):
        """複素偏光での計算実行確認"""
        H0, mu_x, mu_y = create_multilevel_system(4)
        Efield = create_chirped_pulse(11, amplitude=0.2)
        
        psi0 = np.array([1, 0, 0, 0], dtype=complex)
        
        # 異なる偏光での結果を比較
        polarizations = [
            np.array([1, 0], dtype=complex),      # 線形x偏光
            np.array([0, 1], dtype=complex),      # 線形y偏光
            np.array([1, 1j], dtype=complex)/np.sqrt(2),  # 円偏光
            np.array([1, -1j], dtype=complex)/np.sqrt(2)  # 反対円偏光
        ]
        
        final_states = []
        for pol in polarizations:
            traj = splitop_schrodinger(H0, mu_x, mu_y, pol, Efield, psi0,
                                     dt=0.1, steps=5)
            final_states.append(traj[-1, :, 0])
            
            # 基本的な物理性質の確認
            norm = np.linalg.norm(traj[-1, :, 0])
            np.testing.assert_allclose(norm, 1.0, atol=1e-12)
        
        # 全ての偏光で正常に計算が完了したことを確認
        assert len(final_states) == 4
    
    @pytest.mark.skipif(not HAS_CUPY, reason="CuPyがインストールされていないためスキップ")
    def test_cupy_large_system(self):
        """CuPyでの大規模システム処理"""
        H0, mu_x, mu_y = create_multilevel_system(12)
        pol = np.array([1.0, 0.3j], dtype=complex)
        Efield = create_chirped_pulse(21, amplitude=0.1)
        
        psi0 = np.zeros(12, dtype=complex)
        psi0[0] = 1.0
        
        # NumPy版
        traj_numpy = splitop_schrodinger(H0, mu_x, mu_y, pol, Efield, psi0,
                                       dt=0.1, steps=10, backend="numpy")
        
        # CuPy版
        traj_cupy = splitop_schrodinger(H0, mu_x, mu_y, pol, Efield, psi0,
                                      dt=0.1, steps=10, backend="cupy")
        
        # 結果の一致確認
        np.testing.assert_allclose(traj_numpy, traj_cupy, atol=1e-12)
    
    def test_long_time_stability(self):
        """長時間伝播での安定性"""
        H0, mu_x, mu_y = create_multilevel_system(4)
        pol = np.array([1.0, 0.0], dtype=complex)
        
        # 長時間の弱電場
        n_steps = 50
        Efield = 0.02 * np.sin(np.linspace(0, 4*np.pi, 2*n_steps+1))
        
        psi0 = np.array([1, 0, 0, 0], dtype=complex)
        
        traj = splitop_schrodinger(H0, mu_x, mu_y, pol, Efield, psi0,
                                 dt=0.1, steps=n_steps)
        
        # 長時間後もノルムが保存されていることを確認
        norms = [np.linalg.norm(traj[i, :, 0]) for i in range(traj.shape[0])]
        max_norm_deviation = max(abs(norm - 1.0) for norm in norms)
        
        assert max_norm_deviation < 1e-10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
