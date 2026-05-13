# Results Directory

This directory contains experimental outputs from the noise-adaptive depth
threshold probe on IBM Quantum hardware.

## Files

| File | Description |
|------|-------------|
| `depth_threshold_results.json` | Raw measurement counts and computed metrics for the 5-qubit depth sweep on `ibm_torino` |
| `depth_threshold_analysis.png` | Analysis plot generated directly from `depth_threshold_results.json` |
| `gate_count_analysis.png` | Summary plot comparing fidelity vs. CZ gate count and gate-count scaling |
| `publication_figure.png` | Publication figure comparing 4-qubit and 5-qubit fidelity decay |

## Important Scope Note

- `depth_threshold_results.json` contains the raw saved dataset for the **5-qubit**
  run only.
- `publication_figure.png` and `gate_count_analysis.png` include **4-qubit and
  5-qubit summary values** assembled in
  [scripts/analyze_all_data.py](../scripts/analyze_all_data.py).
- As a result, not every figure in this directory is generated solely from
  `depth_threshold_results.json`.

## JSON Data Format

`depth_threshold_results.json` follows this schema:

```json
{
  "metadata": {
    "timestamp": "<ISO 8601 datetime of experiment run>",
    "n_qubits": <int, number of qubits used>,
    "depths": [<int>, ...],
    "shots": <int, measurement shots per circuit>,
    "backends": ["<backend_name>", ...],
    "qubit_mapping": [<int>, ...]
  },
  "data": {
    "<backend_name>": {
      "depth_<N>": {
        "job_id": "<IBM Quantum job ID string>",
        "circuit_depth_logical": <int, logical depth parameter passed to circuit builder>,
        "circuit_depth_transpiled": <int, actual depth after Qiskit transpilation>,
        "gate_count": <int, total gate count in transpiled circuit>,
        "cx_count": <int, number of CX two-qubit gates>,
        "ecr_count": <int, number of ECR two-qubit gates>,
        "cz_count": <int, number of CZ two-qubit gates>,
        "two_qubit_gates": <int, sum of cx_count + ecr_count + cz_count>,
        "counts": {
          "<bitstring>": <int, number of times this bitstring was observed>
        },
        "metrics": {
          "ghz_fidelity": <float in [0,1], P(|00...0>) + P(|11...1>)>,
          "parity_expectation": <float in [-1,1], computational-basis Z-parity average>,
          "heavy_output_frequency": <float in [0,1], fraction of shots above median observed probability>
        }
      }
    }
  }
}
```

## Field Notes

- **`bitstring`**: A binary string of length `n_qubits`. Qiskit orders bits
  right-to-left, so qubit 0 is the rightmost character.
- **`ghz_fidelity`**: Approximate GHZ-state preparation fidelity, defined here as
  the fraction of shots in the two target states `|00...0>` and `|11...1>`.
- **`parity_expectation`**: Average value of the computational-basis parity
  statistic `(-1)^(number of measured 1s)`. This is a population-based parity
  summary, not a full coherence witness. For odd-qubit GHZ populations, the ideal
  value is not generally `+1`.
- **`heavy_output_frequency`**: Heavy-output-generation style metric computed from
  the observed output distribution.
- **`circuit_depth_logical`** vs **`circuit_depth_transpiled`**: Logical depth is
  the parameter passed to `build_ghz_circuit()`. Transpiled depth is the compiled
  depth after decomposition to the backend basis gates.

## Experimental Conditions for `depth_threshold_results.json`

- **Hardware**: IBM Torino (Heron r2, 133 qubits)
- **Backend name**: `ibm_torino`
- **Run type**: 5-qubit GHZ depth sweep
- **Qubit chain**: `[55, 65, 66, 67, 68]`
- **Timestamp**: `2026-01-31T22:28:54.585936`
- **Depths tested**: `2, 4, 6, 8, 10, 15, 20`
- **Shots per circuit**: `1000`
- **Transpilation**: `optimization_level=1`, `seed_transpiler=42`

## Reproducing Results

To regenerate the analysis plot from the saved JSON:

```bash
python scripts/analyze_results.py --file results/depth_threshold_results.json
```

To regenerate the publication-style comparison figures:

```bash
python scripts/analyze_all_data.py
```

To re-run the experiment from hardware credentials and configuration:

```bash
python scripts/run_experiment.py
```
