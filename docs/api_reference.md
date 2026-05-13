# API Reference

Full documentation for all public functions in the `src/` package.

---

## `src.circuits`

### `build_ghz_circuit(n_qubits, depth)`

Build a GHZ state preparation circuit with depth-parameterized noise accumulation layers.

Uses a Trotter-style approach: the base GHZ state is created first, then `depth - 1`
additional entangling layers are appended. Each added layer applies `RZ(θ)` rotations
with varying angles before and after a CZ chain to prevent the transpiler from
optimizing the layers away.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `n_qubits` | `int` | Number of qubits. Must be ≥ 2. |
| `depth` | `int` | Number of entangling layers. `depth=1` produces a minimal GHZ circuit; each increment adds one CZ chain + rotation pair. |

**Returns** `qiskit.QuantumCircuit` — a measured circuit with `n_qubits` qubits and
`n_qubits` classical bits.

**Gate scaling**

| Quantity | Formula |
|----------|---------|
| CZ gates | `(n_qubits - 1) * depth * 2` (approx) |
| Transpiled depth | `6 * depth + const` (ibm\_torino, Heron r2) |

**Example**

```python
from src.circuits import build_ghz_circuit
qc = build_ghz_circuit(n_qubits=4, depth=6)
print(qc.depth())          # logical depth before transpilation
print(qc.count_ops())      # gate summary
```

---

### `build_ghz_circuit_simple(n_qubits)`

Build a minimal GHZ state preparation circuit with no depth extension.

Produces the standard $|00\cdots0\rangle + |11\cdots1\rangle$ state using an H gate
on qubit 0 followed by an H–CZ–H sequence for each subsequent qubit.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `n_qubits` | `int` | Number of qubits. Must be ≥ 2. |

**Returns** `qiskit.QuantumCircuit`

**Example**

```python
from src.circuits import build_ghz_circuit_simple
qc = build_ghz_circuit_simple(5)
```

---

## `src.metrics`

### `calculate_ghz_fidelity(counts, n_qubits, shots)`

Compute an approximation of GHZ state preparation fidelity from measurement counts.

Fidelity is defined as the fraction of shots in the two target bitstrings
(`|00...0>` and `|11...1>`):

```
F = (count("00...0") + count("11...1")) / shots
```

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `counts` | `dict[str, int]` | Bitstring → count mapping from `get_counts()`. |
| `n_qubits` | `int` | Number of qubits (determines target bitstring length). |
| `shots` | `int` | Total number of measurement shots. |

**Returns** `float` in `[0, 1]`. Ideal noiseless GHZ = 1.0.

**Example**

```python
from src.metrics import calculate_ghz_fidelity
counts = {"00000": 480, "11111": 490, "10000": 30}
fidelity = calculate_ghz_fidelity(counts, n_qubits=5, shots=1000)
# fidelity = 0.97
```

---

### `calculate_parity_oscillation(counts, n_qubits, shots)`

Compute the n-qubit Z-parity expectation value $\langle Z_0 Z_1 \cdots Z_n \rangle$.

For each bitstring, parity is `+1` if the number of `1` bits is even, `-1` if odd.
The return value is the shot-weighted average.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `counts` | `dict[str, int]` | Bitstring → count mapping. |
| `n_qubits` | `int` | Number of qubits (unused in calculation, kept for API consistency). |
| `shots` | `int` | Total measurement shots. |

**Returns** `float` in `[-1, 1]`. A perfect GHZ state returns +1; noise drives the
value toward 0.

---

### `calculate_heavy_output_frequency(counts, shots)`

Compute the Heavy Output Generation (HOG) metric.

Probabilities are computed per bitstring; the median probability is used as a
threshold. HOG is the fraction of total shots whose bitstring probability exceeds
the median.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `counts` | `dict[str, int]` | Bitstring → count mapping. |
| `shots` | `int` | Total measurement shots. |

**Returns** `float` in `[0, 1]`. Values significantly above 0.5 indicate
non-trivial quantum output. Classical random circuits produce ≈ 0.5.

---

## `src.experiment`

### `run_depth_threshold_experiment(service, backends, depths, n_qubits=4, shots=1000, optimization_level=1, qubit_mapping=None)`

Main experiment orchestrator. Iterates over all (backend, depth) pairs, builds and
transpiles circuits, submits jobs, collects counts, and computes all three metrics.

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `service` | `QiskitRuntimeService` | — | Authenticated IBM Quantum service instance. |
| `backends` | `list[str]` | — | List of backend names, e.g. `["ibm_torino"]`. |
| `depths` | `list[int]` | — | Logical depths to sweep, e.g. `[2, 4, 6, 8, 10, 15, 20]`. |
| `n_qubits` | `int` | `4` | Number of qubits. |
| `shots` | `int` | `1000` | Shots per circuit. |
| `optimization_level` | `int` | `1` | Qiskit transpiler optimization level (0–3). |
| `qubit_mapping` | `list[int] \| None` | `None` | Physical qubit indices for `initial_layout`. If `None`, Qiskit chooses automatically. |

**Returns** `dict` — nested results dictionary. Top-level keys: `"metadata"` and
`"data"`. See `results/README.md` for the full JSON schema.

**Example**

```python
from qiskit_ibm_runtime import QiskitRuntimeService
from src.experiment import run_depth_threshold_experiment

service = QiskitRuntimeService(channel="ibm_quantum_platform", instance="MY-INSTANCE")
results = run_depth_threshold_experiment(
    service=service,
    backends=["ibm_torino"],
    depths=[2, 4, 6, 8, 10],
    n_qubits=4,
    shots=1000,
    qubit_mapping=[55, 65, 66, 67]
)
```

---

## `src.runner`

### `run_on_backend(backend, circuit, shots)`

Submit a pre-transpiled circuit to an IBM Quantum backend and retrieve measurement
counts.

Uses `SamplerV2`. Handles varying classical register names (`c`, `meas`, or
dynamic lookup) to ensure compatibility across Qiskit versions.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `backend` | `IBMBackend` | Authenticated backend object from `service.backend(name)`. |
| `circuit` | `QuantumCircuit` | A **transpiled** circuit (must be transpiled before calling). |
| `shots` | `int` | Number of measurement shots. |

**Returns** `tuple[dict[str, int], str]` — `(counts_dict, job_id)`

---

## `src.plotting`

### `plot_results(results, output_path='depth_threshold_analysis.png')`

Generate a 3-panel publication-quality figure from experiment results and save as PNG.

Panels: (1) GHZ Fidelity vs Depth, (2) Parity Expectation vs Depth,
(3) Heavy Output Frequency vs Depth. Each backend in `results["data"]` is plotted
as a separate series.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `results` | `dict` | Results dict as returned by `run_depth_threshold_experiment`. |
| `output_path` | `str` | File path for the output PNG. Saved at 300 DPI. |

**Returns** `None`. Saves the figure and calls `plt.show()`.

---

## `src.io_utils`

### `save_results(results, filename='depth_threshold_results.json')`

Serialize experiment results to a JSON file with 2-space indentation.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `results` | `dict` | Results dictionary to serialize. |
| `filename` | `str` | Output file path. Parent directory must exist. |

---

### `load_results(filename)`

Load a previously saved results JSON file.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `filename` | `str` | Path to the JSON file. |

**Returns** `dict`
