# Noise-Adaptive Circuit Depth Threshold Probe

Empirical characterization of depth-dependent fidelity decay on IBM Quantum hardware.

**Paper**: See `paper/main.tex`  
**Documentation**: See `docs/README.md`  
**Quick Start**: Run `python scripts/run_experiment.py`

## Key Results

- 4-qubit circuits plateau at 88% fidelity (depth ≥10)
- 5-qubit circuits decay linearly (0.3%/depth)
- Recommended max_depth ≤ 10 for >85% fidelity

See [docs/README.md](docs/README.md) for full documentation.