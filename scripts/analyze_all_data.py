#!/usr/bin/env python3
"""
Load all saved experimental data and create publication-quality plots.
"""
import json
import matplotlib.pyplot as plt
import numpy as np


# All your data from the notepad
ALL_RUNS = """
[First JSON block content...]
"""

def parse_saved_data():
    """Parse all the JSON blocks from your saved data."""
    
    # I'll manually extract the key data since parsing the full text is complex
    # This is based on your terminal outputs and JSON data
    
    runs = {
        '4q_extended': {
            'n_qubits': 4,
            'depths': [2, 4, 6, 8, 10, 15, 20],
            'fidelities': [0.916, 0.928, 0.908, 0.915, 0.879, 0.882, 0.884],
            'label': '4 qubits',
            'marker': 'o',
            'color': '#1f77b4'
        },
        '5q_extended': {
            'n_qubits': 5,
            'depths': [2, 4, 6, 8, 10, 15, 20],
            'fidelities': [0.894, 0.905, 0.879, 0.874, 0.863, 0.851, 0.837],
            'label': '5 qubits',
            'marker': 's',
            'color': '#ff7f0e'
        }
    }
    
    return runs


def create_publication_plot(runs, save_path='results/publication_figure.png'):
    """Create a publication-quality comparison plot."""
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    for run_name, data in runs.items():
        ax.plot(data['depths'], data['fidelities'],
               marker=data['marker'],
               label=data['label'],
               linewidth=3,
               markersize=12,
               color=data['color'],
               alpha=0.85)
    
    # Add threshold line
    ax.axhline(y=0.85, color='red', linestyle='--', linewidth=2.5,
              alpha=0.7, label='Proposed max_depth threshold (85%)')
    
    # Shaded regions
    ax.axhspan(0.85, 1.0, alpha=0.1, color='green', label='Safe growth zone')
    ax.axhspan(0.0, 0.85, alpha=0.05, color='red')
    
    # Formatting
    ax.set_xlabel('Circuit Depth (Logical Layers)', fontsize=16, fontweight='bold')
    ax.set_ylabel('GHZ State Fidelity', fontsize=16, fontweight='bold')
    ax.set_title('Empirical Depth Thresholds for ADQNN-GAGE\nibm_torino Qubit Chain [55, 65, 66, 67, 68]',
                fontsize=18, fontweight='bold', pad=20)
    
    ax.legend(fontsize=13, loc='lower left', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax.set_ylim([0.82, 0.95])
    ax.set_xlim([0, 22])
    
    # Add text annotations
    ax.text(12, 0.91, 'Plateau region:\nFidelity stabilizes\nat ~88% (4q) and\n~84% (5q)',
           fontsize=11, ha='center',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='yellow', alpha=0.3))
    
    ax.text(5, 0.835, 'ADQNN-GAGE recommended\ngrowth ceiling: Depth ≤ 10',
           fontsize=10, ha='center', style='italic',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.4))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Publication plot saved: {save_path}")
    
    return fig


def create_gate_count_plot(save_path='results/gate_count_analysis.png'):
    """Create a plot showing gate counts vs fidelity."""
    
    # Extracted from your JSON: CZ gate counts
    data_4q = {
        'depths': [2, 4, 6, 8, 10, 15, 20],
        'cz_gates': [6, 12, 18, 24, 30, 45, 60],
        'fidelities': [0.916, 0.928, 0.908, 0.915, 0.879, 0.882, 0.884]
    }
    
    data_5q = {
        'depths': [2, 4, 6, 8, 10, 15, 20],
        'cz_gates': [8, 16, 24, 32, 40, 60, 80],
        'fidelities': [0.894, 0.905, 0.879, 0.874, 0.863, 0.851, 0.837]
    }
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Fidelity vs CZ Gate Count
    ax1.scatter(data_4q['cz_gates'], data_4q['fidelities'], 
               s=150, alpha=0.7, label='4 qubits', color='#1f77b4')
    ax1.scatter(data_5q['cz_gates'], data_5q['fidelities'],
               s=150, alpha=0.7, label='5 qubits', color='#ff7f0e', marker='s')
    
    ax1.set_xlabel('Number of CZ Gates', fontsize=14, fontweight='bold')
    ax1.set_ylabel('GHZ Fidelity', fontsize=14, fontweight='bold')
    ax1.set_title('Fidelity vs Gate Count', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0.85, color='red', linestyle='--', alpha=0.6)
    
    # Plot 2: Gate Count vs Depth (showing scaling)
    ax2.plot(data_4q['depths'], data_4q['cz_gates'], 
            'o-', linewidth=2, markersize=10, label='4 qubits', color='#1f77b4')
    ax2.plot(data_5q['depths'], data_5q['cz_gates'],
            's-', linewidth=2, markersize=10, label='5 qubits', color='#ff7f0e')
    
    ax2.set_xlabel('Circuit Depth', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of CZ Gates', fontsize=14, fontweight='bold')
    ax2.set_title('Gate Count Scaling with Depth', fontsize=16, fontweight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Gate count analysis saved: {save_path}")
    
    return fig


def create_summary_table():
    """Print a summary table of key findings."""
    
    print("\n" + "="*80)
    print("EXPERIMENTAL SUMMARY: Noise-Adaptive Depth Thresholds")
    print("="*80)
    print("\nBackend: ibm_torino")
    print("Qubit chain: [55, 65, 66, 67, 68]")
    print("Average qubit error: ~0.87%")
    print("\n" + "-"*80)
    print(f"{'Qubits':<10} {'Depth Range':<15} {'Fidelity Range':<20} {'Decay':<15}")
    print("-"*80)
    print(f"{'4':<10} {'2 → 20':<15} {'0.916 → 0.884':<20} {'3.2%':<15}")
    print(f"{'5':<10} {'2 → 20':<15} {'0.894 → 0.837':<20} {'5.7%':<15}")
    print("-"*80)
    print("\nKey Findings:")
    print("  • 4-qubit circuits plateau at ~88% fidelity beyond depth 10")
    print("  • 5-qubit circuits show linear decay: 0.3% per depth step")
    print("  • Both maintain >83% fidelity even at depth 20 (60-80 CZ gates)")
    print("  • Recommended ADQNN-GAGE ceiling: depth ≤ 10 (~85% fidelity)")
    print("\nImplications for ADQNN-GAGE:")
    print("  ✓ Safe adaptive growth zone: depths 2-8 (>87% fidelity)")
    print("  ✓ Diminishing returns beyond depth 10-15")
    print("  ✓ Device-specific calibration validates noise-adaptive approach")
    print("="*80 + "\n")


def main():
    """Main execution."""
    
    print("="*80)
    print("DEPTH THRESHOLD ANALYSIS - COMPREHENSIVE VISUALIZATION")
    print("="*80)
    
    # Parse data
    runs = parse_saved_data()
    
    # Create plots
    print("\nGenerating plots...")
    create_publication_plot(runs)
    create_gate_count_plot()
    
    # Print summary
    create_summary_table()
    
    print("\n✓ All visualizations complete!")
    print("\nGenerated files:")
    print("  • results/publication_figure.png - Main comparison plot")
    print("  • results/gate_count_analysis.png - Gate scaling analysis")


if __name__ == "__main__":
    main()