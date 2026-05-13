"""Visualization functions."""
import matplotlib.pyplot as plt


def plot_results(results, output_path='depth_threshold_analysis.png'):
    """
    Generate publication-quality plots of depth vs. metrics.
    
    Args:
        results: Experiment results dictionary
        output_path: Path to save figure
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for backend_name, backend_data in results['data'].items():
        depths = []
        fidelities = []
        parities = []
        hogs = []
        
        for depth_key in sorted(backend_data.keys(), 
                                key=lambda x: int(x.split('_')[1])):
            depth_val = int(depth_key.split('_')[1])
            metrics = backend_data[depth_key]['metrics']
            
            depths.append(depth_val)
            fidelities.append(metrics['ghz_fidelity'])
            parities.append(metrics['parity_expectation'])
            hogs.append(metrics['heavy_output_frequency'])
        
        # Plot 1: GHZ Fidelity vs Depth
        axes[0].plot(depths, fidelities, 'o-', label=backend_name, 
                    linewidth=2, markersize=8)
        axes[0].set_xlabel('Circuit Depth', fontsize=12)
        axes[0].set_ylabel('GHZ Fidelity', fontsize=12)
        axes[0].set_title('Fidelity Decay with Circuit Depth', 
                         fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        axes[0].set_ylim([0, 1.05])
        
        # Plot 2: Parity Expectation vs Depth
        axes[1].plot(depths, parities, 's-', label=backend_name, 
                    linewidth=2, markersize=8)
        axes[1].set_xlabel('Circuit Depth', fontsize=12)
        axes[1].set_ylabel('Parity Expectation ⟨Z⊗Z⊗...⊗Z⟩', fontsize=12)
        axes[1].set_title('Parity Oscillation Decay', 
                         fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        axes[1].axhline(y=0, color='k', linestyle='--', alpha=0.3)
        
        # Plot 3: Heavy Output Frequency vs Depth
        axes[2].plot(depths, hogs, '^-', label=backend_name, 
                    linewidth=2, markersize=8)
        axes[2].set_xlabel('Circuit Depth', fontsize=12)
        axes[2].set_ylabel('Heavy Output Frequency', fontsize=12)
        axes[2].set_title('HOG Metric vs Depth', 
                         fontsize=14, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()
        axes[2].set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as '{output_path}'")
    plt.show()