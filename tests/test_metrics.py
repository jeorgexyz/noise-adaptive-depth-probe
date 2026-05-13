"""
Unit tests for metrics calculation module.
"""
import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from metrics import (
    calculate_ghz_fidelity,
    calculate_parity_oscillation,
    calculate_heavy_output_frequency
)


class TestGHZFidelity:
    """Test GHZ fidelity calculation."""
    
    def test_perfect_ghz(self):
        """Test fidelity of perfect GHZ state."""
        counts = {'0000': 500, '1111': 500}
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        assert fidelity == 1.0
    
    def test_no_entanglement(self):
        """Test fidelity when no entanglement present."""
        # Uniform distribution (completely mixed)
        counts = {f'{i:04b}': 62 for i in range(16)}  # 16 outcomes, ~62 each
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        assert fidelity < 0.2  # Should be very low
    
    def test_partial_ghz(self):
        """Test fidelity with noise."""
        counts = {
            '0000': 400,
            '1111': 400,
            '0001': 50,
            '0010': 50,
            '0100': 50,
            '1000': 50
        }
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        assert 0.7 < fidelity < 0.9  # Should be moderate
    
    def test_different_qubit_counts(self):
        """Test fidelity calculation for different system sizes."""
        # 2 qubits
        counts_2q = {'00': 500, '11': 500}
        fid_2q = calculate_ghz_fidelity(counts_2q, n_qubits=2, shots=1000)
        assert fid_2q == 1.0
        
        # 3 qubits
        counts_3q = {'000': 500, '111': 500}
        fid_3q = calculate_ghz_fidelity(counts_3q, n_qubits=3, shots=1000)
        assert fid_3q == 1.0
    
    def test_bounds(self):
        """Test that fidelity is bounded [0,1]."""
        counts = {'0000': 300, '1111': 700}
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        assert 0 <= fidelity <= 1


class TestParityOscillation:
    """Test parity expectation calculation."""
    
    def test_all_even_parity(self):
        """Test parity when all outcomes have even parity."""
        counts = {'0000': 250, '0011': 250, '1100': 250, '1111': 250}
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        assert parity == 1.0  # All even parity
    
    def test_all_odd_parity(self):
        """Test parity when all outcomes have odd parity."""
        counts = {'0001': 250, '0010': 250, '0100': 250, '1000': 250}
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        assert parity == -1.0  # All odd parity
    
    def test_mixed_parity(self):
        """Test parity with mixed outcomes."""
        counts = {'0000': 500, '0001': 500}  # Half even, half odd
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        assert parity == 0.0  # Balanced
    
    def test_ghz_state_parity(self):
        """Test parity of GHZ state (should be high)."""
        counts = {'0000': 500, '1111': 500}
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        assert parity == 1.0  # Perfect GHZ has even parity
    
    def test_bounds(self):
        """Test that parity is bounded [-1,1]."""
        counts = {'0000': 600, '0001': 400}
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        assert -1 <= parity <= 1


class TestHeavyOutputFrequency:
    """Test Heavy Output Frequency (HOG) calculation."""
    
    def test_perfect_concentration(self):
        """Test HOG when all counts in single outcome."""
        counts = {'0000': 1000}
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        assert hog == 1.0  # All weight in one outcome
    
    def test_uniform_distribution(self):
        """Test HOG for uniform distribution."""
        counts = {f'{i:04b}': 62 for i in range(16)}
        counts['0000'] += 8  # Make total 1000
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        assert 0.4 < hog < 0.6  # Should be around 0.5 for uniform
    
    def test_bimodal_distribution(self):
        """Test HOG for GHZ-like distribution."""
        counts = {'0000': 500, '1111': 500}
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        assert hog == 1.0  # Both above median
    
    def test_bounds(self):
        """Test that HOG is bounded [0,1]."""
        counts = {'0000': 400, '1111': 300, '0001': 200, '0010': 100}
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        assert 0 <= hog <= 1


class TestMetricConsistency:
    """Test consistency between metrics."""
    
    def test_perfect_state_consistency(self):
        """Test that perfect GHZ gives expected metrics."""
        counts = {'0000': 500, '1111': 500}
        
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        
        assert fidelity == 1.0
        assert parity == 1.0
        assert hog == 1.0
    
    def test_noisy_state_consistency(self):
        """Test metrics for noisy state."""
        counts = {
            '0000': 400,
            '1111': 400,
            '0001': 100,
            '0010': 100
        }
        
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        
        # All should indicate some degradation
        assert fidelity < 1.0
        assert parity < 1.0
        assert hog > 0.5  # Still some structure


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_counts(self):
        """Test handling of empty counts dictionary."""
        counts = {}
        # Should handle gracefully (return 0 or raise error)
        try:
            fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
            assert fidelity == 0.0
        except (ValueError, ZeroDivisionError):
            pass  # Also acceptable
    
    def test_single_outcome(self):
        """Test with only one outcome."""
        counts = {'0000': 1000}
        
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        parity = calculate_parity_oscillation(counts, n_qubits=4, shots=1000)
        hog = calculate_heavy_output_frequency(counts, shots=1000)
        
        # All metrics should handle this
        assert isinstance(fidelity, float)
        assert isinstance(parity, float)
        assert isinstance(hog, float)
    
    def test_shot_mismatch(self):
        """Test when sum of counts doesn't match shots."""
        counts = {'0000': 500, '1111': 400}  # Only 900 total
        
        # Should still calculate (using actual total)
        fidelity = calculate_ghz_fidelity(counts, n_qubits=4, shots=1000)
        assert isinstance(fidelity, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])