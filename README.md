# Noise-Adaptive Circuit Depth Threshold Probe

Empirical analysis of circuit-depth fidelity thresholds on IBM Quantum
Heron-class hardware using GHZ-state preparation circuits.

## Records

- Paper: https://doi.org/10.5281/zenodo.20162808
- Software: https://doi.org/10.5281/zenodo.20172113
- Dataset: https://doi.org/10.5281/zenodo.20172472

## Summary

This project investigates logical-depth-dependent fidelity degradation on IBM
Quantum hardware using 4- and 5-qubit GHZ circuits.

Key findings:

- 4-qubit fidelity plateaus near 88% beyond depth 10
- 5-qubit fidelity continues degrading through depth 20
- Observed fidelity exceeds independent gate-error model predictions

## Repository Structure

- `src/`: core experimental and analysis code
- `scripts/`: runnable experiment and plotting scripts
- `configs/`: experiment configuration files
- `results/`: saved results and derived figures
- `paper/`: LaTeX paper source and publication figures
- `docs/`: supporting documentation
- `tests/`: test suite

## Hardware

- IBM Quantum Heron-class hardware
- Backend used in the saved dataset: `ibm_torino`

## Requirements

- Python 3.9+
- Qiskit
- NumPy
- Matplotlib

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Reproducing Results

Run the hardware experiment:

```bash
python scripts/run_experiment.py
```

Analyze the saved JSON dataset:

```bash
python scripts/analyze_results.py --file results/depth_threshold_results.json
```

Regenerate the publication-style figures:

```bash
python scripts/analyze_all_data.py
```

## Citation

If you use this work, cite the related Zenodo records listed above for the
paper, software, and dataset.

## License

MIT License. See [LICENCE](LICENCE).
