import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os
from main import SigmaPI
from test.utils.plotting import plot_metrics

def train(model, device, train_loader, optimizer, epoch, loss_fn, pi_monitor, 
          step_metrics, epoch_metrics, global_step, accumulation_steps, 
          use_gbp=False, initial_surprise_ema=None):
    model.train()
    optimizer.zero_grad()

    # GBP specific state
    ema_surprise = initial_surprise_ema
    ema_surprise_sq = initial_surprise_ema ** 2 if initial_surprise_ema is not None else None
    alpha = 0.1

    epoch_summary = {
        'loss': [], 'acc': [], 'pi': [], 'surprise': [], 'tau': [],
        'consolidate': [], 'ignore': [], 'reject': [],
        'surprise_values': [], 'decisions': []
    }

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        output = model(data)
        # Handle both standard and MoE model outputs
        logits = output[0] if isinstance(output, tuple) else output
        all_gating_logits = output[1] if isinstance(output, tuple) else None

        loss = loss_fn(logits, target)
        loss_normalized = loss / accumulation_steps
        loss_normalized.backward()

        pred = logits.argmax(dim=1, keepdim=True)
        correct = pred.eq(target.view_as(pred)).sum().item()
        accuracy = 100. * correct / len(data)

        if (batch_idx + 1) % accumulation_steps == 0:
            if use_gbp:
                if all_gating_logits is None:
                    raise ValueError("GBP requires a model that returns gating logits.")
                model.zero_inactive_expert_grads(all_gating_logits)
            
            pi_metrics = pi_monitor.calculate(model, loss, logits)
            
            if use_gbp:
                surprise = torch.tensor(pi_metrics['surprise'], device=device)
                if ema_surprise is None:
                    ema_surprise = surprise
                    ema_surprise_sq = surprise ** 2
                else:
                    ema_surprise = alpha * surprise + (1 - alpha) * ema_surprise
                    ema_surprise_sq = alpha * (surprise ** 2) + (1 - alpha) * ema_surprise_sq
                
                variance = ema_surprise_sq - ema_surprise ** 2
                std_dev = torch.sqrt(torch.clamp(variance, min=0))
                
                s_low = ema_surprise - 2.5 * std_dev
                s_high = ema_surprise + 2.5 * std_dev

                decision = "IGNORE"
                if s_low <= surprise < s_high:
                    decision = "CONSOLIDATE"
                    optimizer.step()
                elif surprise >= s_high:
                    decision = "REJECT"
                
                epoch_summary[decision.lower()].append(1)
                epoch_summary['surprise_values'].append((global_step, surprise.item()))
                epoch_summary['decisions'].append((global_step, decision))
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            optimizer.zero_grad()

            # Log metrics for both modes
            step_metrics['train_loss'].append((global_step, loss.item()))
            step_metrics['train_acc'].append((global_step, accuracy))
            step_metrics['train_pi'].append((global_step, pi_metrics['pi_score']))
            step_metrics['train_surprise'].append((global_step, pi_metrics['surprise']))
            step_metrics['train_tau'].append((global_step, pi_metrics['tau']))
            
            # Log metrics for epoch summary
            epoch_summary['loss'].append(loss.item())
            epoch_summary['acc'].append(accuracy)
            epoch_summary['pi'].append(pi_metrics['pi_score'])
            epoch_summary['surprise'].append(pi_metrics['surprise'])
            epoch_summary['tau'].append(pi_metrics['tau'])

            global_step += 1
        
    # Averaging and logging epoch summaries
    avg_metrics = {key: sum(vals) / len(vals) if vals else 0 for key, vals in epoch_summary.items() if key not in ['consolidate', 'ignore', 'reject', 'surprise_values', 'decisions']}
    
    for key, avg_val in avg_metrics.items():
        epoch_metrics[f'train_{key}'].append((global_step - 1, avg_val))

    print(f"Train Epoch {epoch} Summary: Avg loss: {avg_metrics['loss']:.4f}, Avg Accuracy: {avg_metrics['acc']:.2f}%, Avg PI: {avg_metrics['pi']:.4f}, Avg Surprise: {avg_metrics['surprise']:.4f}, Avg Tau: {avg_metrics['tau']:.4f}")
    
    if use_gbp:
        consolidate_count = len(epoch_summary['consolidate'])
        ignore_count = len(epoch_summary['ignore'])
        reject_count = len(epoch_summary['reject'])
        total_decisions = consolidate_count + ignore_count + reject_count
        if total_decisions > 0:
            print(f"Decision Stats: Consolidate: {100*consolidate_count/total_decisions:.1f}%, Ignore: {100*ignore_count/total_decisions:.1f}%, Reject: {100*reject_count/total_decisions:.1f}%")
        return global_step, epoch_summary['surprise_values'], epoch_summary['decisions']
    
    return global_step

def validate(model, device, val_loader, loss_fn, pi_monitor, dataset_name="Validation"):
    model.eval()
    total_loss, correct = 0, 0
    all_pi_scores, all_surprises, all_taus = [], [], []

    for data, target in val_loader:
        data, target = data.to(device), target.to(device)
        
        # Enable gradients for PI calculation
        with torch.enable_grad():
            output = model(data)
            logits = output[0] if isinstance(output, tuple) else output
            loss_epsilon = loss_fn(logits, target)
            
            model.zero_grad()
            loss_epsilon.backward()
            
            pi_metrics = pi_monitor.calculate(model, loss_epsilon, logits)
            all_pi_scores.append(pi_metrics['pi_score'])
            all_surprises.append(pi_metrics['surprise'])
            all_taus.append(pi_metrics['tau'])

        # No-grad context for accuracy and loss accumulation
        with torch.no_grad():
            total_loss += loss_epsilon.item()
            pred = logits.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    avg_loss = total_loss / len(val_loader)
    accuracy = 100. * correct / len(val_loader.dataset)
    avg_pi = sum(all_pi_scores) / len(all_pi_scores) if all_pi_scores else 0
    avg_surprise = sum(all_surprises) / len(all_surprises) if all_surprises else 0
    avg_tau = sum(all_taus) / len(all_taus) if all_taus else 0

    print(f"{dataset_name} set: Avg loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%, Avg PI: {avg_pi:.4f}, Avg Surprise: {avg_surprise:.4f}, Avg Tau: {avg_tau:.4f}")
    return avg_loss, accuracy, avg_pi, avg_surprise, avg_tau
