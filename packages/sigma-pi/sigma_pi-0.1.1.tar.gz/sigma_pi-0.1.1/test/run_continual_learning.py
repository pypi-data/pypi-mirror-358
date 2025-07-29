import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import importlib.util
import torch
from datetime import datetime

from test.run_experiment import setup_experiment, get_dataloaders, execute_training_loop, Tee
from test.utils.training import validate

def run_continual_experiment(config_path: str, checkpoint_path: str = None, start_stage: int = 1):
    spec = importlib.util.spec_from_file_location(name="config", location=config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    train_cfg = config.train_config
    log_dir = os.path.join(train_cfg['output_dir'], 'log')
    os.makedirs(log_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    config_name = os.path.basename(config_path).replace('.py', '')
    log_file_name = f"{current_time}-{config_name}-continual.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    original_stdout = sys.stdout
    log_file = open(log_file_path, 'w')
    sys.stdout = Tee(original_stdout, log_file)
    print(f"Logging output to: {log_file_path}")

    try:
        task_suffix = "-continual"
        model, optimizer, loss_fn, pi_monitor, device, model_name = setup_experiment(
            config, model_name_suffix=task_suffix, checkpoint_path=checkpoint_path
        )
        
        global_step = 0
        
        # --- STAGE 1: CIFAR-10 ---
        if start_stage <= 1:
            print("\n" + "="*50)
            print(" " * 15 + "STAGE 1: Training on CIFAR-10")
            print("="*50 + "\n")
            
            cifar_train_loader, cifar_val_loader = get_dataloaders('CIFAR10', train_cfg['batch_size'])
            stage1_val_loaders = {"CIFAR10_Val": cifar_val_loader}
            
            model, global_step = execute_training_loop(
                model=model, optimizer=optimizer, loss_fn=loss_fn, pi_monitor=pi_monitor,
                device=device, model_name=model_name,
                train_loader=cifar_train_loader, val_loaders=stage1_val_loaders,
                epochs=20,
                use_gbp=(config.model_config.get('model_type') == 'gbp_moe'),
                accumulation_steps=train_cfg['accumulation_steps'],
                output_dir=train_cfg['output_dir'],
                train_fn_kwargs=train_cfg.get('train_fn_kwargs', {})
            )
        else:
            print("\nSkipping Stage 1: Training on CIFAR-10 as requested.")

        # --- STAGE 2: SVHN ---
        if start_stage <= 2:
            print("\n" + "="*50)
            print(" " * 15 + "STAGE 2: Training on SVHN")
            print("="*50 + "\n")

            svhn_train_loader, svhn_val_loader = get_dataloaders('SVHN', train_cfg['batch_size'])
            # We need cifar_val_loader for the final comparison
            _, cifar_val_loader = get_dataloaders('CIFAR10', train_cfg['batch_size'])
            
            stage2_val_loaders = {
                "CIFAR10_Val": cifar_val_loader,
                "SVHN_Val": svhn_val_loader
            }

            model, _ = execute_training_loop(
                model=model, optimizer=optimizer, loss_fn=loss_fn, pi_monitor=pi_monitor,
                device=device, model_name=model_name,
                train_loader=svhn_train_loader, val_loaders=stage2_val_loaders,
                epochs=10,
                use_gbp=(config.model_config.get('model_type') == 'gbp_moe'),
                accumulation_steps=train_cfg['accumulation_steps'],
                output_dir=train_cfg['output_dir'],
                start_epoch=21,
                global_step=global_step,
                train_fn_kwargs=train_cfg.get('train_fn_kwargs', {})
            )

        # --- FINAL EVALUATION ---
        print("\n" + "="*50)
        print(" " * 18 + "FINAL EVALUATION")
        print("="*50 + "\n")

        print(f"--- Final performance for model: {model_name} ---")
        
        _, cifar_val_loader = get_dataloaders('CIFAR10', train_cfg['batch_size'])
        _, svhn_val_loader = get_dataloaders('SVHN', train_cfg['batch_size'])
        
        validate(model, device, cifar_val_loader, loss_fn, pi_monitor, dataset_name="Final CIFAR-10 Val")
        validate(model, device, svhn_val_loader, loss_fn, pi_monitor, dataset_name="Final SVHN Val")

    finally:
        sys.stdout = original_stdout
        log_file.close()
        print(f"Training completed. Log saved to: {log_file_path}")

def main():
    parser = argparse.ArgumentParser(description="Run a continual learning experiment (CIFAR-10 -> SVHN).")
    parser.add_argument('--config', type=str, required=True, help="Path to the model configuration file.")
    parser.add_argument('--checkpoint_path', type=str, default=None, help="Path to a model checkpoint to load and continue training.")
    parser.add_argument('--start_stage', type=int, default=1, choices=[1, 2], help="Start from a specific stage (1: CIFAR, 2: SVHN).")
    args = parser.parse_args()
    run_continual_experiment(args.config, args.checkpoint_path, args.start_stage)

if __name__ == "__main__":
    main()
