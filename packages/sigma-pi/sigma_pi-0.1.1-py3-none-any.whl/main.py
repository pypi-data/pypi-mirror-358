import torch
import math
from typing import Dict, List

def get_surprise_from_grads(gradients: List[torch.Tensor]) -> float:
    with torch.no_grad():
        total_norm_sq = sum(p.norm(2).item() ** 2 for p in gradients if p is not None)
    return math.sqrt(total_norm_sq)

def get_entropy_from_logits(logits: torch.Tensor) -> float:
    probs = torch.softmax(logits, dim=-1)
    entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)
    return entropy.mean().item()

def calculate_pi(
    epsilon: float,
    tau: float,
    surprise: float,
    alpha: float = 1.0,
    gamma: float = 0.5
) -> Dict[str, float]:
    normalized_error = epsilon / (tau + 1e-9)
    cognitive_cost = (1 - gamma) * normalized_error + gamma * surprise
    pi_score = math.exp(-alpha * cognitive_cost)

    return {
        "pi_score": pi_score,
        "normalized_error": normalized_error,
        "cognitive_cost": cognitive_cost,
        "epsilon": epsilon,
        "tau": tau,
        "surprise": surprise,
    }

class SigmaPI:
    def __init__(self, alpha: float = 1.0, gamma: float = 0.5):
        self.alpha = alpha
        self.gamma = gamma

    def calculate(
        self,
        model: torch.nn.Module,
        loss_epsilon: torch.Tensor,
        logits: torch.Tensor
    ) -> Dict[str, float]:
        model_grads = [p.grad for p in model.parameters() if p.grad is not None]
        if not model_grads:
            raise ValueError("No gradients found. Please call loss.backward() before calculate().")

        epsilon = loss_epsilon.item()
        model_grads = [p.grad for p in model.parameters() if p.grad is not None]

        tau = get_entropy_from_logits(logits)
        surprise = get_surprise_from_grads(model_grads)

        pi_metrics = calculate_pi(
            epsilon=epsilon,
            tau=tau,
            surprise=surprise,
            alpha=self.alpha,
            gamma=self.gamma
        )
        return pi_metrics
