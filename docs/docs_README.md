# Noise-Adaptive Circuit Depth Threshold Probe

**Empirical characterization of depth-dependent fidelity decay on IBM Quantum hardware**

## Overview

This project provides the first systematic study of circuit depth thresholds on IBM Quantum's Heron-class processors. We characterize how GHZ state fidelity decays with increasing circuit depth, establishing empirical bounds for adaptive quantum circuit architectures.

## Key Findings

- **4-qubit circuits** plateau at 88% fidelity beyond depth 10
- **5-qubit circuits** show linear decay from 89.4% → 83.7%
- **Recommended max_depth ≤ 10** for >85% fidelity on ibm_torino
- **Device-specific noise ceilings** observed at 83-88% regardless of depth

## Project Structure

```
noise-adaptive-depth-probe/
├── src/                  # Core experimental code
│   ├── circuits.py       # Circuit construction (GHZ with depth parameter)
│   ├── metrics.py        # Fidelity, parity, HOG calculations
│   ├── experiment.py     # Main experiment orchestration
│   ├── runner.py         # IBM Quantum backend interface
│   ├── plotting.py       # Visualization functions
│   └── io_utils.py       # Data save/load utilities
├── scripts/              # Executable scripts
│   ├── run_experiment.py           # Main experiment runner
│   ├── find_good_qubits.py         # Qubit chain optimization
│   ├── analyze_all_data.py         # Comprehensive analysis
│   └── create_comparison_plot.py   # Multi-run visualization
├── configs/              # Configuration files
│   └── default.json      # Default experiment parameters
├── results/              # Experimental outputs
│   ├── *.json            # Raw measurement data
│   └── *.png             # Generated plots
├── paper/                # Research paper
│   ├── main.tex          # LaTeX source
│   ├── figures/          # Publication figures
│   └── references.bib    # Bibliography
├── docs/                 # Documentation
│   ├── README.md         # This file
│   ├── methodology.md    # Detailed methods
│   ├── api_reference.md  # Code documentation
│   └── interpretation.md # Result interpretation guide
└── notebooks/            # Jupyter notebooks for exploration
    ├── paper_figures.ipynb
    └── quicklook.ipynb
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jeorgexyz/noise-adaptive-depth-probe.git
cd noise-adaptive-depth-probe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Experiments

```bash
# Find optimal qubit chains on your target backend
python scripts/find_good_qubits.py

# Run depth threshold experiment
python scripts/run_experiment.py

# Analyze results
python scripts/analyze_all_data.py
```

### Configuration

Edit `configs/default.json` to customize:
- Backend selection
- Qubit mapping
- Depth range
- Shot count

## Hardware Requirements

- IBM Quantum account (free tier supported)
- Access to Heron-class processors (e.g., ibm_torino, ibm_marrakesh)
- Recommended: >1 hour of QPU time for full depth sweep

## Software Requirements

- Python 3.9+
- Qiskit 1.2.4
- qiskit-ibm-runtime 0.15+
- NumPy, Matplotlib

## Citation

If you use this code or results in your research, please cite:

```bibtex
@article{anonymous2026noise,
  title={Empirical Noise-Adaptive Circuit Depth Thresholds for Near-Term Quantum Devices},
  author={Anonymous},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026}
}
```

## License

MIT License - see LICENSE file for details

## Contact

For questions or collaboration inquiries, contact: [your email]

## Related Work

This project provides empirical validation for adaptive quantum circuit architectures, particularly:
- **ADQNN-GAGE**: Adaptive Dynamic Quantum Neural Networks
- Barren plateau mitigation strategies
- Hardware-aware quantum algorithm design

## Acknowledgments

- IBM Quantum for cloud access to Heron processors
- Qiskit development team
- [Any funding sources or collaborators]