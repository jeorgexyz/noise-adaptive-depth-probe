#!/usr/bin/env python3
"""
Analyze experimental results from saved JSON files.

This script can:
- Load multiple result files
- Compare different runs
- Generate summary statistics
- Create publication-quality plots
- Export analysis to CSV/LaTeX tables

Usage:
    python scripts/analyze_results.py --file results/my_results.json
    python scripts/analyze_results.py --directory results/sweeps/
    python scripts/analyze_results.py --compare file1.json file2.json
"""
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict
import pandas as pd


def load_results(filepath: str) -> dict:
    """Load results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_metrics(results: dict, backend: str = 'ibm_torino') -> pd.DataFrame:
    """Extract metrics into pandas DataFrame."""
    rows = []
    
    if backend not in results['data']:
        return pd.DataFrame()
    
    backend_data = results['data'][backend]
    
    for depth_key in sorted(backend_data.keys(), key=lambda x: int(x.split('_')[1])):
        depth_val = int(depth_key.split('_')[1])
        data = backend_data[depth_key]
        
        row = {
            'depth': depth_val,
            'transpiled_depth': data['circuit_depth_transpiled'],
            'gate_count': data['gate_count'],
            'cz_count': data.get('cz_count', 0),
            'fidelity': data['metrics']['ghz_fidelity'],
            'parity': data['metrics']['parity_expectation'],
            'hog': data['metrics']['heavy_output_frequency']
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def calculate_statistics(df: pd.DataFrame) -> Dict:
    """Calculate summary statistics."""
    return {
        'initial_fidelity': df['fidelity'].iloc[0],
        'final_fidelity': df['fidelity'].iloc[-1],
        'total_decay': df['fidelity'].iloc[0] - df['fidelity'].iloc[-1],
        'decay_percent': 100 * (df['fidelity'].iloc[0] - df['fidelity'].iloc[-1]) / df['fidelity'].iloc[0],
        'mean_fidelity': df['fidelity'].mean(),
        'std_fidelity': df['fidelity'].std(),
        'max_fidelity': df['fidelity'].max(),
        'min_fidelity': df['fidelity'].min(),
        'optimal_depth': int(df.loc[df['fidelity'].idxmax(), 'depth'])
    }


def plot_single_run(df: pd.DataFrame, metadata: dict, output_path: str = None):
    """Create comprehensive plot for single run."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Fidelity vs Depth
    axes[0, 0].plot(df['depth'], df['fidelity'], 'o-', linewidth=2, markersize=8)
    axes[0, 0].axhline(y=0.85, color='r', linestyle='--', alpha=0.5, label='85% threshold')
    axes[0, 0].set_xlabel('Circuit Depth', fontsize=12)
    axes[0, 0].set_ylabel('GHZ Fidelity', fontsize=12)
    axes[0, 0].set_title('Fidelity Decay', fontsize=14, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Gate Count vs Depth
    axes[0, 1].plot(df['depth'], df['cz_count'], 's-', linewidth=2, markersize=8, color='orange')
    axes[0, 1].set_xlabel('Circuit Depth', fontsize=12)
    axes[0, 1].set_ylabel('Number of CZ Gates', fontsize=12)
    axes[0, 1].set_title('Gate Scaling', fontsize=14, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Fidelity vs Gate Count
    axes[1, 0].scatter(df['cz_count'], df['fidelity'], s=100, alpha=0.7)
    axes[1, 0].set_xlabel('Number of CZ Gates', fontsize=12)
    axes[1, 0].set_ylabel('GHZ Fidelity', fontsize=12)
    axes[1, 0].set_title('Fidelity vs Gate Count', fontsize=14, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Multiple Metrics
    ax_twin = axes[1, 1].twinx()
    axes[1, 1].plot(df['depth'], df['fidelity'], 'o-', label='Fidelity', color='blue')
    ax_twin.plot(df['depth'], df['parity'], 's-', label='Parity', color='red', alpha=0.7)
    axes[1, 1].set_xlabel('Circuit Depth', fontsize=12)
    axes[1, 1].set_ylabel('Fidelity', fontsize=12, color='blue')
    ax_twin.set_ylabel('Parity Expectation', fontsize=12, color='red')
    axes[1, 1].set_title('Metrics Comparison', fontsize=14, fontweight='bold')
    axes[1, 1].legend(loc='upper left')
    ax_twin.legend(loc='upper right')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add metadata text
    n_qubits = metadata['n_qubits']
    backend = metadata['backends'][0]
    fig.suptitle(f'{n_qubits}-Qubit Depth Sweep on {backend}', 
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Plot saved: {output_path}")
    
    return fig


def compare_runs(files: List[str], output_path: str = None):
    """Compare multiple experimental runs."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(files)))
    
    for i, filepath in enumerate(files):
        results = load_results(filepath)
        df = extract_metrics(results)
        
        if df.empty:
            print(f"Warning: No data found in {filepath}")
            continue
        
        label = f"{results['metadata']['n_qubits']}q ({Path(filepath).stem})"
        ax.plot(df['depth'], df['fidelity'], 
               marker='o', label=label, linewidth=2, 
               markersize=8, color=colors[i])
    
    ax.axhline(y=0.85, color='red', linestyle='--', linewidth=2, 
              alpha=0.6, label='85% threshold')
    ax.set_xlabel('Circuit Depth', fontsize=14, fontweight='bold')
    ax.set_ylabel('GHZ Fidelity', fontsize=14, fontweight='bold')
    ax.set_title('Comparison of Experimental Runs', fontsize=16, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Comparison plot saved: {output_path}")
    
    plt.show()


def export_to_csv(df: pd.DataFrame, filepath: str):
    """Export DataFrame to CSV."""
    df.to_csv(filepath, index=False)
    print(f"✓ Data exported to CSV: {filepath}")


def export_to_latex(df: pd.DataFrame, filepath: str):
    """Export DataFrame as LaTeX table."""
    latex = df.to_latex(index=False, float_format="%.3f")
    
    with open(filepath, 'w') as f:
        f.write(latex)
    
    print(f"✓ LaTeX table saved: {filepath}")


def print_summary_report(results: dict, df: pd.DataFrame):
    """Print comprehensive summary report."""
    metadata = results['metadata']
    stats = calculate_statistics(df)
    
    print("\n" + "="*70)
    print("EXPERIMENTAL RESULTS SUMMARY")
    print("="*70)
    
    print(f"\n📊 Experiment Details:")
    print(f"  Timestamp: {metadata['timestamp']}")
    print(f"  Backend: {metadata['backends'][0]}")
    print(f"  Qubits: {metadata['n_qubits']}")
    print(f"  Shots per circuit: {metadata['shots']}")
    print(f"  Qubit mapping: {metadata.get('qubit_mapping', 'Not specified')}")
    
    print(f"\n📈 Fidelity Statistics:")
    print(f"  Initial (d={df['depth'].iloc[0]}): {stats['initial_fidelity']:.4f}")
    print(f"  Final (d={df['depth'].iloc[-1]}): {stats['final_fidelity']:.4f}")
    print(f"  Total decay: {stats['total_decay']:.4f} ({stats['decay_percent']:.2f}%)")
    print(f"  Mean: {stats['mean_fidelity']:.4f} ± {stats['std_fidelity']:.4f}")
    print(f"  Peak: {stats['max_fidelity']:.4f} at depth {stats['optimal_depth']}")
    
    print(f"\n🎯 Depth Recommendations:")
    if stats['mean_fidelity'] > 0.90:
        print("  ✅ Excellent performance - can use all tested depths")
    elif stats['mean_fidelity'] > 0.85:
        print("  ✅ Good performance - safe to use tested depths")
        depths_above_85 = df[df['fidelity'] > 0.85]['depth'].tolist()
        print(f"  ✅ Depths maintaining >85% fidelity: {depths_above_85}")
    else:
        print("  ⚠️  Moderate performance - consider shallower circuits")
        depths_above_85 = df[df['fidelity'] > 0.85]['depth'].tolist()
        if depths_above_85:
            print(f"  Recommended max_depth: {max(depths_above_85)}")
    
    print(f"\n⚙️  Gate Statistics:")
    print(f"  Total CZ gates (d={df['depth'].iloc[-1]}): {df['cz_count'].iloc[-1]}")
    print(f"  Average gates per depth: {df['cz_count'].iloc[-1] / df['depth'].iloc[-1]:.1f}")
    
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze depth threshold experimental results',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=str, help='Single result file to analyze')
    input_group.add_argument('--directory', type=str, help='Directory containing multiple result files')
    input_group.add_argument('--compare', nargs='+', help='Multiple files to compare')
    
    # Output options
    parser.add_argument('--output', type=str, default='results/analysis',
                       help='Output directory for plots and exports')
    parser.add_argument('--export-csv', action='store_true',
                       help='Export data to CSV')
    parser.add_argument('--export-latex', action='store_true',
                       help='Export data as LaTeX table')
    parser.add_argument('--no-plot', action='store_true',
                       help='Skip plot generation')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle different input modes
    if args.file:
        # Single file analysis
        print(f"Analyzing: {args.file}")
        results = load_results(args.file)
        df = extract_metrics(results)
        
        if df.empty:
            print("Error: No data found in file")
            return
        
        # Print summary
        print_summary_report(results, df)
        
        # Export if requested
        if args.export_csv:
            csv_path = output_dir / f"{Path(args.file).stem}.csv"
            export_to_csv(df, str(csv_path))
        
        if args.export_latex:
            latex_path = output_dir / f"{Path(args.file).stem}.tex"
            export_to_latex(df, str(latex_path))
        
        # Plot if requested
        if not args.no_plot:
            plot_path = output_dir / f"{Path(args.file).stem}_analysis.png"
            plot_single_run(df, results['metadata'], str(plot_path))
            plt.show()
    
    elif args.directory:
        # Directory analysis
        print(f"Analyzing all files in: {args.directory}")
        json_files = list(Path(args.directory).glob('*.json'))
        
        if not json_files:
            print("Error: No JSON files found in directory")
            return
        
        print(f"Found {len(json_files)} result files")
        
        # Compare all files
        if not args.no_plot:
            compare_path = output_dir / "comparison_all_runs.png"
            compare_runs([str(f) for f in json_files], str(compare_path))
    
    elif args.compare:
        # Compare specific files
        print(f"Comparing {len(args.compare)} files")
        
        if not args.no_plot:
            compare_path = output_dir / "comparison.png"
            compare_runs(args.compare, str(compare_path))
    
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()