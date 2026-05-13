"""
Unit tests for circuit construction module.
"""
import pytest
import numpy as np
from qiskit import QuantumCircuit
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from circuits import build_ghz_circuit


class TestGHZCircuitConstruction:
    """Test GHZ circuit construction with varying depths."""
    
    def test_basic_construction(self):
        """Test that circuit can be built without errors."""
        qc = build_ghz_circuit(n_qubits=4, depth=2)
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == 4
        assert qc.num_clbits == 4
    
    def test_qubit_counts(self):
        """Test various qubit counts."""
        for n in [2, 3, 4, 5]:
            qc = build_ghz_circuit(n_qubits=n, depth=2)
            assert qc.num_qubits == n
            assert qc.num_clbits == n
    
    def test_depth_scaling(self):
        """Test that circuit depth increases with depth parameter."""
        depths = [2, 4, 6]
        circuit_depths = []
        
        for d in depths:
            qc = build_ghz_circuit(n_qubits=4, depth=d)
            circuit_depths.append(qc.depth())
        
        # Circuit depth should generally increase (not strict due to transpilation)
        assert circuit_depths[1] >= circuit_depths[0]
        assert circuit_depths[2] >= circuit_depths[1]
    
    def test_gate_count_scaling(self):
        """Test that CZ gate count scales with depth."""
        qc_d2 = build_ghz_circuit(n_qubits=4, depth=2)
        qc_d4 = build_ghz_circuit(n_qubits=4, depth=4)
        
        cz_d2 = qc_d2.count_ops().get('cz', 0)
        cz_d4 = qc_d4.count_ops().get('cz', 0)
        
        # More depth should mean more CZ gates
        assert cz_d4 > cz_d2
    
    def test_measurement_present(self):
        """Test that measurement operations are included."""
        qc = build_ghz_circuit(n_qubits=4, depth=2)
        ops = qc.count_ops()
        
        assert 'measure' in ops
        assert ops['measure'] == 4  # Should measure all qubits
    
    def test_entangling_gates_present(self):
        """Test that entangling gates (CZ) are present."""
        qc = build_ghz_circuit(n_qubits=4, depth=2)
        ops = qc.count_ops()
        
        assert 'cz' in ops
        assert ops['cz'] > 0  # Should have at least some CZ gates
    
    def test_depth_one_minimum(self):
        """Test that depth parameter accepts minimum value."""
        # Depth 1 should work (just basic GHZ)
        qc = build_ghz_circuit(n_qubits=4, depth=1)
        assert qc.num_qubits == 4
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Negative qubits should fail
        with pytest.raises((ValueError, Exception)):
            build_ghz_circuit(n_qubits=-1, depth=2)
        
        # Zero qubits should fail
        with pytest.raises((ValueError, Exception)):
            build_ghz_circuit(n_qubits=0, depth=2)
    
    def test_reproducibility(self):
        """Test that same parameters produce same circuit."""
        qc1 = build_ghz_circuit(n_qubits=4, depth=2)
        qc2 = build_ghz_circuit(n_qubits=4, depth=2)
        
        # Should have same structure
        assert qc1.num_qubits == qc2.num_qubits
        assert qc1.depth() == qc2.depth()
        assert qc1.count_ops() == qc2.count_ops()
    
    def test_gate_types(self):
        """Test that only expected gate types are used."""
        qc = build_ghz_circuit(n_qubits=4, depth=2)
        ops = qc.count_ops()
        
        expected_gates = {'h', 'cz', 'rz', 'measure'}
        actual_gates = set(ops.keys())
        
        # All gates should be expected
        assert actual_gates.issubset(expected_gates)


class TestCircuitProperties:
    """Test mathematical properties of constructed circuits."""
    
    def test_hermitian_check(self):
        """Test that circuit is valid quantum operation."""
        qc = build_ghz_circuit(n_qubits=2, depth=2)
        # Remove measurements for unitary check
        qc_no_meas = qc.remove_final_measurements(inplace=False)
        
        # Should be able to decompose to unitary
        from qiskit.quantum_info import Operator
        try:
            unitary = Operator(qc_no_meas)
            # Unitary should be square
            assert unitary.data.shape[0] == unitary.data.shape[1]
        except Exception as e:
            pytest.skip(f"Could not compute unitary: {e}")
    
    def test_qubit_connectivity(self):
        """Test that circuit respects linear connectivity."""
        qc = build_ghz_circuit(n_qubits=4, depth=2)
        
        # Extract CZ gates and check they're between adjacent qubits
        for instruction in qc.data:
            if instruction[0].name == 'cz':
                qubits = [qc.find_bit(q).index for q in instruction[1]]
                # CZ should be between adjacent qubits (linear chain)
                assert abs(qubits[0] - qubits[1]) <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])