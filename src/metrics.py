"""Metrics for analyzing circuit performance."""
import numpy as np

def calculate_ghz_fidelity(counts, n_qubits, shots):
    """Calculate GHZ state fidelity from measurement counts."""
    all_zeros = '0' * n_qubits
    all_ones = '1' * n_qubits
    
    count_zeros = counts.get(all_zeros, 0)
    count_ones = counts.get(all_ones, 0)
    
    fidelity = (count_zeros + count_ones) / shots
    return fidelity


def calculate_parity_oscillation(counts, n_qubits, shots):
    """Calculate parity-based metric: ⟨Z₀Z₁...Zₙ⟩"""
    parity_sum = 0
    for bitstring, count in counts.items():
        num_ones = bitstring.count('1')
        parity = 1 if num_ones % 2 == 0 else -1
        parity_sum += parity * count
    
    parity_expectation = parity_sum / shots
    return parity_expectation


def calculate_heavy_output_frequency(counts, shots):
    """Heavy Output Generation (HOG) metric."""
    probabilities = {k: v / shots for k, v in counts.items()}
    median_prob = np.median(list(probabilities.values()))
    
    heavy_count = sum(count for bitstring, count in counts.items() 
                      if probabilities[bitstring] > median_prob)
    
    return heavy_count / shots