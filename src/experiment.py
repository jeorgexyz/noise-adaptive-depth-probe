"""Core experiment orchestration."""
from datetime import datetime
from qiskit import transpile

from src.circuits import build_ghz_circuit
from src.metrics import (
    calculate_ghz_fidelity,
    calculate_parity_oscillation,
    calculate_heavy_output_frequency
)
from src.runner import run_on_backend


def run_depth_threshold_experiment(
    service,
    backends,
    depths,
    n_qubits=4,
    shots=1000,
    optimization_level=1,
    qubit_mapping=None  # Add this parameter
):
    """
    Main experiment: Run circuits at multiple depths and analyze noise effects.
    
    Args:
        service: QiskitRuntimeService instance
        backends: List of backend names
        depths: List of circuit depths to test
        n_qubits: Number of qubits
        shots: Shots per circuit
        optimization_level: Transpilation optimization level
        qubit_mapping: Optional list of physical qubit indices to use
    
    Returns:
        dict: Experiment results
    """
    results = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'n_qubits': n_qubits,
            'depths': depths,
            'shots': shots,
            'backends': backends,
            'qubit_mapping': qubit_mapping
        },
        'data': {}
    }
    
    for backend_name in backends:
        print(f"\n{'='*70}")
        print(f"Running on backend: {backend_name}")
        print(f"{'='*70}")
        
        backend = service.backend(backend_name)
        results['data'][backend_name] = {}
        
        for depth in depths:
            print(f"\n--- Depth {depth} ---")
            
            # Build circuit
            circuit = build_ghz_circuit(n_qubits, depth)
            
            # Transpile for backend with optional qubit mapping
            transpile_options = {
                'backend': backend,
                'optimization_level': optimization_level,
                'seed_transpiler': 42
            }
            
            if qubit_mapping:
                transpile_options['initial_layout'] = qubit_mapping
                print(f"Using qubit mapping: {qubit_mapping}")
            
            transpiled = transpile(circuit, **transpile_options)
            
            # Count gates
            gate_count = sum(transpiled.count_ops().values())
            cx_count = transpiled.count_ops().get('cx', 0)
            ecr_count = transpiled.count_ops().get('ecr', 0)
            cz_count = transpiled.count_ops().get('cz', 0)
            two_qubit_gates = cx_count + ecr_count + cz_count
            
            print(f"Original circuit depth: {circuit.depth()}")
            print(f"Transpiled circuit depth: {transpiled.depth()}")
            print(f"Total gates: {gate_count}")
            print(f"2Q gates - CX: {cx_count}, ECR: {ecr_count}, CZ: {cz_count}, Total: {two_qubit_gates}")
            
            # Run on backend
            counts_dict, job_id = run_on_backend(backend, transpiled, shots)
            
            print(f"Retrieved {sum(counts_dict.values())} counts")
            
            # Calculate metrics
            fidelity = calculate_ghz_fidelity(counts_dict, n_qubits, shots)
            parity = calculate_parity_oscillation(counts_dict, n_qubits, shots)
            hog = calculate_heavy_output_frequency(counts_dict, shots)
            
            print(f"\nMetrics:")
            print(f"  GHZ Fidelity: {fidelity:.4f}")
            print(f"  Parity Expectation: {parity:.4f}")
            print(f"  Heavy Output Frequency: {hog:.4f}")
            
            # Store results
            results['data'][backend_name][f'depth_{depth}'] = {
                'job_id': job_id,
                'circuit_depth_logical': depth,
                'circuit_depth_transpiled': transpiled.depth(),
                'gate_count': gate_count,
                'cx_count': cx_count,
                'ecr_count': ecr_count,
                'cz_count': cz_count,
                'two_qubit_gates': two_qubit_gates,
                'counts': counts_dict,
                'metrics': {
                    'ghz_fidelity': fidelity,
                    'parity_expectation': parity,
                    'heavy_output_frequency': hog
                }
            }
    
    return results