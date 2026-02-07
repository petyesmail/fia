# طرح توسعه علمی هدفمند پروژه
# Targeted Scientific Development Plan for Research Project

**تاریخ تحلیل:** 1404/11/13 - 2026-02-01
**سطح هدف:** پیشرفته (Advanced)
**وضعیت:** طراحی توسعه پس از تحلیل جامع

---

## 📊 تحلیل وضعیت فعلی | Current Status Analysis

### ✅ نقاط قوت موجود | Existing Strengths

1. **معماری جامع:**
   - 9 الگوریتم پیاده‌سازی شده (3 baseline + 6 advanced)
   - مدل انرژی تخصصی First-Order Radio Model
   - معیارهای ارزیابی کامل (FND, HND, LND, PDR, Throughput, Energy Efficiency)

2. **پیاده‌سازی‌های قوی:**
   - **MSSO-FCM:** کامل‌ترین پیاده‌سازی با Multi-Strategy Snake Optimizer
   - **PGAECR:** NSGA-II با Pareto optimization
   - **NN_ILEACH:** Neural Network با feature engineering

3. **زیرساخت تحقیق:**
   - Simulation framework قابل توسعه
   - پارامترهای قابل تنظیم
   - مستندات اولیه

### ❌ محدودیت‌های اساسی | Critical Limitations

#### 1. **پیاده‌سازی‌های ناقص**

**WOAD3QN-RP:**
```
✗ WOA optimization: فقط placeholder
✗ Dueling DQN architecture: پیاده‌سازی نشده
✗ Experience replay: تعریف شده ولی استفاده نمی‌شود
✗ Target network update: دستور pass (خالی)
✗ Training loop: وجود ندارد
```

**GN-DQN:**
```
✗ GraphNeuralNetwork: کلاس تعریف نشده
✗ GAT+GCN layers: جزئیات پیاده‌سازی ناموجود
✗ Graph embedding: ابعاد inconsistent (128 vs 256)
✗ Training mechanism: غیرفعال
✗ Feature integration: ناقص (buffer=0.0 hardcoded)
```

#### 2. **فقدان توجیه علمی**

- ❌ هیچ ablation study برای تحلیل مؤلفه‌ها
- ❌ بدون sensitivity analysis برای پارامترها
- ❌ فقدان convergence analysis
- ❌ بدون theoretical justification برای hyperparameters
- ❌ مقایسه با state-of-the-art ناکافی

#### 3. **نمایش‌های بصری ناکافی**

- ❌ فقدان network topology visualization
- ❌ بدون نمایش cluster formation در راندها
- ❌ عدم نمایش routing paths
- ❌ فقدان energy heatmap
- ❌ بدون animated evolution شبکه

#### 4. **تحلیل‌های ناکامل**

- ❌ فقدان statistical significance testing
- ❌ بدون confidence intervals
- ❌ عدم box plots برای distribution analysis
- ❌ فقدان correlation analysis بین metrics

---

## 🎯 اهداف توسعه علمی | Scientific Development Goals

### هدف کلی
**ارائه یک چارچوب جامع ارزیابی الگوریتم‌های مسیریابی SD-WSN با:**
1. پیاده‌سازی کامل و صحیح همه الگوریتم‌ها
2. تحلیل‌های آماری معتبر با توجیه علمی
3. نمایش‌های بصری دقیق و قابل فهم
4. مقایسه چند-سناریویی با توجیه علمی
5. مستندات کامل برای ارائه پروژه

### اهداف خاص

#### 1. تکمیل پیاده‌سازی‌ها
- [ ] تکمیل WOAD3QN-RP با WOA واقعی + Dueling D3QN
- [ ] پیاده‌سازی کامل GN-DQN با GAT/GCN layers
- [ ] اصلاح DOS-RL با reward function اصولی
- [ ] بهبود NN_ILEACH با online learning

#### 2. افزودن نمایش‌های بصری
- [ ] Network topology با clustering در هر راند
- [ ] Energy heatmap temporal
- [ ] Routing path visualization
- [ ] Node lifetime distribution
- [ ] Animated network evolution

#### 3. تحلیل‌های آماری پیشرفته
- [ ] Statistical significance testing (t-test, ANOVA)
- [ ] Confidence intervals (95%)
- [ ] Box plots برای distribution
- [ ] Correlation analysis
- [ ] Scalability analysis (50-500 nodes)

#### 4. سناریوهای تخصصی
- [ ] Density variation: 50, 100, 150, 200, 250 nodes
- [ ] Traffic variation: Low, Medium, High, Burst
- [ ] Energy heterogeneity: Uniform vs Non-uniform
- [ ] Mobility scenarios: Static vs Mobile nodes
- [ ] Failure scenarios: Random node failures

---

## 🔬 معیارهای ارائه پروژه | Project Acceptance Criteria

### معیارهای علمی | Scientific Criteria

1. **اصالت (Novelty):**
   - ✅ پیاده‌سازی جامع 9 الگوریتم در یک framework
   - ⚠️ نیاز: مقایسه با آخرین تحقیقات 2024-2026
   - ⚠️ نیاز: تحلیل trade-offs الگوریتم‌ها

2. **دقت علمی (Rigor):**
   - ✅ مدل انرژی معتبر (First-Order Radio)
   - ⚠️ نیاز: validation با نتایج published papers
   - ⚠️ نیاز: statistical significance در همه مقایسه‌ها

3. **قابلیت تکرار (Reproducibility):**
   - ✅ Random seed = 42
   - ✅ پارامترها documented
   - ⚠️ نیاز: detailed experimental setup
   - ⚠️ نیاز: computational environment specification

4. **تحلیل جامع (Comprehensive Analysis):**
   - ⚠️ نیاز: convergence analysis برای RL/GA algorithms
   - ⚠️ نیاز: complexity analysis (time, space)
   - ⚠️ نیاز: scalability experiments
   - ⚠️ نیاز: sensitivity analysis

### معیارهای فنی | Technical Criteria

1. **صحت پیاده‌سازی:**
   - ✅ LEACH, PEGASIS, OSPF: کامل
   - ✅ MSSO-FCM, PGAECR: نسبتاً کامل
   - ❌ WOAD3QN-RP, GN-DQN: ناقص
   - ⚠️ NN_ILEACH, DOS-RL: نیاز به بهبود

2. **کیفیت کد:**
   - ✅ ساختار modular
   - ✅ docstrings برای توابع
   - ⚠️ نیاز: unit tests
   - ⚠️ نیاز: integration tests

3. **نتایج:**
   - ⚠️ نیاز: consistency check با literature
   - ⚠️ نیاز: validation با real-world scenarios
   - ⚠️ نیاز: benchmark datasets

---

## 📈 طرح توسعه مرحله‌ای | Phased Development Plan

### مرحله 1: تکمیل پیاده‌سازی‌ها (Priority: HIGH)

**مدت:** 2 هفته

#### Task 1.1: WOAD3QN-RP Complete Implementation
```python
# اضافه کردن:
- WhaleOptimizationAlgorithm class واقعی
- DuelingDQN architecture با value/advantage streams
- Experience replay buffer با proper sampling
- Target network update mechanism
- Training loop با proper rewards
- Hyperparameter tuning با WOA
```

#### Task 1.2: GN-DQN Complete Implementation
```python
# اضافه کردن:
- GraphAttentionLayer (GAT) implementation
- GraphConvolutionalLayer (GCN) implementation
- Proper node feature extraction
- Graph embedding concatenation
- Training loop
- Batch processing for graphs
```

#### Task 1.3: DOS-RL Improvements
```python
# بهبود:
- Principled reward function (actual packet delivery)
- Proper Q-value updates با true rewards
- Convergence monitoring
- Multi-objective Pareto analysis
```

#### Task 1.4: NN_ILEACH Online Learning
```python
# اضافه کردن:
- Online training با new data
- Incremental learning
- Model adaptation per round
```

### مرحله 2: افزودن Visualization (Priority: HIGH)

**مدت:** 1 هفته

#### Task 2.1: Network Topology Plots
- Scatter plot of nodes با colors برای: alive/dead, CH/member, energy levels
- Clustering boundaries
- Routing paths (source → sink)
- Snapshots در rounds: 1, 50, 100, 200, 300

#### Task 2.2: Energy Heatmaps
- 2D heatmap با interpolation
- Temporal evolution (animated GIF یا video)
- Hotspot identification

#### Task 2.3: Routing Path Visualization
- Path من source تا sink
- Multi-hop visualization
- Load distribution on paths

#### Task 2.4: Statistical Plots
- Box plots برای metric distributions
- Violin plots
- CDF plots
- Correlation heatmaps

### مرحله 3: تحلیل‌های پیشرفته (Priority: MEDIUM)

**مدت:** 1 هفته

#### Task 3.1: Statistical Testing
```python
# اضافه کردن:
- Paired t-tests برای algorithm comparisons
- ANOVA برای multi-group comparison
- Post-hoc tests (Tukey HSD)
- Effect size calculations (Cohen's d)
```

#### Task 3.2: Confidence Intervals
```python
# برای همه metrics:
- Bootstrap confidence intervals (95%)
- Standard error bars در plots
- Significance markers (* p<0.05, ** p<0.01)
```

#### Task 3.3: Convergence Analysis
```python
# برای RL/GA algorithms:
- Plot reward/fitness over iterations
- Moving average smoothing
- Convergence threshold detection
- Early stopping analysis
```

#### Task 3.4: Sensitivity Analysis
```python
# Test parameter variations:
- Energy model parameters (E_elec, ε_fs, ε_mp)
- DRL hyperparameters (α, γ, ε)
- Network parameters (comm_range, initial_energy)
# Generate tornado plots
```

### مرحله 4: سناریوهای تخصصی (Priority: HIGH)

**مدت:** 1 هفته

#### Scenario A: Scalability Analysis
```
Configurations:
- Nodes: 50, 100, 150, 200, 250, 300
- Area: scale proportionally (maintain density)
- Metrics: FND, PDR, Energy Efficiency, Computation Time
- Plot: metrics vs number of nodes
```

#### Scenario B: Traffic Load Analysis
```
Configurations:
- Traffic: 3, 5, 10, 15, 20 packets/round
- Fixed: 100 nodes, 100×100m area
- Metrics: PDR, End-to-End Delay, Throughput
- Plot: metrics vs traffic load
```

#### Scenario C: Energy Heterogeneity
```
Configurations:
- Uniform: all nodes 0.5J
- Heterogeneous-1: 70% normal (0.5J), 30% advanced (1.0J)
- Heterogeneous-2: random U(0.3, 0.7)
- Metrics: Fairness, Lifetime, PDR
```

#### Scenario D: Node Failure Resilience
```
Configurations:
- Random failures: 5%, 10%, 20% at round 150
- Metrics: Recovery time, PDR drop, Network partition
```

### مرحله 5: مستندات و گزارش نهایی (Priority: HIGH)

**مدت:** 3 روز

#### Task 5.1: Comprehensive Report
```markdown
# ساختار گزارش نهایی:

1. چکیده (Abstract) - فارسی و انگلیسی
2. مقدمه و بیان مسئله
3. مروری بر کارهای مرتبط
4. روش‌شناسی
   - معماری SD-WSN
   - مدل انرژی
   - فرمول‌بندی مسئله
5. الگوریتم‌های پیشنهادی
   - توضیح ریاضی هر الگوریتم
   - Pseudocode
   - پیچیدگی محاسباتی
6. ارزیابی تجربی
   - تنظیمات شبیه‌سازی
   - سناریوها
   - نتایج
7. تحلیل و مقایسه
   - تحلیل آماری
   - بحث بر روی نتایج
   - Trade-offs
8. نتیجه‌گیری و کارهای آینده
9. مراجع
10. پیوست‌ها
```

#### Task 5.2: Supplementary Materials
- Table of all parameters
- Detailed algorithm configurations
- Complete result tables
- Source code documentation

---

## 🚀 پیاده‌سازی فوری | Immediate Implementation

### اولویت 1: شبیه‌ساز جامع با Visualization

**فایل جدید:** `phd_level_comprehensive_simulator.py`

**ویژگی‌ها:**
1. ✅ اجرای همه 9 الگوریتم
2. ✅ چند سناریو: Density, Traffic, Heterogeneity
3. ✅ Network topology visualization در راندهای کلیدی
4. ✅ Energy heatmap temporal
5. ✅ Routing path visualization
6. ✅ Statistical analysis با confidence intervals
7. ✅ Comprehensive plots (15-20 نمودار)
8. ✅ JSON/CSV results export
9. ✅ گزارش جامع markdown

### اولویت 2: تحلیل آماری پیشرفته

**فایل جدید:** `statistical_analysis.py`

**ویژگی‌ها:**
1. ✅ T-tests و ANOVA
2. ✅ Effect size calculations
3. ✅ Bootstrap confidence intervals
4. ✅ Distribution analysis
5. ✅ Correlation matrices

### اولویت 3: مستندات علمی

**فایل جدید:** `DISSERTATION_FINAL_REPORT.md`

**ویژگی‌ها:**
1. ✅ ساختار پروژه کامل
2. ✅ فرمول‌های ریاضی با LaTeX
3. ✅ تمام جداول و نمودارها
4. ✅ تحلیل‌های عمیق
5. ✅ منابع کامل

---

## 📊 Metrics جامع برای ارزیابی | Comprehensive Evaluation Metrics

### 1. Network Lifetime Metrics
- **FND** (First Node Death) - round number
- **HND** (Half Nodes Death) - round number
- **LND** (Last Node Death) - round number
- **Stability Period** = HND - FND
- **Instability Period** = LND - HND
- **Average Lifetime** = mean(node lifetimes)

### 2. Energy Metrics
- **Total Energy Consumed** (Joules)
- **Average Residual Energy** per round
- **Energy Efficiency** = packets_delivered / energy_consumed
- **Energy Variance** = std(node energies)
- **Energy Balance Factor** = min_energy / max_energy
- **Energy Depletion Rate** (J/round)

### 3. Quality of Service (QoS)
- **PDR** (Packet Delivery Ratio) %
- **Throughput** (packets/second)
- **End-to-End Delay** (milliseconds)
  - Average delay
  - 90th percentile delay
  - Max delay
- **Jitter** (delay variance) (ms)
- **Packet Loss Rate** %

### 4. Load Balance & Fairness
- **Jain's Fairness Index** ∈ [0, 1]
- **Load Standard Deviation**
- **CH Load Balance** (for clustering)
- **Path Usage Distribution**

### 5. Routing Efficiency
- **Average Hop Count**
- **Path Length Distribution**
- **Routing Overhead** (control packets / data packets)
- **Route Convergence Time**

### 6. Algorithm-Specific Metrics

**For Clustering (LEACH, NN_ILEACH, MSSO-FCM):**
- Number of clusters per round
- Average cluster size
- CH energy consumption
- Member-to-CH distance

**For RL/DRL (DOS-RL, WOAD3QN-RP, GN-DQN):**
- Learning curve (reward over episodes)
- Convergence rate
- Exploration-exploitation ratio
- Q-value statistics

**For GA (PGAECR):**
- Fitness evolution
- Pareto front size
- Hypervolume indicator
- Population diversity

---

## 🎨 Visualization Plan | طرح نمایش‌های بصری

### Plot 1: Network Topology Evolution (6 subplots)
- Rounds: 1, 50, 100, 200, 300, Final
- Node colors: Energy level (colormap: RdYlGn)
- Node markers: Circle (alive), X (dead), Star (CH), Square (sink)
- Edges: Routing paths (alpha=0.3)

### Plot 2: Energy Heatmap Temporal (GIF/Video)
- 2D interpolated heatmap
- Colorbar: Energy (0-0.5J)
- Frame per 10 rounds
- Side panel: Round number, Alive nodes, Avg energy

### Plot 3: Lifetime Analysis
- Subplot 1: CDF of node lifetimes per algorithm
- Subplot 2: Box plot of lifetimes
- Subplot 3: Violin plot showing distribution
- Subplot 4: FND/HND/LND bars

### Plot 4: Energy Efficiency Comparison
- Multi-bar chart: all algorithms
- Error bars: 95% CI
- Significance markers
- Inset: zoom on top performers

### Plot 5: PDR vs Traffic Load
- Line plot with markers
- Shaded area: confidence interval
- Separate line per algorithm
- Grid: alpha=0.3

### Plot 6: Scalability Analysis
- X-axis: Number of nodes (50-300)
- Y-axes: FND, PDR, Energy Efficiency, Computation Time
- 4 subplots
- Log scale where appropriate

### Plot 7: Correlation Matrix
- Heatmap of metric correlations
- Metrics: FND, PDR, Energy, Fairness, Throughput, etc.
- Color: RdBu diverging
- Annotations: correlation coefficients

### Plot 8: Routing Path Visualization
- For each algorithm: sample network snapshot
- Highlight: 5 random routing paths from sources to sink
- Path colors: different per source
- Arrow heads show direction

### Plot 9: Convergence Analysis (RL/GA)
- Learning curve: reward/fitness vs iteration
- Subplot per algorithm
- Moving average (window=10)
- Shaded area: std deviation

### Plot 10: Statistical Comparison
- Grouped bar chart with error bars
- Groups: algorithms
- Bars: FND, PDR×10, Efficiency/100 (normalized)
- Significance brackets (p<0.05)

### Plot 11: Energy Variance Over Time
- Line plot: energy variance per round
- Separate line per algorithm
- Lower = better balance

### Plot 12: Cluster Formation (for clustering algorithms)
- Voronoi diagram showing cluster boundaries
- CH positions marked
- Member colors per cluster

---

## 🔧 Technical Implementation Details

### Energy Model (بازنویسی برای دقت بالاتر)

```python
@dataclass
class EnhancedEnergyModel:
    """Enhanced First-Order Radio Energy Model"""

    # Constants (نانوژول)
    E_elec: float = 50.0  # nJ/bit
    E_fs: float = 10.0  # pJ/bit/m²
    E_mp: float = 0.0013  # pJ/bit/m⁴
    d0: float = 87.0  # meters
    E_DA: float = 5.0  # nJ/bit (data aggregation)

    # Packet parameters
    packet_size: int = 4000  # bits
    control_packet_size: int = 200  # bits

    def tx_energy(self, bits: int, distance: float) -> float:
        """Transmission energy in Joules"""
        if distance < self.d0:
            e_amp = (self.E_fs * 1e-3) * (distance ** 2)  # pJ→nJ
        else:
            e_amp = (self.E_mp * 1e-3) * (distance ** 4)

        return (self.E_elec + e_amp) * bits * 1e-9  # nJ→J

    def rx_energy(self, bits: int) -> float:
        """Reception energy in Joules"""
        return self.E_elec * bits * 1e-9

    def aggregation_energy(self, num_packets: int) -> float:
        """Data aggregation energy"""
        return self.E_DA * self.packet_size * num_packets * 1e-9
```

### Simulation Framework Enhancement

```python
class EnhancedNetworkSimulator:
    """Advanced Network Simulator with Full Instrumentation"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.controller = SDNController(config)
        self.energy_model = EnhancedEnergyModel()

        # Instrumentation
        self.round_history = []  # Full state per round
        self.event_log = []  # Packet-level events
        self.topology_snapshots = {}  # Network topology at key rounds

    def run_algorithm(self, algorithm, max_rounds=500, snapshot_rounds=[1,50,100,200,300]):
        """Run with full logging"""

        results = {
            'algorithm': algorithm.algorithm_name,
            'rounds': [],
            'node_lifetimes': [],
            'packets': {'sent': 0, 'delivered': 0},
            'energy': {'consumed': [], 'residual': []},
            'topology_snapshots': {},
            'events': []
        }

        for round_num in range(1, max_rounds + 1):
            # Compute routing
            routing_table = algorithm.compute_routing_table(self.controller)

            # Simulate traffic
            round_stats = self._simulate_round(routing_table, round_num)
            results['rounds'].append(round_stats)

            # Snapshot topology
            if round_num in snapshot_rounds:
                results['topology_snapshots'][round_num] = self._capture_topology()

            # Check termination
            if not self.controller.get_active_sensors():
                break

        return results

    def _simulate_round(self, routing_table, round_num):
        """Simulate one round with detailed logging"""
        # ... (packet transmission, energy consumption, logging)
        pass

    def _capture_topology(self):
        """Capture current network state"""
        return {
            'nodes': [(n.x, n.y, n.current_energy, n.is_alive)
                      for n in self.controller.nodes.values()],
            'clusters': self._get_current_clusters(),
            'routing_paths': self._extract_routing_paths()
        }
```

---

## 📝 نتیجه‌گیری طرح توسعه

### برای ارائه پروژه دکتری باید:

1. ✅ **تکمیل پیاده‌سازی‌ها:** WOAD3QN-RP و GN-DQN به صورت کامل
2. ✅ **افزودن نمایش‌های بصری:** 12+ نمودار دقیق
3. ✅ **تحلیل‌های آماری:** Significance testing, CIs, Effect sizes
4. ✅ **سناریوهای چندگانه:** Density, Traffic, Heterogeneity, Failures
5. ✅ **مستندات جامع:** گزارش 100+ صفحه با فرمول‌ها و تحلیل

### زمان‌بندی کلی
- **تکمیل پیاده‌سازی:** 2 هفته
- **Visualization:** 1 هفته
- **تحلیل‌های پیشرفته:** 1 هفته
- **سناریوها:** 1 هفته
- **مستندات:** 3 روز

**جمع کل:** ~5 هفته برای پروژه کامل

---

## 🚦 مرحله بعدی: اجرای فوری

با توجه به درخواست کاربر، **الان** باید:

1. شبیه‌ساز جامع با visualization بسازیم
2. همه الگوریتم‌ها را اجرا کنیم
3. نمودارهای گرافیکی تولید کنیم
4. نمایش شبکه در راندها
5. تحلیل‌های آماری
6. گزارش نهایی

**فایل‌های مورد نیاز:**
- `comprehensive_simulator.py` - شبیه‌ساز اصلی
- `network_visualizer.py` - ماژول visualization
- `statistical_analyzer.py` - تحلیل‌های آماری
- `DISSERTATION_RESULTS.md` - گزارش نهایی

---

**این طرح را اکنون اجرایی می‌کنیم! 🚀**
