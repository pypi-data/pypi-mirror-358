import matplotlib.pyplot as plt
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def plot_gbp_decisions(
    gbp_surprise_values: List[Tuple[int, float]],
    gbp_decisions: List[Tuple[int, str]],
    output_dir: str,
    model_name: str = "model"
) -> None:
    if not gbp_surprise_values or not gbp_decisions:
        print("No GBP decision data to plot.")
        return

    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Prepare data for plotting
    steps = [s for s, _ in gbp_surprise_values]
    surprise_vals = [v for _, v in gbp_surprise_values]
    decisions = [d for _, d in gbp_decisions]

    # Map decisions to colors and markers
    color_map = {'CONSOLIDATE': 'green', 'IGNORE': 'blue', 'REJECT': 'red'}
    marker_map = {'CONSOLIDATE': 'o', 'IGNORE': 'x', 'REJECT': '^'}
    label_map = {'CONSOLIDATE': 'Consolidate (Update)', 'IGNORE': 'Ignore (No Update)', 'REJECT': 'Reject (No Update)'}

    # Plot each decision type
    for decision_type in ['CONSOLIDATE', 'IGNORE', 'REJECT']:
        filtered_steps = [steps[i] for i, d in enumerate(decisions) if d == decision_type]
        filtered_surprise = [surprise_vals[i] for i, d in enumerate(decisions) if d == decision_type]
        
        if filtered_steps:
            ax.scatter(
                filtered_steps,
                filtered_surprise,
                color=color_map[decision_type],
                marker=marker_map[decision_type],
                label=label_map[decision_type],
                alpha=0.6
            )

    ax.set_title(f'GBP Decision vs. Surprise over Steps ({model_name})')
    ax.set_xlabel('Global Steps')
    ax.set_ylabel('Surprise (Gradient Norm)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)

    current_date = datetime.now().strftime("%Y%m%d")
    file_name = f"{current_date}-{model_name}-GBP_Decisions.png"
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

def plot_metrics(
    step_metrics: Dict[str, List[Tuple[int, float]]],
    epoch_metrics: Dict[str, List[Tuple[int, float]]],
    output_dir: str,
    model_name: str = "model",
    gbp_surprise_values: Optional[List[Tuple[int, float]]] = None,
    gbp_decisions: Optional[List[Tuple[int, str]]] = None,
    lr_mod_values: Optional[List[Tuple[int, float]]] = None # Added lr_mod_values
) -> None:
    
    # Determine the number of subplots needed
    num_plots = len(['loss', 'acc', 'pi', 'surprise', 'tau'])
    if gbp_surprise_values and gbp_decisions:
        num_plots += 1 # Add one for the GBP decision plot
    if lr_mod_values: # Add one for LR-Mod plot
        num_plots += 1

    # Adjust figsize based on number of plots
    rows = (num_plots + 1) // 2 # 2 columns
    fig = plt.figure(figsize=(10 * 2, 5 * rows)) # Adjust width and height per plot

    fig.suptitle(model_name, fontsize=16)
    
    metric_types = ['loss', 'acc', 'pi', 'surprise', 'tau']
    plot_titles = {
        'loss': 'Loss',
        'acc': 'Accuracy',
        'pi': 'Predictive Integrity (PI)',
        'surprise': 'Surprise (Gradient Norm)',
        'tau': 'Tau (Entropy)',
        'lr_mod': 'Learning Rate Modifier' # Added LR-Mod title
    }
    y_labels = {
        'loss': 'Loss',
        'acc': 'Accuracy (%)',
        'pi': 'PI Score',
        'surprise': 'Surprise',
        'tau': 'Tau',
        'lr_mod': 'LR Modifier' # Added LR-Mod label
    }

    current_subplot_idx = 0
    for i, metric_type in enumerate(metric_types):
        current_subplot_idx += 1
        plt.subplot(rows, 2, current_subplot_idx)
        
        # Plot step-level data (only for training)
        train_key = f'train_{metric_type}'
        if train_key in step_metrics and step_metrics[train_key]:
            steps, values = zip(*step_metrics[train_key])
            plt.plot(steps, values, alpha=0.5, label=f'Train {metric_type} (Step)')

        # Plot epoch-level data
        for key, data in epoch_metrics.items():
            if metric_type in key and data:
                steps, values = zip(*data)
                label = key.replace('_', ' ').title()
                plt.plot(steps, values, marker='o', linestyle='-', label=f'{label} (Epoch Avg)')

        plt.title(f'{plot_titles[metric_type]} over Steps')
        plt.xlabel('Global Steps')
        plt.ylabel(y_labels[metric_type])
        plt.legend()
        plt.grid(True)

    # Add the LR-Mod plot if data is available
    if lr_mod_values:
        current_subplot_idx += 1
        plt.subplot(rows, 2, current_subplot_idx)
        steps, values = zip(*lr_mod_values)
        plt.plot(steps, values, marker='o', linestyle='-', label='Train LR-Mod (Epoch Avg)', color='purple')
        plt.title(f'{plot_titles["lr_mod"]} over Steps')
        plt.xlabel('Global Steps')
        plt.ylabel(y_labels["lr_mod"])
        plt.legend()
        plt.grid(True)

    # Add the GBP decision plot if data is available
    if gbp_surprise_values and gbp_decisions:
        current_subplot_idx += 1
        plt.subplot(rows, 2, current_subplot_idx) # Place it in the next available subplot position
        plot_gbp_decisions_internal(
            plt.gca(), # Get current axes
            gbp_surprise_values,
            gbp_decisions,
            model_name
        )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to make room for suptitle
    
    current_date = datetime.now().strftime("%Y%m%d")
    file_name = f"{current_date}-{model_name}.png"
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Internal helper for plotting GBP decisions on a given axes
def plot_gbp_decisions_internal(
    ax,
    gbp_surprise_values: List[Tuple[int, float]],
    gbp_decisions: List[Tuple[int, str]],
    model_name: str
) -> None:
    
    # Prepare data for plotting
    steps = [s for s, _ in gbp_surprise_values]
    surprise_vals = [v for _, v in gbp_surprise_values]
    decisions = [d for _, d in gbp_decisions]

    # Map decisions to colors and markers
    color_map = {'CONSOLIDATE': 'green', 'IGNORE': 'blue', 'REJECT': 'red'}
    marker_map = {'CONSOLIDATE': 'o', 'IGNORE': 'x', 'REJECT': '^'}
    label_map = {'CONSOLIDATE': 'Consolidate (Update)', 'IGNORE': 'Ignore (No Update)', 'REJECT': 'Reject (No Update)'}

    # Plot each decision type
    for decision_type in ['CONSOLIDATE', 'IGNORE', 'REJECT']:
        filtered_steps = [steps[i] for i, d in enumerate(decisions) if d == decision_type]
        filtered_surprise = [surprise_vals[i] for i, d in enumerate(decisions) if d == decision_type]
        
        if filtered_steps:
            ax.scatter(
                filtered_steps,
                filtered_surprise,
                color=color_map[decision_type],
                marker=marker_map[decision_type],
                label=label_map[decision_type],
                alpha=0.6
            )

    ax.set_title(f'GBP Decision vs. Surprise over Steps')
    ax.set_xlabel('Global Steps')
    ax.set_ylabel('Surprise (Gradient Norm)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
