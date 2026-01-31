# 🗺️ ROADMAP جامع پروژه بازسازی الگوریتم‌های مسیریابی WSN-SDN

**تاریخ شروع**: 2026-01-31
**وضعیت**: در حال اجرا
**هدف**: پیاده‌سازی 6 الگوریتم پیشرفته از مقالات 2023-2026

---

## 📊 تحلیل ساختار فعلی پروژه

### الگوریتم‌های موجود (قابل حذف):
1. ✅ **SPR** (Shortest Path Routing) - `src/routing/spr.py` (84 خط)
2. ✅ **EAR** (Energy Aware Routing) - `src/routing/ear.py` (127 خط)
3. ✅ **ALB** (Adaptive Load Balancing) - `src/routing/alb.py` (153 خط)

### الگوریتم‌های نگهداری شده:
- **DRLSDNRouting** - `src/routing/drl_sdn.py` (380 خط) - به عنوان baseline
- **CDRL Advanced** - `src/routing/cdrl_advanced.py` (345 خط) - احتمالاً مفید

### کامپوننت‌های زیرساختی:
- ✅ `src/routing/base.py` - کلاس پایه `RoutingAlgorithm`
- ✅ `src/models/network.py` - مدل شبکه و SDN Controller
- ✅ `src/models/node.py` - مدل گره حسگر
- ✅ `src/simulation/simulator.py` - شبیه‌ساز اصلی
- ✅ `src/visualization/plotter.py` - رسم نمودارها
- ✅ `src/config.py` - پیکربندی شبیه‌سازی

---

## 🎯 اهداف پروژه

### فاز 1: پاکسازی و آماده‌سازی (1 روز)
- [x] تحلیل ساختار فعلی
- [ ] حذف فایل‌های قدیمی (SPR, EAR, ALB)
- [ ] ایجاد ساختار پوشه جدید
- [ ] آماده‌سازی utility modules

### فاز 2: پیاده‌سازی الگوریتم‌های اولویت 1 (5-7 روز)
1. **NN_ILEACH** (Neural Network Improved LEACH)
   - سادگی نسبی برای شروع
   - نیاز به شبکه عصبی ساده (2 لایه مخفی)
   - زمان تخمینی: 1-2 روز

2. **DOS-RL** (Dynamic Objective Selection with RL)
   - Q-learning استاندارد
   - 3 هدف همبسته
   - زمان تخمینی: 2 روز

3. **MSSO-FCM** (Multi-Strategy Snake Optimizer + FCM)
   - بهینه‌سازی متاهیوریستیک
   - خوشه‌بندی فازی
   - زمان تخمینی: 2-3 روز

### فاز 3: پیاده‌سازی الگوریتم‌های اولویت 2 (4-6 روز)
4. **PGAECR** (Pareto GA for Energy-efficient Clustering)
   - الگوریتم ژنتیک چندهدفه
   - NSGA-II sorting
   - زمان تخمینی: 2-3 روز

5. **WOAD3QN-RP** (WOA + Dueling Double DQN)
   - DRL پیشرفته
   - ترکیب با بهینه‌سازی
   - زمان تخمینی: 2-3 روز

### فاز 4: پیاده‌سازی الگوریتم پیشرفته (3-5 روز)
6. **GN-DQN** (Graph Neural Network + DQN)
   - پیچیده‌ترین الگوریتم
   - نیاز به GNN layers (GAT, GCN)
   - زمان تخمینی: 3-5 روز

### فاز 5: توسعه سناریوهای آزمایش (3-4 روز)
- [ ] سناریو 1: مقایسه طول عمر شبکه
- [ ] سناریو 2: مقایسه کارایی انرژی
- [ ] سناریو 3: مقایسه کیفیت سرویس (QoS)
- [ ] سناریو 4: تحلیل مقیاس‌پذیری
- [ ] سناریو 5: تحلیل حساسیت پارامترها
- [ ] سناریو 6: مقایسه با Benchmarks علمی

### فاز 6: اجرای شبیه‌سازی‌ها (5-10 روز)
- [ ] اجرای تمام سناریوها با 10 run
- [ ] جمع‌آوری نتایج در CSV/JSON
- [ ] اعتبارسنجی نتایج با مقالات

### فاز 7: تصویرسازی و گزارش‌دهی (3-4 روز)
- [ ] تولید 10+ نمودار با کیفیت publication
- [ ] نوشتن گزارش جامع (20+ صفحه)
- [ ] ایجاد executive summary
- [ ] مستندسازی کامل API

---

## 📁 ساختار پوشه هدف

```
fia/
├── src/
│   ├── routing/
│   │   ├── base.py                    [موجود - نگهداری]
│   │   ├── drl_sdn.py                 [موجود - نگهداری]
│   │   ├── cdrl_advanced.py           [موجود - نگهداری]
│   │   │
│   │   ├── nn_ileach.py               [جدید - الگوریتم 1]
│   │   ├── dos_rl.py                  [جدید - الگوریتم 2]
│   │   ├── msso_fcm.py                [جدید - الگوریتم 3]
│   │   ├── pgaecr.py                  [جدید - الگوریتم 4]
│   │   ├── woad3qn_rp.py              [جدید - الگوریتم 5]
│   │   ├── gn_dqn.py                  [جدید - الگوریتم 6]
│   │   │
│   │   ├── baselines/                 [جدید - پوشه]
│   │   │   ├── leach.py               [baseline 1]
│   │   │   ├── pegasis.py             [baseline 2]
│   │   │   └── ospf.py                [baseline 3]
│   │   │
│   │   └── __init__.py                [به‌روزرسانی]
│   │
│   ├── utils/                          [جدید/توسعه]
│   │   ├── neural_networks.py         [شبکه‌های عصبی مشترک]
│   │   ├── graph_utils.py             [ابزارهای گراف برای GN-DQN]
│   │   ├── optimization.py            [متاهیوریستیک‌ها]
│   │   ├── clustering.py              [الگوریتم‌های خوشه‌بندی]
│   │   ├── fuzzy_logic.py             [منطق فازی]
│   │   └── metrics.py                 [محاسبه معیارها]
│   │
│   ├── models/                         [موجود - نگهداری]
│   ├── simulation/                     [موجود - نگهداری]
│   ├── visualization/                  [توسعه]
│   └── config.py                       [موجود - نگهداری]
│
├── experiments/                        [جدید - پوشه]
│   ├── 1_lifetime_comparison.py
│   ├── 2_energy_efficiency.py
│   ├── 3_qos_analysis.py
│   ├── 4_scalability_test.py
│   ├── 5_sensitivity_analysis.py
│   └── 6_benchmark_validation.py
│
├── results/                            [توسعه]
│   ├── tables/                         [CSV files]
│   ├── plots/                          [نمودارها]
│   └── raw_data/                       [JSON files]
│
├── reports/                            [جدید - پوشه]
│   ├── comprehensive_report.md
│   ├── executive_summary.pdf
│   └── benchmarking_analysis.pdf
│
├── docs/                               [جدید - پوشه]
│   ├── API_documentation.md
│   ├── User_Guide.md
│   ├── Algorithm_Details.md
│   └── Installation_Guide.md
│
├── tests/                              [جدید - پوشه]
│   ├── test_algorithms.py
│   ├── test_simulation.py
│   └── test_metrics.py
│
├── main.py                             [به‌روزرسانی]
├── requirements.txt                    [به‌روزرسانی]
├── README.md                           [بازنویسی کامل]
└── PROJECT_ROADMAP.md                  [این فایل]
```

---

## 📋 جزئیات پیاده‌سازی هر الگوریتم

### 1️⃣ NN_ILEACH (اولویت: بالا)

**منبع**: Scientific Reports, 2024, DOI: 10.1038/s41598-024-75904-1

**ویژگی‌های کلیدی**:
- شبکه عصبی برای انتخاب Cluster Head
- معماری: 5 → 5 → 5 → 1 neuron
- Activation: tanh
- Training: 85/15 split, 1000 epochs

**State Features** (5 ویژگی):
1. Residual energy (normalized)
2. Distance to base station
3. Node degree
4. Average distance to neighbors
5. Previous CH count

**نتایج مورد انتظار**:
- Network lifetime: 11,361 rounds (vs 505 LEACH)
- Throughput: +30%
- PDR: +25%
- Energy: -40%

**فایل‌های مورد نیاز**:
- `src/routing/nn_ileach.py` (300-400 خط)
- `src/utils/neural_networks.py` (helper functions)
- `src/utils/clustering.py` (TDMA scheduling)

---

### 2️⃣ DOS-RL (اولویت: بالا)

**منبع**: Sensors, 2023, DOI: 10.3390/s23208435

**ویژگی‌های کلیدی**:
- Multi-objective Q-learning
- 3 Q-tables همزمان
- Dynamic weight adjustment
- SDN integration

**Objectives**:
1. Energy Conservation (Q_energy)
2. Load Balancing (Q_load)
3. Link Quality (Q_link)

**Combined Q-value**:
```
Q_total(s,a) = w1×Q_energy + w2×Q_load + w3×Q_link
```

**Dynamic Weights**:
- Low energy (< 30%): w1=0.6, w2=0.2, w3=0.2
- High congestion (> 70%): w1=0.2, w2=0.6, w3=0.2
- Poor link quality (< 90%): w1=0.2, w2=0.2, w3=0.6
- Normal: w1=w2=w3=0.33

**نتایج مورد انتظار**:
- PDR improvement: 10-20% vs OSPF
- End-to-end delay: Significant reduction
- Energy balance: Jain's index > 0.85

**فایل‌های مورد نیاز**:
- `src/routing/dos_rl.py` (400-500 خط)

---

### 3️⃣ MSSO-FCM (اولویت: بالا)

**منبع**: Scientific Reports, 2024, DOI: 10.1038/s41598-024-66703-9

**ویژگی‌های کلیدی**:
- Multi-Strategy Snake Optimizer
- Fuzzy C-Means clustering
- Minimum Spanning Tree routing
- 3 improvement strategies

**Fitness Function**:
```
F = w1×E_residual + w2×(1/d_BS) + w3×(1/d_intra) + w4×N_neighbors
Weights: [0.4, 0.2, 0.2, 0.2]
```

**نتایج مورد انتظار**:
- Energy reduction: 26.64% minimum
- Network lifetime: +25.84%
- Stability period: +52.43%
- Throughput: +40.99%

**فایل‌های مورد نیاز**:
- `src/routing/msso_fcm.py` (500-600 خط)
- `src/utils/optimization.py` (Snake Optimizer)
- `src/utils/fuzzy_logic.py` (FCM implementation)

---

### 4️⃣ PGAECR (اولویت: متوسط)

**منبع**: Scientific Reports, 2025, DOI: 10.1038/s41598-025-09117-5

**ویژگی‌های کلیدی**:
- Pareto-based Genetic Algorithm
- 4 simultaneous objectives
- NSGA-II sorting
- Historical learning

**Objectives**:
1. Minimize total energy consumption
2. Maximize residual energy balance
3. Optimize load distribution
4. Maximize network longevity

**Chromosome Encoding**:
```
[CH_1, CH_2, ..., CH_K, Route_1, Route_2, ..., Route_K]
```

**نتایج مورد انتظار**:
- Energy reduction: 12.4%
- Network lifetime: +15.7%
- PDR: 92.4%
- Residual energy @ round 120: ~70J

**فایل‌های مورد نیاز**:
- `src/routing/pgaecr.py` (600-700 خط)
- `src/utils/optimization.py` (GA operators)

---

### 5️⃣ WOAD3QN-RP (اولویت: متوسط)

**منبع**: Expert Systems with Applications, 2024, DOI: S0957417423035911

**ویژگی‌های کلیدی**:
- Dueling Double Deep Q-Network
- Whale Optimization Algorithm
- Experience replay buffer
- Target network

**D3QN Architecture**:
```
Input → FC(256) → FC(128) → [Value Stream(64→1), Advantage Stream(64→actions)]
Output: Q(s,a) = V(s) + [A(s,a) - mean(A)]
```

**WOA Integration**:
- Optimize hyperparameters
- Population size: 30
- Max iterations: 50

**نتایج مورد انتظار**:
- Network lifetime (FND): > 1500 rounds
- PDR: > 99%
- Energy efficiency: > 2100 packets/J
- Convergence: < 50 episodes

**فایل‌های مورد نیاز**:
- `src/routing/woad3qn_rp.py` (700-800 خط)
- `src/utils/neural_networks.py` (Dueling DQN)
- `src/utils/optimization.py` (WOA)

---

### 6️⃣ GN-DQN (اولویت: پیشرفته)

**منبع**: Future Generation Computer Systems, 2024, DOI: S0167739X23003497

**ویژگی‌های کلیدی**:
- Graph Neural Network layers
- Graph Attention (GAT)
- Graph Convolution (GCN)
- Deep Q-Network

**GNN Architecture**:
```
Layer 1: GAT (attention-based aggregation)
Layer 2: GCN (normalized aggregation)
Layer 3: Global Pooling → 128-dim graph embedding
```

**DQN Integration**:
```
State: [h_graph(128), h_current_node(5), packet_info(3)] = 136 dims
DQN: 136 → 256 → 128 → 64 → actions
```

**نتایج مورد انتظار**:
- Generalization across topologies
- Long-term revenue optimization
- Path selection optimality

**فایل‌های مورد نیاز**:
- `src/routing/gn_dqn.py` (800-1000 خط)
- `src/utils/graph_utils.py` (GAT, GCN layers)
- `src/utils/neural_networks.py` (DQN)

---

## 🔧 Utility Modules مورد نیاز

### 1. `src/utils/neural_networks.py`
```python
- SimpleFeedForward (for NN_ILEACH)
- DuelingDQN (for WOAD3QN-RP)
- StandardDQN (for GN-DQN)
- ExperienceReplayBuffer
- TargetNetworkUpdater
```

### 2. `src/utils/graph_utils.py`
```python
- GraphAttentionLayer (GAT)
- GraphConvolutionLayer (GCN)
- GlobalPooling
- GraphBuilder (from Network)
```

### 3. `src/utils/optimization.py`
```python
- SnakeOptimizer (for MSSO-FCM)
- WhaleOptimizationAlgorithm (for WOAD3QN-RP)
- GeneticAlgorithm (for PGAECR)
- NSGA2Sorting (Pareto front)
```

### 4. `src/utils/clustering.py`
```python
- FuzzyCMeans (for MSSO-FCM)
- KruskalMST (for MSSO-FCM)
- TDMAScheduler (for NN_ILEACH)
- ClusterHeadSelector
```

### 5. `src/utils/fuzzy_logic.py`
```python
- FuzzyMembershipCalculator
- FuzzyInferenceSystem
```

### 6. `src/utils/metrics.py`
```python
- calculate_jains_fairness_index
- calculate_pdr
- calculate_energy_efficiency
- calculate_stability_period
- calculate_variance
```

---

## 📊 سناریوهای آزمایش جامع

### سناریو 1: Lifetime Comparison
```python
# experiments/1_lifetime_comparison.py

Configuration:
- Nodes: 100
- Area: 200×200 m
- Initial Energy: 0.5 J
- Rounds: 3000
- Runs: 10 (different seeds)

Algorithms:
- NN_ILEACH
- DOS-RL
- MSSO-FCM
- PGAECR
- WOAD3QN-RP
- GN-DQN
- LEACH (baseline)
- PEGASIS (baseline)

Metrics:
- FND, HND, LND
- Stability Period
- Instability Period
- Alive Nodes vs Rounds

Output:
- CSV: lifetime_comparison.csv
- Plots:
  * Fig1_Lifetime_Comparison.png
  * Fig2_Alive_Nodes_Over_Time.png
```

### سناریو 2: Energy Efficiency
```python
# experiments/2_energy_efficiency.py

Configuration:
- Nodes: 100
- Rounds: 2000
- Focus: Energy analysis

Metrics:
- Total energy consumption
- Energy efficiency (packets/J)
- Energy per packet
- Jain's fairness index
- Energy variance
- Hotspot formation

Output:
- CSV: energy_efficiency.csv
- Plots:
  * Fig3_Energy_Consumption.png
  * Fig4_Energy_Efficiency_Timeline.png
  * Fig5_Fairness_Index_Evolution.png
  * Fig6_Energy_Heatmaps.png
```

### سناریو 3: QoS Analysis
```python
# experiments/3_qos_analysis.py

Configuration:
- Traffic loads: 10, 20, 30, 40, 50 pkts/round
- Rounds: 1500

Metrics:
- PDR
- End-to-end delay
- Throughput
- Hop count
- Packet loss rate
- Latency jitter

Output:
- CSV: qos_metrics.csv
- Plots:
  * Fig7_PDR_vs_Traffic_Load.png
  * Fig8_Delay_Distribution.png
  * Fig9_Throughput_Comparison.png
```

### سناریو 4: Scalability Test
```python
# experiments/4_scalability_test.py

Configuration:
- Node counts: 50, 100, 150, 200, 250
- Area: proportional (sqrt(N) × base)
- Rounds: 1000

Metrics:
- FND vs network size
- Computational time
- Memory usage
- Convergence speed
- Scalability coefficient

Output:
- CSV: scalability_results.csv
- Plots:
  * Fig10_Scalability_Analysis.png
  * Fig11_Computational_Complexity.png
```

### سناریو 5: Sensitivity Analysis
```python
# experiments/5_sensitivity_analysis.py

Parameters to vary:
1. Initial Energy: 0.25, 0.5, 0.75, 1.0 J
2. Comm Range: 30, 40, 50, 60, 70 m
3. Packet Size: 500, 1000, 2000, 4000 bits
4. BS Location: Center, Corner, Edge
5. Node Density: Sparse, Medium, Dense

Output:
- CSV: sensitivity_results.csv
- Plots:
  * Fig12_Sensitivity_Heatmaps.png
  * Fig13_Parameter_Impact.png
```

### سناریو 6: Benchmark Validation
```python
# experiments/6_benchmark_validation.py

Benchmarks from literature:
1. LEACH baseline (~500-700 FND)
2. PEGASIS (~1.5× LEACH)
3. NN_ILEACH (reported: 11,361 FND)
4. MSSO-FCM (reported: +25.84% lifetime)
5. DOS-RL (reported: +10-20% PDR vs OSPF)

Validation:
- Replicate exact configurations
- Compare our results vs published
- Calculate % error
- Statistical significance (t-test)

Output:
- CSV: benchmark_validation.csv
- Report: benchmarking_analysis.md
```

---

## 📈 نمودارهای مورد نیاز (10+ plots)

### Publication-Quality Plots

1. **Network Lifetime Comparison** (Bar chart)
   - FND, HND, LND for 8 algorithms
   - Grouped bars with error bars
   - Color-blind friendly palette

2. **Energy Consumption Evolution** (Line chart)
   - Average residual energy vs rounds
   - 8 lines for 8 algorithms
   - Confidence intervals

3. **Packet Delivery Ratio Over Time** (Line chart)
   - PDR for each algorithm
   - Show degradation point

4. **Energy Efficiency Comparison** (Bar chart)
   - Packets/Joule
   - Sorted from highest to lowest
   - Show % improvement vs LEACH

5. **Fairness Index Evolution** (Line chart)
   - Jain's Index vs rounds
   - Highlight optimal range (>0.8)

6. **QoS Multi-Metric Comparison** (Radar/Spider chart)
   - Axes: FND, PDR, Efficiency, Fairness, Delay, Throughput
   - Overlay 6 new algorithms

7. **Scalability Analysis** (Multi-line chart)
   - FND vs Number of Nodes
   - 8 lines for 8 algorithms
   - Log scale if needed

8. **Energy Distribution Heatmap** (Heatmap)
   - Residual energy at key rounds
   - Show hotspot formation
   - One per algorithm

9. **Statistical Comparison Box Plots** (Box plot)
   - FND from 10 runs
   - Show median, quartiles, outliers

10. **Convergence Analysis** (Line chart)
    - Reward per episode (for RL algorithms)
    - Compare WOAD3QN-RP, DOS-RL, GN-DQN

11. **Performance Heatmap** (Heatmap)
    - Algorithm × Metric
    - Normalized scores 0-1
    - Identify best algorithm per metric

12. **Trade-off Analysis** (Scatter plot)
    - Energy Efficiency vs Network Lifetime
    - Each point = one algorithm
    - Pareto frontier highlighted

**Plot Settings**:
- DPI: 300
- Font: Arial, size 12
- Grid: Minor grid
- Legend: Outside plot area
- Export: PNG, PDF, SVG

---

## 🔍 معیارهای ارزیابی جامع

### 1. Network Lifetime Metrics
```python
FND = First Node Death (round number)
HND = Half Nodes Death (round number)
LND = Last Node Death (round number)
Stability Period = FND
Instability Period = LND - FND

Goal: Maximize FND, HND, LND
```

### 2. Energy Metrics
```python
Total Energy Consumed = Σ(E_tx + E_rx)
Energy Efficiency = Total Packets Delivered / Total Energy Consumed
Energy per Packet = Total Energy / Packets Delivered
Energy Variance = Var(E_residual_1, ..., E_residual_N)

Goal: Minimize consumption, Maximize efficiency
```

### 3. QoS Metrics
```python
PDR = Packets Delivered / Packets Sent × 100%
Average Delay = Σ(delay_i) / N
Throughput = Packets to Sink / Time
Hop Count = Average hops per packet
Packet Loss Rate = 100% - PDR

Goal: PDR > 95%, Low delay, High throughput
```

### 4. Fairness Metrics
```python
Jain's Fairness Index = (Σx_i)² / (n × Σx_i²)
Range: [0, 1]
1 = perfectly fair
0 = completely unfair

Apply to:
- Energy consumption
- Traffic load
- Transmission count

Goal: Index > 0.85
```

### 5. Scalability Metrics
```python
Computational Time = Runtime(N nodes)
Memory Usage = RAM consumption
Convergence Speed = Episodes to converge
Scalability Coefficient = T(2N) / T(N)

Goal: Linear or sub-linear growth
```

---

## 📝 Baseline Algorithms (برای مقایسه)

### LEACH (Low-Energy Adaptive Clustering Hierarchy)
```python
# src/routing/baselines/leach.py

Characteristics:
- Random CH selection (probability-based)
- Clusters reform every round
- TDMA within cluster
- Direct CH-to-sink transmission

Expected Performance:
- FND: ~500-700 rounds (100 nodes, 0.5J)
- PDR: 95-98%
- Energy: baseline reference
```

### PEGASIS (Power-Efficient Gathering in Sensor Information Systems)
```python
# src/routing/baselines/pegasis.py

Characteristics:
- Chain-based topology
- Nodes take turns as leader
- Greedy algorithm for chain formation
- Fusion along chain

Expected Performance:
- FND: ~1.5× LEACH
- Energy efficiency: +30% vs LEACH
- Lower latency than LEACH
```

### OSPF (for SDN comparison)
```python
# src/routing/baselines/ospf.py

Characteristics:
- Link-state routing
- Dijkstra's shortest path
- No energy consideration
- Suitable for SDN baseline

Expected Performance:
- Fast convergence
- High PDR
- Poor energy balance (hotspots)
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_algorithms.py

Test cases:
1. Algorithm initialization
2. Routing table computation
3. State/action space validity
4. Reward function calculation
5. Energy model correctness
6. Convergence behavior

Tools: pytest, unittest
Coverage target: > 80%
```

### Integration Tests
```python
# tests/test_simulation.py

Test cases:
1. Network deployment
2. Multi-round simulation
3. Metric collection
4. Result aggregation
5. Plot generation

Tools: pytest
```

### Performance Tests
```python
# tests/test_performance.py

Test cases:
1. Runtime benchmarks
2. Memory profiling
3. Scalability tests
4. Stress tests (large networks)

Tools: pytest-benchmark, memory_profiler
```

---

## 📦 Dependencies

### Core Dependencies
```txt
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
pandas>=2.0.0
networkx>=3.1
scikit-learn>=1.3.0
```

### Deep Learning
```txt
torch>=2.0.0
torch-geometric>=2.3.0  # For GNN
```

### Optimization
```txt
deap>=1.4.0  # For Genetic Algorithms
pymoo>=0.6.0  # For multi-objective optimization
```

### Utilities
```txt
tqdm>=4.65.0  # Progress bars
seaborn>=0.12.0  # Advanced plotting
joblib>=1.3.0  # Parallel processing
```

---

## ⚠️ چالش‌ها و راه‌حل‌ها

### چالش 1: زمان اجرای طولانی DRL algorithms
**راه‌حل**:
- استفاده از GPU (CUDA)
- Parallel training با multiprocessing
- Checkpoint saving هر 100 round
- Early stopping based on convergence

### چالش 2: Reproducibility
**راه‌حل**:
- Fixed random seeds
- Deterministic mode for PyTorch
- Save complete configuration
- Version control for dependencies

### چالش 3: Memory constraints
**راه‌حل**:
- Batch processing for large networks
- Limited replay buffer size
- Gradient checkpointing for GNN
- Clear cache regularly

### چالش 4: Hyperparameter tuning
**راه‌حل**:
- Grid search for critical parameters
- Use published values as starting point
- Sensitivity analysis to identify important params
- Document all hyperparameter choices

---

## 📊 برنامه زمانی پیشنهادی

### هفته 1: آماده‌سازی و الگوریتم 1-2
- روز 1: پاکسازی و setup
- روز 2-3: NN_ILEACH implementation
- روز 4-5: DOS-RL implementation
- روز 6-7: Testing و debugging

### هفته 2: الگوریتم 3-4
- روز 8-10: MSSO-FCM implementation
- روز 11-13: PGAECR implementation
- روز 14: Testing و integration

### هفته 3: الگوریتم 5-6
- روز 15-17: WOAD3QN-RP implementation
- روز 18-21: GN-DQN implementation

### هفته 4: Baselines و Experiments
- روز 22-23: LEACH, PEGASIS baselines
- روز 24-25: Experiment scripts
- روز 26-28: Running all experiments

### هفته 5: Analysis و Documentation
- روز 29-30: Plot generation
- روز 31-32: Comprehensive report
- روز 33-35: Documentation و final review

**مجموع**: ~5 هفته (35 روز)

---

## 🎯 معیارهای موفقیت

### کد:
- ✅ 6 الگوریتم جدید پیاده‌سازی شده
- ✅ بدون هیچ ردی از SPR, EAR, ALB
- ✅ کد تمیز با docstrings کامل
- ✅ Test coverage > 80%

### شبیه‌سازی:
- ✅ 6 سناریو کامل اجرا شده
- ✅ حداقل 10 run برای هر پیکربندی
- ✅ Reproducible با fixed seeds

### نتایج:
- ✅ جداول جامع CSV
- ✅ 12+ نمودار publication-quality
- ✅ تحلیل آماری معنادار (p-values < 0.05)
- ✅ مقایسه موفق با benchmarks (<10% error)

### مستندات:
- ✅ README جامع
- ✅ گزارش 20+ صفحه‌ای
- ✅ API documentation کامل
- ✅ User guide با مثال‌ها

---

## 📚 منابع کلیدی

### الگوریتم‌ها:
1. NN_ILEACH: DOI: 10.1038/s41598-024-75904-1
2. DOS-RL: DOI: 10.3390/s23208435
3. MSSO-FCM: DOI: 10.1038/s41598-024-66703-9
4. PGAECR: DOI: 10.1038/s41598-025-09117-5
5. WOAD3QN-RP: DOI: S0957417423035911
6. GN-DQN: DOI: S0167739X23003497

### مبانی نظری:
- Kobo et al., 2017: SD-WSN survey (DOI: 10.1109/ACCESS.2017.2656638)
- Wang et al., 2024: DRL survey (DOI: 10.1109/TNNLS.2022.3207346)

---

## 🚀 Next Steps

1. **APPROVE این ROADMAP**
   - آیا با این برنامه موافقید؟
   - آیا تغییری در اولویت‌ها می‌خواهید؟

2. **شروع فاز 1: پاکسازی**
   - حذف SPR, EAR, ALB
   - ایجاد ساختار جدید
   - Setup utility modules

3. **پیاده‌سازی مرحله‌ای**
   - شروع با NN_ILEACH
   - Testing پس از هر الگوریتم
   - Integration مداوم

---

**آماده برای شروع هستید؟** 🚀

لطفاً تأیید کنید تا به فاز 1 (پاکسازی و آماده‌سازی) بپردازم!
