#!/bin/bash
# Automated depth sweep experiment runner
# Runs multiple configurations and saves with unique filenames

set -e  # Exit on error

echo "=========================================="
echo "DEPTH THRESHOLD SWEEP - BATCH RUNNER"
echo "=========================================="

# Configuration
BACKEND="ibm_torino"
SHOTS=1000
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create results directory if it doesn't exist
mkdir -p results/sweeps

echo ""
echo "Configuration:"
echo "  Backend: $BACKEND"
echo "  Shots: $SHOTS"
echo "  Timestamp: $TIMESTAMP"
echo ""

# Sweep 1: 4 qubits, standard depths
echo "=== Sweep 1: 4 qubits, depths 2-6 ==="
python scripts/run_experiment.py \
    --backend $BACKEND \
    --qubits 4 \
    --depths 2 4 6 \
    --shots $SHOTS \
    --output results/sweeps/4q_standard_${TIMESTAMP}

# Sweep 2: 4 qubits, extended depths
echo ""
echo "=== Sweep 2: 4 qubits, extended depths ==="
python scripts/run_experiment.py \
    --backend $BACKEND \
    --qubits 4 \
    --depths 2 4 6 8 10 15 20 \
    --shots $SHOTS \
    --output results/sweeps/4q_extended_${TIMESTAMP}

# Sweep 3: 5 qubits, standard depths
echo ""
echo "=== Sweep 3: 5 qubits, depths 2-6 ==="
python scripts/run_experiment.py \
    --backend $BACKEND \
    --qubits 5 \
    --depths 2 4 6 \
    --shots $SHOTS \
    --output results/sweeps/5q_standard_${TIMESTAMP}

# Sweep 4: 5 qubits, extended depths
echo ""
echo "=== Sweep 4: 5 qubits, extended depths ==="
python scripts/run_experiment.py \
    --backend $BACKEND \
    --qubits 5 \
    --depths 2 4 6 8 10 15 20 \
    --shots $SHOTS \
    --output results/sweeps/5q_extended_${TIMESTAMP}

echo ""
echo "=========================================="
echo "ALL SWEEPS COMPLETE"
echo "=========================================="
echo ""
echo "Results saved in: results/sweeps/"
echo ""
echo "To analyze all results:"
echo "  python scripts/analyze_results.py --directory results/sweeps"
echo ""