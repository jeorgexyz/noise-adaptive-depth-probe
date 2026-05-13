# Results Directory

This directory contains all experimental outputs from the noise-adaptive depth threshold probe experiments run on IBM Quantum hardware.

---

## Files

| File | Description |
|------|-------------|
| `depth_threshold_results.json` | Raw measurement counts and computed metrics for all depth/qubit configurations |
| `depth_threshold_analysis.png` | 3-panel plot: GHZ fidelity, parity expectation, and HOG vs circuit depth |
| `gate_count_analysis.png` | 2-panel plot: fidelity vs CZ gate count and gate count scaling with depth |
| `publication_figure.png` | Single publication-quality comparison figure (4q vs 5q fidelity decay) |

---

## JSON Data Format

`depth_threshold_results.json` follows this schema:

```json
{
  "metadata": {
    "timestamp":     "<ISO 8601 datetime of experiment run>",
    "n_qubits":      <int — number of qubits used>,
    "depths":        [<int>, ...],
    "shots":         <int — measurement shots per circuit>,
    "backends":      ["<backend_name>", ...],
    "qubit_mapping": [<int>, ...]
  },
  "data": {
    "<backend_name>": {
      "depth_<N>": {
        "job_id":                  "<IBM Quantum job ID string>",
        "circuit_depth_logical":   <int — logical depth parameter passed to circuit builder>,
        "circuit_depth_transpiled":<int — actual depth after Qiskit transpilation>,
        "gate_count":              <int — total gate count in transpiled circuit>,
        "cx_count":                <int — number of CX (CNOT) two-qubit gates>,
        "ecr_count":               <int — number of ECR two-qubit gates>,
        "cz_count":                <int — number of CZ two-qubit gates>,
        "two_qubit_gates":         <int — sum of cx_count + ecr_count + cz_count>,
        "counts": {
          "<bitstring>": <int — number of times this bitstring was observed>
        },
        "metrics": {
          "ghz_fidelity":           <float in [0,1] — P(|00...0>) + P(|11...1>)>,
          "parity_expectation":     <float in [-1,1] — <Z_0 Z_1 ... Z_n>>,
          "heavy_output_frequency": <float in [0,1] — fraction of shots above median probability>
        }
      }
    }
  }
}
```

### Field Notes

- **`bitstring`**: A binary string of length `n_qubits`. Qiskit orders bits right-to-left (qubit 0 is the rightmost character). E.g., `"11111"` = all qubits measured as 1.
- **`ghz_fidelity`**: Approximation of GHZ state preparation fidelity. Defined as the fraction of shots in the two target states (`|00...0>` or `|11...1>`). Ideal noiseless value = 1.0.
- **`parity_expectation`**: Expectation value of the n-qubit Z-parity operator. For a perfect GHZ state this equals +1; noise drives it toward 0.
- **`heavy_output_frequency`**: HOG metric from quantum volume definition. Values significantly above 0.5 indicate the circuit is producing non-trivial quantum output.
- **`circuit_depth_logical`** vs **`circuit_depth_transpiled`**: Logical depth is the parameter passed to `build_ghz_circuit()`. Transpiled depth is larger due to native gate decomposition on the Heron r2 architecture (CZ, SX, RZ basis set).

---

## Experimental Conditions

- **Hardware**: IBM Torino (Heron r2, 133 qubits)
- **Qubit chain**: [55, 65, 66, 67, 68]
- **Calibration date**: 2026-01-31
- **Shots per circuit**: 1000
- **Transpilation**: `optimization_level=1`, `seed_transpiler=42`

---

## Reproducing Results

To regenerate plots from the saved JSON:

```bash
python scripts/analyze_results.py results/depth_threshold_results.json
python scripts/analyze_all_data.py
```

To re-run the experiment (requires IBM Quantum credentials):

```bash
python scripts/run_experiment.py
```
