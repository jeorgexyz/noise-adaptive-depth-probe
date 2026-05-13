"""File I/O utilities."""
import json


def save_results(results, filename='depth_threshold_results.json'):
    """Save experiment results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to '{filename}'")


def load_results(filename):
    """Load experiment results from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)