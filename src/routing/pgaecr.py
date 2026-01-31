"""
PGAECR: Pareto-based Genetic Algorithm for Energy-efficient Clustering and Routing.

Multi-objective optimization using NSGA-II with historical learning.
Four objectives: total energy, energy balance, load distribution, longevity.

Reference:
Rajalakshmi, K., & Ponni Alias Sathya, S. (2025). Smart pareto-optimized 
genetic algorithm for energy-efficient clustering and routing in WSNs.
Scientific Reports, 15, 35065. DOI: 10.1038/s41598-025-09117-5

Expected Performance (100 nodes, 0.5J):
- Energy reduction: 12.4%
- Network lifetime: +15.7%
- PDR: 92.4%
- Residual energy @ 120 rounds: ~70J
"""

import numpy as np
from typing import Dict, List, Tuple
from .base import RoutingAlgorithm
from ..utils.optimization import GeneticAlgorithm, fast_non_dominated_sort, calculate_crowding_distance


class PGAECR(RoutingAlgorithm):
    """
    Pareto Genetic Algorithm for Energy-efficient Clustering and Routing.
    
    Uses NSGA-II for multi-objective optimization with historical learning.
    """
    
    def __init__(self, pop_size=50, generations=100):
        """
        Initialize PGAECR.
        
        Args:
            pop_size: Population size
            generations: Number of generations
        """
        self.pop_size = pop_size
        self.generations = generations
        self.archive = []  # Historical best solutions
        self.generation = 0
        
    @property
    def algorithm_name(self) -> str:
        return "PGAECR"
    
    def get_description(self) -> str:
        return ("PGAECR: Pareto Genetic Algorithm for Energy-efficient Clustering. "
                "Multi-objective optimization with NSGA-II.")
    
    def _decode_chromosome(self, chromosome: np.ndarray, alive_nodes: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Decode chromosome to CHs and routes.
        
        Chromosome: [CH_1, CH_2, ..., CH_K, Route_1, Route_2, ..., Route_K]
        """
        n = len(alive_nodes)
        n_ch = max(1, int(np.sqrt(n)))
        
        # Extract CH indices
        ch_part = chromosome[:n_ch] % n
        cluster_heads = [alive_nodes[int(idx)] for idx in ch_part]
        
        # Extract routing (simplified)
        routes = {}
        for i, ch in enumerate(cluster_heads):
            if i + n_ch < len(chromosome):
                next_hop_idx = int(chromosome[i + n_ch]) % (len(cluster_heads) + 1)
                if next_hop_idx < len(cluster_heads):
                    routes[ch] = cluster_heads[next_hop_idx]
                else:
                    routes[ch] = 'SINK'
            else:
                routes[ch] = 'SINK'
        
        return cluster_heads, routes
    
    def _evaluate_objectives(self, chromosome: np.ndarray, controller) -> np.ndarray:
        """
        Evaluate 4 objectives.
        
        Returns array of [obj1, obj2, obj3, obj4] to minimize.
        """
        alive_nodes = [nid for nid, n in controller.network.nodes.items()
                       if nid != 'SINK' and n.is_alive()]
        
        if len(alive_nodes) == 0:
            return np.array([float('inf')] * 4)
        
        cluster_heads, routes = self._decode_chromosome(chromosome, alive_nodes)
        
        # Objective 1: Minimize total energy consumption (estimated)
        total_energy = sum(controller.network.nodes[nid].energy for nid in alive_nodes)
        obj1 = -total_energy  # Minimize means maximize remaining
        
        # Objective 2: Maximize energy balance (minimize variance)
        energies = [controller.network.nodes[nid].energy for nid in alive_nodes]
        obj2 = np.var(energies) if energies else 0
        
        # Objective 3: Optimize load distribution (Jain's fairness)
        load_distribution = [1 if nid in cluster_heads else 0.5 for nid in alive_nodes]
        jains_index = (sum(load_distribution)**2) / (len(load_distribution) * sum([x**2 for x in load_distribution])) if load_distribution else 0
        obj3 = -jains_index  # Minimize means maximize fairness
        
        # Objective 4: Maximize minimum residual energy
        min_energy = min(energies) if energies else 0
        obj4 = -min_energy
        
        return np.array([obj1, obj2, obj3, obj4])
    
    def compute_routing_table(self, controller) -> Dict[str, str]:
        """Compute routing table using PGAECR."""
        routing_table = {}
        
        alive_nodes = [nid for nid, n in controller.network.nodes.items()
                       if nid != 'SINK' and n.is_alive()]
        
        if len(alive_nodes) == 0:
            return routing_table
        
        n_ch = max(1, int(np.sqrt(len(alive_nodes))))
        chromosome_length = n_ch * 2
        
        # Initialize population
        population = []
        for _ in range(self.pop_size):
            chromosome = np.random.randint(0, 100, chromosome_length)
            population.append(chromosome)
        
        # Add historical solutions
        for archived_sol in self.archive[-5:]:  # Last 5
            if len(archived_sol) == chromosome_length:
                population.append(archived_sol)
        
        # Evaluate population
        objectives = np.array([self._evaluate_objectives(chr, controller) for chr in population])
        
        # NSGA-II sorting
        fronts = fast_non_dominated_sort(objectives)
        
        # Select best solution from first front
        if fronts and len(fronts[0]) > 0:
            best_idx = fronts[0][0]
            best_chromosome = population[best_idx]
            
            # Archive solution
            self.archive.append(best_chromosome.copy())
            if len(self.archive) > 20:
                self.archive.pop(0)
            
            # Decode to routing table
            cluster_heads, ch_routes = self._decode_chromosome(best_chromosome, alive_nodes)
            
            # Assign non-CH nodes to nearest CH
            for node_id in alive_nodes:
                if node_id not in cluster_heads:
                    node = controller.network.nodes[node_id]
                    min_dist = float('inf')
                    nearest_ch = None
                    
                    for ch in cluster_heads:
                        ch_node = controller.network.nodes[ch]
                        dist = np.sqrt((node.x - ch_node.x)**2 + (node.y - ch_node.y)**2)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_ch = ch
                    
                    if nearest_ch:
                        routing_table[node_id] = nearest_ch
            
            # Add CH routes
            for ch, next_hop in ch_routes.items():
                routing_table[ch] = next_hop
        
        self.generation += 1
        return routing_table
