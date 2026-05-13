#!/usr/bin/env python3
"""Main entry point for depth threshold experiment."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime
from qiskit_ibm_runtime import QiskitRuntimeService

# Import from src using absolute imports after adding to path
from src.experiment import run_depth_threshold_experiment
from src.plotting import plot_results
from src.io_utils import save_results

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVICE_CONFIG = {
    'channel': 'ibm_quantum_platform',  # Correct channel name
    'instance': 'ADQNN-GAGE'
}

BACKENDS = ['ibm_torino']
DEPTHS = [2, 4, 6, 8, 10, 15, 20]
N_QUBITS = 5
SHOTS = 1000
OPTIMIZATION_LEVEL = 1


def main():
    """Run the depth threshold experiment."""
    print("=" * 70)
    print("NOISE-ADAPTIVE CIRCUIT DEPTH THRESHOLD PROBE")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Backends: {BACKENDS}")
    print(f"  Depths: {DEPTHS}")
    print(f"  Qubits: {N_QUBITS}")
    print(f"  Shots per circuit: {SHOTS}")
    print(f"  Estimated total runtime: ~{len(BACKENDS) * len(DEPTHS) * 30}s")
    print("=" * 70)
    
    # Initialize IBM Quantum service
    print("\nConnecting to IBM Quantum...")
    service = QiskitRuntimeService(**SERVICE_CONFIG)

    # Select good qubit chain for ibm_torino
    QUBIT_MAPPING = [55, 65, 66, 67, 68]  # Example - check topology
    
    # Run experiment
    results = run_depth_threshold_experiment(
        service=service,
        backends=BACKENDS,
        depths=DEPTHS,
        n_qubits=N_QUBITS,
        shots=SHOTS,
        optimization_level=OPTIMIZATION_LEVEL,
        qubit_mapping=QUBIT_MAPPING
    )
    
    # Create results directory if it doesn't exist
    results_dir = project_root / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Save results
    results_file = results_dir / 'depth_threshold_results.json'
    save_results(results, str(results_file))
    
    # Plot results
    plot_file = results_dir / 'depth_threshold_analysis.png'
    plot_results(results, str(plot_file))
    
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print("\nKey Findings:")
    for backend_name, backend_data in results['data'].items():
        print(f"\n{backend_name}:")
        for depth_key in sorted(backend_data.keys(), 
                                key=lambda x: int(x.split('_')[1])):
            depth_val = int(depth_key.split('_')[1])
            fid = backend_data[depth_key]['metrics']['ghz_fidelity']
            print(f"  Depth {depth_val}: Fidelity = {fid:.4f}")
    
    return results


if __name__ == "__main__":
    results = main()