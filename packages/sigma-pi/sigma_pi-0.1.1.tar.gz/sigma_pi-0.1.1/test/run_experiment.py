import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import os
import argparse
import importlib.util
from main import SigmaPI
from test.utils.training import train, validate
from test.utils.plotting import plot_metrics
from test.models.vit import VisionTransformer, MoEVisionTransformer
from torchvision import datasets, transforms
from datetime import datetime
from typing import Dict, Any

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()
    def isatty(self):
        return False

def setup_experiment(config: Dict[str, Any], model_name_suffix: str = "", checkpoint_path: str = None):
    model_cfg = config.model_config
    train_cfg = config.train_config
    pi_cfg = config.pi_config

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == 'cpu':
        raise RuntimeError("CUDA not available, exiting.")

    model_type = model_cfg.get('model_type') # Use .get() to avoid popping
    if model_type == 'base':
        model = VisionTransformer(**model_cfg).to(device)
    elif model_type in ['moe', 'gbp_moe']:
        model = MoEVisionTransformer(**model_cfg).to(device)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    if checkpoint_path:
        print(f"Loading checkpoint from: {checkpoint_path}")
        model.load_state_dict(torch.load(checkpoint_path))

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Construct a clean model name based on the config file name
    config_name = model_name_suffix.split('/')[-1].replace('.py', '')
    model_name = f"{config_name}{model_name_suffix}"
    print(f"Model: {model_name}")
    print(f"Total Trainable Parameters: {total_params/1e6:.2f}M")

    optimizer = optim.AdamW(model.parameters(), lr=train_cfg['learning_rate'], weight_decay=train_cfg['weight_decay'])
    loss_fn = nn.CrossEntropyLoss()
    pi_monitor = SigmaPI(**pi_cfg)

    return model, optimizer, loss_fn, pi_monitor, device, model_name

def get_dataloaders(dataset_name: str, batch_size: int, num_workers: int = 8):
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    if dataset_name.upper() == 'CIFAR10':
        data_dir = "temp_data/CIFAR10"
        os.makedirs(data_dir, exist_ok=True)
        is_downloaded = os.path.exists(os.path.join(data_dir, 'cifar-10-batches-py'))
        train_dataset = datasets.CIFAR10(data_dir, train=True, download=not is_downloaded, transform=transform_train)
        val_dataset = datasets.CIFAR10(data_dir, train=False, download=not is_downloaded, transform=transform_test)
    elif dataset_name.upper() == 'SVHN':
        data_dir = "temp_data/SVHN"
        os.makedirs(data_dir, exist_ok=True)
        train_file = os.path.join(data_dir, 'train_32x32.mat')
        test_file = os.path.join(data_dir, 'test_32x32.mat')
        train_dataset = datasets.SVHN(data_dir, split='train', download=not os.path.exists(train_file), transform=transform_train)
        val_dataset = datasets.SVHN(data_dir, split='test', download=not os.path.exists(test_file), transform=transform_test)
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
    
    return train_loader, val_loader

def execute_training_loop(
    model, optimizer, loss_fn, pi_monitor, device, model_name,
    train_loader, val_loaders: Dict[str, DataLoader],
    epochs: int, accumulation_steps: int, output_dir: str,
    use_gbp: bool,
    start_epoch: int = 1, global_step: int = 0,
    train_fn_kwargs: Dict[str, Any] = {}
):
    metric_keys = ['loss', 'acc', 'pi', 'surprise', 'tau']
    step_metrics = {f'train_{key}': [] for key in metric_keys}
    epoch_metrics = {f'train_{key}': [] for key in metric_keys}
    for val_set_name in val_loaders.keys():
        for key in metric_keys:
            epoch_metrics[f'{val_set_name}_{key}'] = []

    for epoch in range(start_epoch, start_epoch + epochs):
        print(f"\n--- Epoch {epoch} ---")
        
        train_output = train(
            model, device, train_loader, optimizer, epoch, loss_fn, 
            pi_monitor, step_metrics, epoch_metrics, global_step, 
            accumulation_steps, use_gbp=use_gbp, **train_fn_kwargs
        )

        if use_gbp:
            global_step, gbp_surprise_values, gbp_decisions = train_output
            if 'gbp_surprise_values' not in epoch_metrics:
                epoch_metrics['gbp_surprise_values'] = []
                epoch_metrics['gbp_decisions'] = []
            epoch_metrics['gbp_surprise_values'].extend(gbp_surprise_values)
            epoch_metrics['gbp_decisions'].extend(gbp_decisions)
        else:
            global_step = train_output

        for name, loader in val_loaders.items():
            val_loss, val_acc, val_pi, val_surprise, val_tau = validate(model, device, loader, loss_fn, pi_monitor, dataset_name=name)
            epoch_metrics[f'{name}_loss'].append((global_step - 1, val_loss))
            epoch_metrics[f'{name}_acc'].append((global_step - 1, val_acc))
            epoch_metrics[f'{name}_pi'].append((global_step - 1, val_pi))
            epoch_metrics[f'{name}_surprise'].append((global_step - 1, val_surprise))
            epoch_metrics[f'{name}_tau'].append((global_step - 1, val_tau))

    checkpoint_dir = os.path.join(output_dir, 'checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_name = f"{model_name}-epoch_{start_epoch + epochs - 1}.pth"
    checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)
    torch.save(model.state_dict(), checkpoint_path)
    print(f"\nCheckpoint saved to: {checkpoint_path}")

    plot_metrics_kwargs = {}
    if 'gbp_surprise_values' in epoch_metrics:
        plot_metrics_kwargs['gbp_surprise_values'] = epoch_metrics['gbp_surprise_values']
        plot_metrics_kwargs['gbp_decisions'] = epoch_metrics['gbp_decisions']

    plot_metrics(step_metrics, epoch_metrics, output_dir, model_name=model_name, **plot_metrics_kwargs)
    print(f"\nPlots saved to: {os.path.abspath(output_dir)}")
    
    return model, global_step

def run_experiment(config, config_path: str, task_name_suffix: str = "", checkpoint_path: str = None):
    train_cfg = config.train_config
    log_dir = os.path.join(train_cfg['output_dir'], 'log')
    os.makedirs(log_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    config_name = os.path.basename(config_path).replace('.py', '')
    log_file_name = f"{current_time}-{config_name}{task_name_suffix}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    original_stdout = sys.stdout
    log_file = open(log_file_path, 'w')
    sys.stdout = Tee(original_stdout, log_file)
    print(f"Logging output to: {log_file_path}")

    try:
        model, optimizer, loss_fn, pi_monitor, device, model_name = setup_experiment(config, model_name_suffix=f"{task_name_suffix}", checkpoint_path=checkpoint_path)
        
        train_loader, val_loader = get_dataloaders('CIFAR10', train_cfg['batch_size'])
        _, ood_val_loader = get_dataloaders('SVHN', train_cfg['batch_size'])

        val_loaders = {
            "CIFAR10_Val": val_loader,
            "SVHN_OOD_Val": ood_val_loader
        }

        execute_training_loop(
            model=model, optimizer=optimizer, loss_fn=loss_fn, pi_monitor=pi_monitor,
            device=device, model_name=model_name,
            train_loader=train_loader, val_loaders=val_loaders,
            epochs=train_cfg['epochs'], accumulation_steps=train_cfg['accumulation_steps'],
            use_gbp=(config.model_config.get('model_type') == 'gbp_moe'),
            output_dir=train_cfg['output_dir'],
            train_fn_kwargs=train_cfg.get('train_fn_kwargs', {})
        )
    finally:
        sys.stdout = original_stdout
        log_file.close()
        print(f"Training completed. Log saved to: {log_file_path}")

def main():
    parser = argparse.ArgumentParser(description="Run a ViT experiment from a configuration file.")
    parser.add_argument('--config', type=str, required=True, help="Path to the configuration file.")
    parser.add_argument('--task', type=str, default="single", help="Task name for logging (e.g., 'CIFAR10', 'continual').")
    parser.add_argument('--checkpoint_path', type=str, default=None, help="Path to a model checkpoint to load.")
    args = parser.parse_args()

    # Load config module
    spec = importlib.util.spec_from_file_location(name="config", location=args.config)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    
    run_experiment(config, config_path=args.config, task_name_suffix=f"-{args.task}", checkpoint_path=args.checkpoint_path)

if __name__ == "__main__":
    main()
