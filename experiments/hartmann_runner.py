#!/usr/bin/env python3
from typing import Callable

import os
import sys
import torch
from botorch.acquisition.analytic import PosteriorMean
from botorch.settings import debug
from botorch.test_functions.synthetic import Hartmann
from torch import Tensor

torch.set_default_dtype(torch.float64)
torch.autograd.set_detect_anomaly(False)
debug._set_state(False)

script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
print(script_dir[:-12])
sys.path.append(script_dir[:-12])

from src.bax.alg.evolution_strategies import EvolutionStrategies
from src.experiment_manager import experiment_manager
from src.performance_metrics import compute_obj_val_at_max_post_mean


# Objective function
input_dim = 6


def obj_func(X: Tensor) -> Tensor:
    hartmann = Hartmann(dim=input_dim)
    objective_X = -hartmann.evaluate_true(X)
    return objective_X


# Set algorithm details
n_dim = 6
domain = [[0, 1]] * n_dim
init_x = [[0.0] * n_dim]

algo_params = {
    "n_generation": 50,
    "n_population": 10,
    "samp_str": "mut",
    "opt_mode": "min",
    "init_x": init_x[0],
    "domain": domain,
    "normal_scale": 0.05,
    "keep_frac": 0.3,
    "crop": False,
    "opt_mode": "max",
    #'crop': True,
}
algo = EvolutionStrategies(algo_params)


def algo_exe(obj_func: Callable) -> Tensor:
    _, output = algo.run_algorithm_on_f(obj_func)
    return output


def obj_val_at_max_post_mean(
    obj_func: Callable, posterior_mean_func: PosteriorMean
) -> Tensor:
    return compute_obj_val_at_max_post_mean(obj_func, posterior_mean_func, input_dim)


performance_metrics = {
    "Objective value at maximizer of the posterior mean": obj_val_at_max_post_mean
}

# Policies
policy = "ps"

# Run experiment
if len(sys.argv) == 3:
    first_trial = int(sys.argv[1])
    last_trial = int(sys.argv[2])
elif len(sys.argv) == 2:
    first_trial = int(sys.argv[1])
    last_trial = int(sys.argv[1])

experiment_manager(
    problem="hartmann",
    obj_func=obj_func,
    algo_exe=algo_exe,
    performance_metrics=performance_metrics,
    input_dim=input_dim,
    noise_type="noiseless",
    noise_level=0.0,
    policy=policy,
    batch_size=1,
    num_init_points=2 * (input_dim + 1),
    num_iter=100,
    first_trial=first_trial,
    last_trial=last_trial,
    restart=False,
)
