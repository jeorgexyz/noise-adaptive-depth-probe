# Experimental Methodology

## Overview

This document provides detailed methodology for characterizing circuit depth thresholds on IBM Quantum hardware.

## 1. Qubit Selection

### Why Qubit Selection Matters

On heavy-hexagon architectures like IBM's Heron processors, not all qubits are equal. Gate error rates vary significantly across the chip.

### Selection Algorithm

```python
def find_best_qubit_chain(backend, chain_length=5):
    """
    Find optimal linear qubit chain by minimizing average gate error.
    
    Algorithm:
    1. Construct qubit connectivity graph from coupling map
    2. Find all linear chains of specified length
    3. Score each chain by average CZ gate error rate
    4. Return chain with lowest average error
    """
```

### Selected Chain for ibm_torino

**Qubits**: [55, 65, 66, 67, 68]  
**Average CZ error**: 0.87%  
**Selection date**: January 31, 2026

**Quality metrics**:
- Single-qubit gate error: ~0.05%
- T1 (relaxation time): ~150 μs
- T2 (dephasing time): ~120 μs
- Readout fidelity: 98.8%

## 2. Circuit Design

### Base GHZ State Preparation

Create maximally entangled state |000...0⟩ + |111...1⟩:

```
Circuit (n=4 qubits):
q0: ──H──●────────────
         │
q1: ──H──●──●─────────
            │
q2: ──H─────●──●──────
               │
q3: ──H────────●──────
```

Using native CZ gates (Heron architecture):
```python
qc.h(0)
for i in range(n_qubits - 1):
    qc.h(i + 1)
    qc.cz(i, i + 1)  # Native gate
    qc.h(i + 1)      # Effective CNOT via H-CZ-H
```

### Depth Extension

To prevent transpiler optimization, we use rotation-protected layers:

```python
for layer in range(depth - 1):
    angle = 0.1 * (layer + 1)
    
    # Forward rotation
    for i in range(n_qubits):
        qc.rz(angle, i)
    
    # Re-entangle
    for i in range(n_qubits - 1):
        qc.cz(i, i + 1)
    
    # Inverse rotation
    for i in range(n_qubits):
        qc.rz(-angle, i)
```

**Key insight**: RZ(θ) - CZ - RZ(-θ) is logically equivalent to CZ but prevents gate cancellation during transpilation, ensuring actual depth variation.

## 3. Transpilation

### Settings

```python
transpile_options = {
    'backend': backend,
    'optimization_level': 1,          # Balance speed vs gate count
    'initial_layout': [55,65,66,67,68], # Fixed qubit mapping
    'seed_transpiler': 42              # Reproducibility
}
```

### Why optimization_level=1?

- **Level 0**: No optimization (may miss trivial simplifications)
- **Level 1**: Light optimization (our choice - preserves structure)
- **Level 2-3**: Aggressive optimization (may collapse depth variations)

## 4. Measurement Protocol

### Shot Budget

**Per circuit**: 1000 shots  
**Total circuits**: 14 (2 qubit counts × 7 depths)  
**Total shots**: 14,000

**Statistical uncertainty**: 
$$\sigma_F = \sqrt{\frac{F(1-F)}{N}} \approx \sqrt{\frac{0.9 \times 0.1}{1000}} \approx 0.9\%$$

For F ≈ 0.9, 1000 shots gives ~1% error bars.

### Runtime Estimate

- Transpilation: ~5s per circuit
- Queue time: Variable (0-30 minutes)
- Execution time: ~30s per circuit
- **Total experiment time**: ~1-2 hours

## 5. Metric Calculation

### GHZ Fidelity

Measures overlap with ideal GHZ state:

```python
F = (P(|000...0⟩) + P(|111...1⟩)) / N_shots
```

**Interpretation**:
- F = 1.0: Perfect GHZ state
- F = 0.5: Completely mixed (random)
- F > 0.9: High-quality entanglement

### Parity Expectation

Measures Z⊗Z⊗...⊗Z observable:

```python
parity_sum = 0
for bitstring, count in counts.items():
    num_ones = bitstring.count('1')
    parity = 1 if (num_ones % 2 == 0) else -1
    parity_sum += parity * count

parity_expectation = parity_sum / shots
```

**Interpretation**:
- ⟨Z⊗n⟩ = +1: All-even or all-odd parity (good)
- ⟨Z⊗n⟩ = 0: Mixed parity (depolarization)
- ⟨Z⊗n⟩ = -1: Odd-even imbalance

### Heavy Output Frequency (HOG)

Quantum volume metric:

```python
probabilities = {bitstring: count/shots for bitstring, count in counts.items()}
median_prob = np.median(list(probabilities.values()))

HOG = sum(count for bitstring, count in counts.items() 
          if probabilities[bitstring] > median_prob) / shots
```

**Interpretation**:
- HOG > 2/3: Quantum advantage threshold
- HOG ≈ 0.5: Classical-like distribution

## 6. Data Collection

### JSON Structure

```json
{
  "metadata": {
    "timestamp": "2026-01-31T22:21:00",
    "n_qubits": 4,
    "depths": [2, 4, 6, 8, 10, 15, 20],
    "shots": 1000,
    "backends": ["ibm_torino"],
    "qubit_mapping": [55, 65, 66, 67, 68]
  },
  "data": {
    "ibm_torino": {
      "depth_2": {
        "job_id": "d5vd9bt...",
        "circuit_depth_logical": 2,
        "circuit_depth_transpiled": 18,
        "gate_count": 38,
        "cz_count": 6,
        "counts": {"0000": 524, "1111": 392, ...},
        "metrics": {
          "ghz_fidelity": 0.916,
          "parity_expectation": 0.854,
          "heavy_output_frequency": 0.978
        }
      }
    }
  }
}
```

## 7. Error Sources and Mitigation

### Main Error Sources

1. **Gate errors**: ~0.87% per CZ gate
2. **Decoherence**: T1 ≈ 150 μs limits circuit duration
3. **Readout errors**: ~1.2% per qubit measurement
4. **Crosstalk**: Adjacent qubit interactions

### Mitigation Strategies (Future Work)

- **Readout error mitigation**: Calibration matrix correction
- **Zero-noise extrapolation**: Vary pulse amplitudes
- **Dynamical decoupling**: Add idle-time spin echoes
- **Probabilistic error cancellation**: Inverse noise maps

## 8. Reproducibility Checklist

✅ Fixed qubit mapping  
✅ Fixed transpiler seed  
✅ Recorded calibration date  
✅ Saved job IDs  
✅ Documented all parameters  
✅ Open-source code  
✅ Raw data available  

## 9. Validation Tests

### Sanity Checks

1. **Ideal fidelity check**: Depth 1 should give F > 0.85
2. **Monotonicity**: (Generally) F(d) ≥ F(d+1)
3. **Shot noise**: Repeat measurements should vary by ~1%
4. **Transpiler consistency**: Same circuit → same gate count

### Statistical Tests

- **Significance**: Student's t-test for F differences
- **Outliers**: Z-score test (reject |z| > 3)
- **Trends**: Linear regression on decay rate

## 10. Common Issues and Solutions

### Issue: Zero CZ gates in transpiled circuit

**Cause**: Transpiler optimized away all gates  
**Solution**: Add non-commuting rotations (RZ gates)

### Issue: Fidelity too low (<50%)

**Causes**:
- Wrong qubit mapping (disconnected qubits)
- Incorrect gate set (CX vs CZ)
- Calibration drift

**Solution**: Re-run qubit selection, verify native gates

### Issue: Results not reproducible

**Causes**:
- Calibration changed (qubits recalibrated)
- Different time-of-day (thermal drift)
- Queue priority (different execution order)

**Solution**: Record timestamp, re-run within 24 hours

## References

- IBM Quantum documentation: https://docs.quantum.ibm.com
- Qiskit textbook: https://qiskit.org/textbook
- Heavy-hexagon topology: arXiv:2009.00140