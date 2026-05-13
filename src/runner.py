"""IBM Quantum backend interface."""
from qiskit_ibm_runtime import SamplerV2 as Sampler


def run_on_backend(backend, circuit, shots):
    """
    Run a circuit on IBM Quantum backend.
    
    Args:
        backend: IBMBackend instance
        circuit: Transpiled QuantumCircuit
        shots: Number of shots
    
    Returns:
        tuple: (counts_dict, job_id)
    """
    sampler = Sampler(mode=backend)
    job = sampler.run([circuit], shots=shots)
    
    print(f"Job submitted: {job.job_id()}")
    print("Waiting for results...")
    
    result = job.result()
    pub_result = result[0]
    
    # Get counts - handle different attribute names
    data = pub_result.data
    
    # The classical register name varies - try to find it
    if hasattr(data, 'c'):
        # Most common: register named 'c'
        counts_dict = data.c.get_counts()
    elif hasattr(data, 'meas'):
        # Sometimes named 'meas'
        counts_dict = data.meas.get_counts()
    else:
        # Get first available register from __dict__
        reg_name = list(data.__dict__.keys())[0]
        counts_dict = data.__getattribute__(reg_name).get_counts()
    
    return counts_dict, job.job_id()