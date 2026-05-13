"""Circuit construction for depth threshold experiments."""
import numpy as np
from qiskit import QuantumCircuit


def build_ghz_circuit(n_qubits, depth):
    """
    Build a GHZ circuit with depth-dependent structure that tests noise accumulation.
    
    We use a "Trotter-style" approach where we create the GHZ state, then apply
    layers of operations that can't be optimized away by the transpiler.
    
    Args:
        n_qubits: Number of qubits
        depth: Number of additional entangling layers (1 = minimal, higher = more gates)
    
    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Create clean GHZ state: |000⟩ + |111⟩
    qc.h(0)
    for i in range(n_qubits - 1):
        qc.h(i + 1)
        qc.cz(i, i + 1)
        qc.h(i + 1)
    
    # Add depth by applying entangling layers with varying angles
    # This can't be optimized away because the rotations prevent simplification
    for d in range(depth - 1):
        # Small rotations that accumulate (angle depends on layer)
        angle = 0.1 * (d + 1)  # Different angle per layer
        for i in range(n_qubits):
            qc.rz(angle, i)
        
        # Re-entangle with CZ gates
        for i in range(n_qubits - 1):
            qc.cz(i, i + 1)
        
        # Undo the rotation (but errors accumulate)
        for i in range(n_qubits):
            qc.rz(-angle, i)
    
    # Measure in computational basis
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


def build_ghz_circuit_simple(n_qubits):
    """
    Build a simple GHZ state preparation circuit using CZ gates.
    
    This creates the standard |000...0⟩ + |111...1⟩ state.
    
    Args:
        n_qubits: Number of qubits
    
    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Create GHZ state
    qc.h(0)  # Put first qubit in superposition
    
    # Entangle all qubits using CZ (with H-CZ-H = CNOT pattern)
    for i in range(n_qubits - 1):
        qc.h(i + 1)
        qc.cz(i, i + 1)
        qc.h(i + 1)
    
    # Measure
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc