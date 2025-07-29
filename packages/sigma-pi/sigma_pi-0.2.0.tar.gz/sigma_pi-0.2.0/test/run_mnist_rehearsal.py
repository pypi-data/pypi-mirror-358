import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import importlib.util
import torch
from datetime import datetime
from collections import defaultdict

from test.run_experiment import setup_experiment, get_dataloaders, execute_training_loop, Tee
from test.utils.plotting import plot_metrics

def merge_metrics(main_metrics, new_metrics):
    for key, value in new_metrics.items():
        main_metrics[key].extend(value)

def run_mnist_rehearsal_experiment(config_path: str, checkpoint_path: str = None):
    spec = importlib.util.spec_from_file_location(name="config", location=config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    train_cfg = config.train_config
    log_dir = os.path.join(train_cfg['output_dir'], 'log')
    os.makedirs(log_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    config_name = os.path.basename(config_path).replace('.py', '').replace('_', '-')
    log_file_name = f"{current_time}-{config_name}-mnist-rehearsal.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    original_stdout = sys.stdout
    log_file = open(log_file_path, 'w')
    sys.stdout = Tee(original_stdout, log_file)
    print(f"Logging output to: {log_file_path}")

    try:
        task_suffix = "-mnist-rehearsal"
        config_name = os.path.basename(config_path).replace('.py', '').replace('_', '-')
        model, optimizer, loss_fn, pi_monitor, device, model_name = setup_experiment(
            config, base_model_name=config_name, model_name_suffix=task_suffix, checkpoint_path=checkpoint_path
        )
        
        # Load FashionMNIST and MNIST dataloaders
        model_img_size = config.model_config['img_size']
        fashion_mnist_train_loader, fashion_mnist_val_loader = get_dataloaders('FashionMNIST', train_cfg['batch_size'], model_img_size)
        mnist_train_loader, mnist_val_loader = get_dataloaders('MNIST', train_cfg['batch_size'], model_img_size)
        # Initialize metric collectors
        full_step_metrics = defaultdict(list)
        full_epoch_metrics = defaultdict(list)
        
        global_step = 0
        start_epoch = 1 # Start from scratch for this new experiment
        num_rehearsal_cycles = 4 # Changed from 5 to 4
        fashion_mnist_epochs_per_cycle = 4
        rehearsal_epochs = 1

        print("\n" + "="*50)
        print(" " * 10 + f"FashionMNIST Rehearsal: {num_rehearsal_cycles}x({fashion_mnist_epochs_per_cycle} FashionMNIST + {rehearsal_epochs} MNIST)")
        print("="*50 + "\n")

        for i in range(num_rehearsal_cycles):
            print(f"\n--- Cycle {i+1}/{num_rehearsal_cycles} ---")
            # Train on FashionMNIST
            print(f"\n--- Training on FashionMNIST for {fashion_mnist_epochs_per_cycle} epochs ---")
            
            model, global_step, step_metrics, epoch_metrics = execute_training_loop(
                model=model, optimizer=optimizer, loss_fn=loss_fn, pi_monitor=pi_monitor,
                device=device, model_name=model_name,
                train_loader=fashion_mnist_train_loader,
                val_loaders={"FashionMNIST_Val": fashion_mnist_val_loader, "MNIST_Val": mnist_val_loader},
                epochs=fashion_mnist_epochs_per_cycle,
                use_gbp=(config.model_config.get('model_type') == 'gbp_moe'),
                accumulation_steps=train_cfg['accumulation_steps'],
                output_dir=train_cfg['output_dir'],
                start_epoch=start_epoch,
                global_step=global_step,
                train_fn_kwargs=train_cfg.get('train_fn_kwargs', {})
            )
            merge_metrics(full_step_metrics, step_metrics)
            merge_metrics(full_epoch_metrics, epoch_metrics)
            start_epoch += fashion_mnist_epochs_per_cycle
            
            # Rehearsal on MNIST
            print(f"\n--- Rehearsal on MNIST for {rehearsal_epochs} epoch ---")
            model, global_step, step_metrics, epoch_metrics = execute_training_loop(
                model=model, optimizer=optimizer, loss_fn=loss_fn, pi_monitor=pi_monitor,
                device=device, model_name=model_name,
                train_loader=mnist_train_loader,
                val_loaders={"FashionMNIST_Val": fashion_mnist_val_loader, "MNIST_Val": mnist_val_loader},
                epochs=rehearsal_epochs,
                use_gbp=(config.model_config.get('model_type') == 'gbp_moe'),
                accumulation_steps=train_cfg['accumulation_steps'],
                output_dir=train_cfg['output_dir'],
                start_epoch=start_epoch,
                global_step=global_step,
                train_fn_kwargs=train_cfg.get('train_fn_kwargs', {})
            )
            merge_metrics(full_step_metrics, step_metrics)
            merge_metrics(full_epoch_metrics, epoch_metrics)
            start_epoch += rehearsal_epochs

        # --- FINAL PLOTTING & EVALUATION ---
        plot_metrics_kwargs = {}
        use_gbp = config.model_config.get('model_type') == 'gbp_moe'
        train_fn_kwargs = train_cfg.get('train_fn_kwargs', {})
        if use_gbp:
            if train_fn_kwargs.get('gbp_mode', 'gate') == 'gate':
                if 'gbp_surprise_values' in full_epoch_metrics:
                    plot_metrics_kwargs['gbp_surprise_values'] = full_epoch_metrics['gbp_surprise_values']
                    plot_metrics_kwargs['gbp_decisions'] = full_epoch_metrics['gbp_decisions']
            elif train_fn_kwargs.get('gbp_mode') == 'lr_scheduler':
                if 'train_lr_mod' in full_epoch_metrics:
                    plot_metrics_kwargs['lr_mod_values'] = full_epoch_metrics['train_lr_mod']

        plot_metrics(full_step_metrics, full_epoch_metrics, train_cfg['output_dir'], model_name=model_name, **plot_metrics_kwargs)
        print(f"\nPlots for full experiment saved to: {os.path.abspath(train_cfg['output_dir'])}")

    finally:
        sys.stdout = original_stdout
        log_file.close()
        print(f"Training completed. Log saved to: {log_file_path}")

def main():
    parser = argparse.ArgumentParser(description="Run a continual learning experiment with MNIST and FashionMNIST.")
    parser.add_argument('--config', type=str, required=True, help="Path to the model configuration file.")
    parser.add_argument('--checkpoint_path', type=str, default=None, help="Optional path to a model checkpoint to start from.")
    args = parser.parse_args()
    run_mnist_rehearsal_experiment(args.config, args.checkpoint_path)

if __name__ == "__main__":
    main()
