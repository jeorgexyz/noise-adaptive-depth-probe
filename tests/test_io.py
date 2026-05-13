"""
Unit tests for I/O utilities module.
"""
import pytest
import json
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from io_utils import save_results, load_results


class TestResultsSaving:
    """Test saving experimental results."""
    
    def test_save_basic_results(self):
        """Test saving basic results dictionary."""
        results = {
            'metadata': {
                'timestamp': '2026-01-31T22:00:00',
                'n_qubits': 4,
                'depths': [2, 4, 6]
            },
            'data': {
                'ibm_torino': {
                    'depth_2': {
                        'fidelity': 0.92,
                        'counts': {'0000': 500, '1111': 500}
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            save_results(results, filepath)
            
            # Verify file exists
            assert Path(filepath).exists()
            
            # Verify content
            with open(filepath, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['metadata']['n_qubits'] == 4
            assert loaded['data']['ibm_torino']['depth_2']['fidelity'] == 0.92
        
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_save_creates_directory(self):
        """Test that save creates directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'subdir' / 'results.json'
            
            results = {'test': 'data'}
            save_results(results, str(filepath))
            
            assert filepath.exists()
    
    def test_save_overwrites_existing(self):
        """Test that save overwrites existing files."""
        results1 = {'version': 1}
        results2 = {'version': 2}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            save_results(results1, filepath)
            save_results(results2, filepath)
            
            with open(filepath, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['version'] == 2
        
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestResultsLoading:
    """Test loading experimental results."""
    
    def test_load_basic_results(self):
        """Test loading basic results."""
        results = {
            'metadata': {'n_qubits': 4},
            'data': {'test': 'value'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(results, f)
            filepath = f.name
        
        try:
            loaded = load_results(filepath)
            assert loaded['metadata']['n_qubits'] == 4
            assert loaded['data']['test'] == 'value'
        
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_load_nonexistent_file(self):
        """Test loading file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_results('/nonexistent/path/file.json')
    
    def test_load_invalid_json(self):
        """Test loading file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("This is not valid JSON {{{")
            filepath = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_results(filepath)
        
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestRoundTrip:
    """Test save-load round trip."""
    
    def test_roundtrip_preserves_data(self):
        """Test that save-load preserves all data."""
        original = {
            'metadata': {
                'timestamp': '2026-01-31T22:00:00',
                'n_qubits': 5,
                'depths': [2, 4, 6, 8, 10],
                'shots': 1000,
                'qubit_mapping': [55, 65, 66, 67, 68]
            },
            'data': {
                'ibm_torino': {
                    'depth_2': {
                        'job_id': 'test123',
                        'fidelity': 0.894,
                        'counts': {'00000': 450, '11111': 450, '00001': 50, '10000': 50}
                    },
                    'depth_4': {
                        'job_id': 'test456',
                        'fidelity': 0.905,
                        'counts': {'00000': 500, '11111': 400, '00001': 100}
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            save_results(original, filepath)
            loaded = load_results(filepath)
            
            # Check metadata
            assert loaded['metadata']['n_qubits'] == original['metadata']['n_qubits']
            assert loaded['metadata']['depths'] == original['metadata']['depths']
            assert loaded['metadata']['qubit_mapping'] == original['metadata']['qubit_mapping']
            
            # Check data
            assert loaded['data']['ibm_torino']['depth_2']['fidelity'] == \
                   original['data']['ibm_torino']['depth_2']['fidelity']
            assert loaded['data']['ibm_torino']['depth_2']['counts'] == \
                   original['data']['ibm_torino']['depth_2']['counts']
        
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_roundtrip_preserves_types(self):
        """Test that data types are preserved."""
        original = {
            'int_val': 42,
            'float_val': 3.14159,
            'str_val': 'test',
            'list_val': [1, 2, 3],
            'dict_val': {'a': 1, 'b': 2},
            'bool_val': True,
            'null_val': None
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            save_results(original, filepath)
            loaded = load_results(filepath)
            
            assert isinstance(loaded['int_val'], int)
            assert isinstance(loaded['float_val'], float)
            assert isinstance(loaded['str_val'], str)
            assert isinstance(loaded['list_val'], list)
            assert isinstance(loaded['dict_val'], dict)
            assert isinstance(loaded['bool_val'], bool)
            assert loaded['null_val'] is None
        
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestDataIntegrity:
    """Test data integrity and validation."""
    
    def test_large_counts_dictionary(self):
        """Test handling of large counts dictionaries."""
        # Simulate 10-qubit system (1024 possible outcomes)
        counts = {f'{i:010b}': i for i in range(1024)}
        
        results = {
            'metadata': {'n_qubits': 10},
            'data': {'counts': counts}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            save_results(results, filepath)
            loaded = load_results(filepath)
            
            assert len(loaded['data']['counts']) == 1024
            assert loaded['data']['counts']['0000000000'] == 0
            assert loaded['data']['counts']['1111111111'] == 1023
        
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_nested_structure_preservation(self):
        """Test that deeply nested structures are preserved."""
        results = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'value': 42
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            save_results(results, filepath)
            loaded = load_results(filepath)
            
            assert loaded['level1']['level2']['level3']['level4']['value'] == 42
        
        finally:
            Path(filepath).unlink(missing_ok=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])