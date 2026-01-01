# WSN-SDN Routing with Deep Reinforcement Learning

A comprehensive framework for evaluating routing algorithms in Wireless Sensor Networks using Software-Defined Networking principles and Deep Reinforcement Learning.

## Overview

This research implements and compares four routing algorithms for WSN:

1. **SPR** (Shortest Path Routing) - Baseline using Dijkstra's algorithm
2. **EAR** (Energy-Aware Routing) - Considers residual energy in routing decisions
3. **ALB** (Adaptive Load Balancing) - Multi-metric optimization with load balancing
4. **DRL-SDN** (Proposed Method) - Deep reinforcement learning with adaptive weights

## Key Features

- **Comprehensive Energy Modeling**: First Order Radio Energy Model
- **DRL Implementation**: Double DQN with experience replay
- **Adaptive Routing**: State-dependent weight adjustment
- **Extensive Metrics**: Lifetime, PDR, energy efficiency, fairness, etc.
- **Professional Visualization**: Detailed performance comparison plots

## Project Structure

```
fia/
├── src/
│   ├── config.py              # Configuration parameters
│   ├── models/
│   │   ├── node.py           # Sensor node implementation
│   │   ├── network.py        # SDN controller
│   │   └── drl_agent.py      # DRL agent (DQN)
│   ├── routing/
│   │   ├── base.py           # Base routing algorithm
│   │   ├── spr.py            # Shortest Path Routing
│   │   ├── ear.py            # Energy-Aware Routing
│   │   ├── alb.py            # Adaptive Load Balancing
│   │   └── drl_sdn.py        # DRL-SDN (Proposed)
│   ├── simulation/
│   │   └── simulator.py      # Network simulator
│   └── visualization/
│       └── plotter.py        # Results visualization
├── results/                   # Output directory
├── main.py                    # Main simulation runner
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the complete simulation:

```bash
python main.py
```

This will:
1. Deploy a WSN with configured parameters
2. Evaluate all routing algorithms
3. Generate comprehensive performance metrics
4. Create visualization plots
5. Save results to JSON

## Results

The simulation generates:

- `results.json` - Complete numerical results
- `network_topology.png` - Network visualization
- `comparative_metrics.png` - Algorithm comparison
- `temporal_evolution.png` - Metric evolution over time
- `improvement_analysis.png` - Improvement percentages
- `energy_analysis.png` - Energy consumption details

## Configuration

Edit `src/config.py` to adjust:

- Network parameters (nodes, area, communication range)
- Energy model parameters
- DRL hyperparameters
- Simulation settings

## Key Metrics

- **Network Lifetime**: Rounds until network partition
- **FND**: First Node Death
- **HND**: Half Nodes Death
- **PDR**: Packet Delivery Ratio
- **Energy Efficiency**: Packets per Joule
- **Fairness Index**: Jain's fairness index

## Research Contributions

1. **Adaptive Weight Mechanism**: Dynamic adjustment based on network state
2. **DRL-based Routing**: Learns optimal policies through experience
3. **Multi-metric Optimization**: Balances energy, distance, and load
4. **Critical Node Protection**: Preserves nodes with low energy

## Citation

If you use this code in your research, please cite:

```
@article{wsn_drl_sdn,
  title={Deep Reinforcement Learning for Energy-Efficient Routing in WSN-SDN},
  year={2026}
}
```

## License

Academic and research use only.
