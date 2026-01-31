"""
Metaheuristic optimization algorithms.

This module provides:
- Snake Optimizer (for MSSO-FCM)
- Whale Optimization Algorithm (for WOAD3QN-RP)
- Genetic Algorithm (for PGAECR)
- NSGA-II sorting for multi-objective optimization
"""

import numpy as np
from typing import Callable, List, Tuple, Dict
import random


class SnakeOptimizer:
    """
    Multi-Strategy Snake Optimizer (MSSO) for clustering optimization.

    Implements three improvement strategies:
    1. Dynamic parameter updating
    2. Adaptive alpha mutation (Cauchy → Gaussian)
    3. Bi-directional search
    """

    def __init__(self, pop_size: int = 30, max_iter: int = 50, dim: int = 10,
                 lb: float = 0.0, ub: float = 1.0):
        """
        Initialize Snake Optimizer.

        Args:
            pop_size: Population size
            max_iter: Maximum iterations
            dim: Problem dimension
            lb: Lower bound
            ub: Upper bound
        """
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.dim = dim
        self.lb = lb
        self.ub = ub

        # Initialize population
        self.population = np.random.uniform(lb, ub, (pop_size, dim))
        self.fitness = np.zeros(pop_size)
        self.best_position = None
        self.best_fitness = float('inf')

    def update_parameters(self, t: int) -> Tuple[float, float, float]:
        """
        Strategy 1: Dynamic parameter updating.

        Args:
            t: Current iteration

        Returns:
            Tuple of (c1, c2, c3) parameters
        """
        T_max = self.max_iter

        c1 = 2 * np.exp(-(4 * t / T_max) ** 2)
        c2 = 2 * np.exp(-((t - T_max) / T_max) ** 2)
        c3 = 2 * (1 - t / T_max)

        return c1, c2, c3

    def adaptive_mutation(self, alpha: np.ndarray, t: int) -> np.ndarray:
        """
        Strategy 2: Adaptive alpha mutation.
        Cauchy mutation in early iterations, Gaussian in late iterations.

        Args:
            alpha: Current alpha values
            t: Current iteration

        Returns:
            Mutated alpha values
        """
        T_max = self.max_iter

        if t < T_max / 3:
            # Cauchy mutation
            mutation = np.random.standard_cauchy(alpha.shape)
        else:
            # Gaussian mutation
            mutation = np.random.randn(*alpha.shape)

        alpha_new = alpha + 0.1 * mutation
        return np.clip(alpha_new, self.lb, self.ub)

    def optimize(self, fitness_func: Callable) -> Tuple[np.ndarray, float]:
        """
        Run optimization.

        Args:
            fitness_func: Fitness function to minimize

        Returns:
            Tuple of (best_position, best_fitness)
        """
        # Evaluate initial population
        for i in range(self.pop_size):
            self.fitness[i] = fitness_func(self.population[i])

        best_idx = np.argmin(self.fitness)
        self.best_position = self.population[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]

        # Main optimization loop
        for t in range(self.max_iter):
            # Update parameters
            c1, c2, c3 = self.update_parameters(t)

            for i in range(self.pop_size):
                # Strategy 3: Bi-directional search
                if np.random.random() < 0.5:
                    # Exploration
                    rand_idx1 = np.random.randint(0, self.pop_size)
                    rand_idx2 = np.random.randint(0, self.pop_size)
                    new_pos = self.best_position + np.random.random() * (
                            self.population[rand_idx1] - self.population[rand_idx2]
                    )
                else:
                    # Exploitation
                    new_pos = self.best_position + c3 * (
                            self.best_position - self.population[i]
                    )

                # Apply adaptive mutation
                new_pos = self.adaptive_mutation(new_pos, t)

                # Boundary check
                new_pos = np.clip(new_pos, self.lb, self.ub)

                # Evaluate new position
                new_fitness = fitness_func(new_pos)

                # Update if better
                if new_fitness < self.fitness[i]:
                    self.population[i] = new_pos
                    self.fitness[i] = new_fitness

                    if new_fitness < self.best_fitness:
                        self.best_position = new_pos.copy()
                        self.best_fitness = new_fitness

        return self.best_position, self.best_fitness


class WhaleOptimizationAlgorithm:
    """
    Whale Optimization Algorithm (WOA) for hyperparameter tuning.
    Used in WOAD3QN-RP to optimize neural network hyperparameters.
    """

    def __init__(self, pop_size: int = 30, max_iter: int = 50, dim: int = 5,
                 lb: np.ndarray = None, ub: np.ndarray = None):
        """
        Initialize WOA.

        Args:
            pop_size: Population size
            max_iter: Maximum iterations
            dim: Problem dimension
            lb: Lower bounds array
            ub: Upper bounds array
        """
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.dim = dim
        self.lb = lb if lb is not None else np.zeros(dim)
        self.ub = ub if ub is not None else np.ones(dim)

        # Initialize population
        self.population = np.random.uniform(0, 1, (pop_size, dim))
        for i in range(dim):
            self.population[:, i] = self.lb[i] + self.population[:, i] * (self.ub[i] - self.lb[i])

        self.fitness = np.zeros(pop_size)
        self.best_position = None
        self.best_fitness = float('inf')

    def optimize(self, fitness_func: Callable) -> Tuple[np.ndarray, float]:
        """
        Run WOA optimization.

        Args:
            fitness_func: Fitness function to minimize

        Returns:
            Tuple of (best_position, best_fitness)
        """
        # Evaluate initial population
        for i in range(self.pop_size):
            self.fitness[i] = fitness_func(self.population[i])

        best_idx = np.argmin(self.fitness)
        self.best_position = self.population[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]

        # Main loop
        for t in range(self.max_iter):
            a = 2 - t * (2.0 / self.max_iter)  # Linearly decreased from 2 to 0

            for i in range(self.pop_size):
                r = np.random.random()
                A = 2 * a * r - a
                C = 2 * r
                l = np.random.uniform(-1, 1)
                p = np.random.random()

                if p < 0.5:
                    if abs(A) < 1:
                        # Encircling prey
                        D = abs(C * self.best_position - self.population[i])
                        new_pos = self.best_position - A * D
                    else:
                        # Search for prey (exploration)
                        rand_idx = np.random.randint(0, self.pop_size)
                        X_rand = self.population[rand_idx]
                        D = abs(C * X_rand - self.population[i])
                        new_pos = X_rand - A * D
                else:
                    # Spiral updating position
                    D_prime = abs(self.best_position - self.population[i])
                    new_pos = D_prime * np.exp(l) * np.cos(2 * np.pi * l) + self.best_position

                # Boundary check
                new_pos = np.clip(new_pos, self.lb, self.ub)

                # Evaluate
                new_fitness = fitness_func(new_pos)

                if new_fitness < self.fitness[i]:
                    self.population[i] = new_pos
                    self.fitness[i] = new_fitness

                    if new_fitness < self.best_fitness:
                        self.best_position = new_pos.copy()
                        self.best_fitness = new_fitness

        return self.best_position, self.best_fitness


class GeneticAlgorithm:
    """
    Genetic Algorithm for multi-objective optimization.
    Used in PGAECR with NSGA-II sorting.
    """

    def __init__(self, pop_size: int = 100, generations: int = 200,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1,
                 chromosome_length: int = 20):
        """
        Initialize GA.

        Args:
            pop_size: Population size
            generations: Number of generations
            crossover_rate: Crossover probability
            mutation_rate: Mutation probability
            chromosome_length: Length of chromosome
        """
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.chromosome_length = chromosome_length

        # Initialize population
        self.population = [
            np.random.randint(0, 100, chromosome_length) for _ in range(pop_size)
        ]

    def tournament_selection(self, fitness_values: List[float], tournament_size: int = 3) -> np.ndarray:
        """
        Tournament selection.

        Args:
            fitness_values: List of fitness values
            tournament_size: Tournament size

        Returns:
            Selected chromosome
        """
        indices = np.random.choice(len(self.population), tournament_size, replace=False)
        best_idx = indices[np.argmin([fitness_values[i] for i in indices])]
        return self.population[best_idx].copy()

    def two_point_crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Two-point crossover.

        Args:
            parent1: First parent
            parent2: Second parent

        Returns:
            Two offspring
        """
        if np.random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        point1 = np.random.randint(1, len(parent1) - 1)
        point2 = np.random.randint(point1 + 1, len(parent1))

        offspring1 = np.concatenate([parent1[:point1], parent2[point1:point2], parent1[point2:]])
        offspring2 = np.concatenate([parent2[:point1], parent1[point1:point2], parent2[point2:]])

        return offspring1, offspring2

    def mutate(self, chromosome: np.ndarray) -> np.ndarray:
        """
        Mutation operator.

        Args:
            chromosome: Chromosome to mutate

        Returns:
            Mutated chromosome
        """
        for i in range(len(chromosome)):
            if np.random.random() < self.mutation_rate:
                chromosome[i] = np.random.randint(0, 100)

        return chromosome


def fast_non_dominated_sort(objectives: np.ndarray) -> List[List[int]]:
    """
    NSGA-II fast non-dominated sorting.

    Args:
        objectives: Array of shape (pop_size, num_objectives)

    Returns:
        List of fronts (each front is a list of indices)
    """
    pop_size = objectives.shape[0]
    domination_counts = np.zeros(pop_size, dtype=int)
    dominated_solutions = [[] for _ in range(pop_size)]
    fronts = [[]]

    for i in range(pop_size):
        for j in range(pop_size):
            if i == j:
                continue

            # Check if i dominates j
            dominates = False
            dominated_by = False

            for k in range(objectives.shape[1]):
                if objectives[i, k] < objectives[j, k]:
                    dominates = True
                elif objectives[i, k] > objectives[j, k]:
                    dominated_by = True

            if dominates and not dominated_by:
                dominated_solutions[i].append(j)
            elif dominated_by and not dominates:
                domination_counts[i] += 1

        if domination_counts[i] == 0:
            fronts[0].append(i)

    # Build subsequent fronts
    i = 0
    while len(fronts[i]) > 0:
        next_front = []
        for p in fronts[i]:
            for q in dominated_solutions[p]:
                domination_counts[q] -= 1
                if domination_counts[q] == 0:
                    next_front.append(q)

        i += 1
        if len(next_front) > 0:
            fronts.append(next_front)
        else:
            break

    return fronts[:-1] if len(fronts) > 1 and len(fronts[-1]) == 0 else fronts


def calculate_crowding_distance(objectives: np.ndarray, front: List[int]) -> np.ndarray:
    """
    Calculate crowding distance for a front.

    Args:
        objectives: Array of objectives
        front: List of indices in the front

    Returns:
        Crowding distances for each individual
    """
    num_objectives = objectives.shape[1]
    distances = np.zeros(len(front))

    for m in range(num_objectives):
        # Sort by m-th objective
        sorted_indices = np.argsort([objectives[i, m] for i in front])

        # Boundary points have infinite distance
        distances[sorted_indices[0]] = float('inf')
        distances[sorted_indices[-1]] = float('inf')

        obj_min = objectives[front[sorted_indices[0]], m]
        obj_max = objectives[front[sorted_indices[-1]], m]

        if obj_max - obj_min == 0:
            continue

        # Calculate crowding distance
        for i in range(1, len(front) - 1):
            distances[sorted_indices[i]] += (
                    (objectives[front[sorted_indices[i + 1]], m] -
                     objectives[front[sorted_indices[i - 1]], m]) /
                    (obj_max - obj_min)
            )

    return distances
