#!/usr/bin/env python3
"""Find optimal qubit chains for the experiment."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qiskit_ibm_runtime import QiskitRuntimeService
import networkx as nx

SERVICE_CONFIG = {
    'channel': 'ibm_quantum_platform',
    'instance': 'ADQNN-GAGE'
}

def find_best_qubit_chains(backend, chain_length=4, top_n=5):
    """
    Find the best connected qubit chains on a backend.
    
    Args:
        backend: IBM Backend
        chain_length: Length of chain needed
        top_n: Number of best chains to return
    
    Returns:
        List of qubit chains sorted by quality
    """
    # Get backend properties
    coupling_map = backend.coupling_map
    props = backend.properties()
    
    # Build graph of qubit connectivity
    G = nx.Graph()
    G.add_edges_from(coupling_map)
    
    # Find all simple paths of required length
    all_chains = []
    for start in range(backend.num_qubits):
        for target in range(backend.num_qubits):
            if start != target:
                try:
                    paths = nx.all_simple_paths(G, start, target, cutoff=chain_length-1)
                    for path in paths:
                        if len(path) == chain_length:
                            all_chains.append(path)
                except nx.NetworkXNoPath:
                    continue
    
    # Score each chain by gate errors
    chain_scores = []
    for chain in all_chains:
        score = 0
        count = 0
        
        # Score single-qubit gates
        for qubit in chain:
            try:
                sx_error = props.gate_error('sx', qubit)
                score += sx_error
                count += 1
            except:
                score += 0.01  # Default if not available
                count += 1
        
        # Score two-qubit gates
        for i in range(len(chain) - 1):
            try:
                cx_error = props.gate_error('ecr', [chain[i], chain[i+1]])
                score += cx_error
                count += 1
            except:
                try:
                    cx_error = props.gate_error('cx', [chain[i], chain[i+1]])
                    score += cx_error
                    count += 1
                except:
                    score += 0.02  # Default if not available
                    count += 1
        
        avg_score = score / count if count > 0 else 1.0
        chain_scores.append((chain, avg_score, score))
    
    # Sort by average error (lower is better)
    chain_scores.sort(key=lambda x: x[1])
    
    return chain_scores[:top_n]


def main():
    print("Finding optimal qubit chains on IBM Quantum backends...\n")
    
    service = QiskitRuntimeService(**SERVICE_CONFIG)
    
    # Check ibm_torino
    backend_name = 'ibm_torino'
    backend = service.backend(backend_name)
    
    print(f"Backend: {backend_name}")
    print(f"Qubits: {backend.num_qubits}")
    print(f"Basis gates: {backend.operation_names}")
    print()
    
    print("Top 5 qubit chains for 4-qubit experiments:")
    print("-" * 60)
    
    best_chains = find_best_qubit_chains(backend, chain_length=4, top_n=5)
    
    for i, (chain, avg_error, total_error) in enumerate(best_chains, 1):
        print(f"{i}. Qubits {chain}")
        print(f"   Avg error: {avg_error:.4f}, Total error: {total_error:.4f}")
        print()
    
    if best_chains:
        print("=" * 60)
        print(f"RECOMMENDED: Use qubit chain {best_chains[0][0]}")
        print("=" * 60)
        print(f"\nAdd this to your scripts/run_experiment.py:")
        print(f"QUBIT_MAPPING = {best_chains[0][0]}")


if __name__ == "__main__":
    main()