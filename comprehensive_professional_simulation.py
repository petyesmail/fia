"""
شبیه‌سازی جامع و تخصصی الگوریتم‌های مسیریابی WSN-SDN
Comprehensive Professional Simulation of WSN-SDN Routing Algorithms

این شبیه‌ساز در سطح دکتری شامل:
- تحلیل چگالی شبکه (Density Analysis): 50-250 نود
- تحلیل ترافیک متغیر (Traffic Analysis): Low, Medium, High
- مقایسه کامل الگوریتم‌ها با metrics تخصصی
- تولید نمودارها و تحلیل رفتاری

PhD-Level Simulator Including:
- Network Density Analysis: 50-250 nodes
- Variable Traffic Analysis: Low, Medium, High
- Complete algorithm comparison with professional metrics
- Graph generation and behavioral analysis

نویسنده: تیم تحقیقاتی
Author: Research Team
تاریخ: 1404/11/12 - 2026-01-31
"""

import numpy as np
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.config import SimulationConfig
from src.simulation.simulator import NetworkSimulator

# Import all 9 algorithms
from src.routing.baselines.leach import LEACH
from src.routing.baselines.pegasis import PEGASIS
from src.routing.baselines.ospf import OSPF
from src.routing.nn_ileach import NN_ILEACH
from src.routing.dos_rl import DOS_RL
from src.routing.msso_fcm import MSSO_FCM
from src.routing.pgaecr import PGAECR
from src.routing.woad3qn_rp import WOAD3QN_RP
from src.routing.gn_dqn import GN_DQN


# =============================================================================
# پارامترهای انرژی تخصصی - Professional Energy Parameters
# =============================================================================

@dataclass
class ProfessionalEnergyModel:
    """
    مدل انرژی رادیویی مرتبه اول با دقت نانوژول
    First-Order Radio Energy Model with Nanojoule Precision

    مبنا: Heinzelman et al., "Energy-Efficient Communication Protocol"
    Reference: Heinzelman et al., "Energy-Efficient Communication Protocol"
    """
    # Electronics energy - انرژی الکترونیک
    E_elec: float = 50.0  # nJ/bit

    # Free-space model (d² power loss) - مدل فضای آزاد
    epsilon_fs: float = 10.0  # pJ/bit/m² = 0.01 nJ/bit/m²

    # Multi-path fading model (d⁴ power loss) - مدل چندمسیره
    epsilon_mp: float = 0.0013  # pJ/bit/m⁴

    # Crossover distance - فاصله تقاطع
    d0: float = 87.0  # meters

    # Data aggregation energy - انرژی تجمیع داده
    E_DA: float = 5.0  # nJ/bit/signal

    # Packet size - اندازه بسته
    packet_size: int = 4000  # bits

    def calculate_tx_energy_nJ(self, num_bits: int, distance: float) -> float:
        """
        محاسبه انرژی ارسال به نانوژول
        Calculate transmission energy in nanojoules

        E_TX = E_elec × k + ε_amp × k × d^n
        """
        if distance < self.d0:
            e_amp = self.epsilon_fs * (distance ** 2)
        else:
            e_amp = self.epsilon_mp * (distance ** 4)

        energy_nj = (self.E_elec + e_amp) * num_bits
        return energy_nj

    def calculate_rx_energy_nJ(self, num_bits: int) -> float:
        """
        محاسبه انرژی دریافت به نانوژول
        Calculate reception energy in nanojoules
        """
        return self.E_elec * num_bits

    def nJ_to_microJ(self, nanojoules: float) -> float:
        """تبدیل نانوژول به میکروژول - Convert nJ to μJ"""
        return nanojoules / 1000.0

    def nJ_to_milliJ(self, nanojoules: float) -> float:
        """تبدیل نانوژول به میلی‌ژول - Convert nJ to mJ"""
        return nanojoules / 1_000_000.0

    def nJ_to_J(self, nanojoules: float) -> float:
        """تبدیل نانوژول به ژول - Convert nJ to J"""
        return nanojoules / 1_000_000_000.0


# =============================================================================
# Metrics تخصصی - Professional Metrics
# =============================================================================

@dataclass
class ProfessionalMetrics:
    """
    معیارهای ارزیابی عملکرد تخصصی
    Professional Performance Evaluation Metrics
    """
    # Network Lifetime Metrics - معیارهای طول عمر شبکه
    fnd: Optional[int] = None  # First Node Death - مرگ اولین نود
    hnd: Optional[int] = None  # Half Nodes Death - مرگ نیمی از نودها
    lnd: Optional[int] = None  # Last Node Death - مرگ آخرین نود
    stability_period: Optional[int] = None  # FND rounds - دوره پایداری
    instability_period: Optional[int] = None  # LND - FND - دوره ناپایداری

    # Quality of Service Metrics - معیارهای کیفیت سرویس
    pdr: float = 0.0  # Packet Delivery Ratio (%) - نسبت تحویل بسته
    throughput: float = 0.0  # packets/second - توان عبور
    average_delay: float = 0.0  # milliseconds - تأخیر میانگین
    jitter: float = 0.0  # milliseconds - لرزش

    # Energy Metrics - معیارهای انرژی
    total_energy_consumed_mJ: float = 0.0  # میلی‌ژول
    energy_per_packet_microJ: float = 0.0  # میکروژول
    energy_efficiency: float = 0.0  # packets/Joule
    avg_residual_energy_ratio: float = 0.0  # نسبت انرژی باقیمانده

    # Load Balance Metrics - معیارهای توازن بار
    jains_fairness_index: float = 0.0  # شاخص عدالت Jain
    energy_balance_factor: float = 0.0  # ضریب توازن انرژی
    load_std_deviation: float = 0.0  # انحراف معیار بار

    # Traffic Metrics - معیارهای ترافیک
    total_packets_sent: int = 0
    total_packets_delivered: int = 0
    total_packets_dropped: int = 0
    average_hop_count: float = 0.0

    # Scalability Metrics - معیارهای مقیاس‌پذیری
    network_efficiency: float = 0.0  # alive_nodes / total_nodes
    connectivity_ratio: float = 0.0  # connected_nodes / total_nodes


# =============================================================================
# شبیه‌ساز تخصصی - Professional Simulator
# =============================================================================

class ComprehensiveProfessionalSimulator:
    """
    شبیه‌ساز جامع سطح دکتری
    PhD-Level Comprehensive Simulator
    """

    def __init__(self):
        self.energy_model = ProfessionalEnergyModel()
        self.results = defaultdict(list)
        self.figures = []

        # آرایه رنگ‌ها برای نمودارها
        self.colors = {
            'LEACH': '#FF6B6B',
            'PEGASIS': '#4ECDC4',
            'OSPF': '#45B7D1',
            'NN_ILEACH': '#FFA07A',
            'DOS-RL': '#98D8C8',
            'MSSO-FCM': '#F7DC6F',
            'PGAECR': '#BB8FCE',
            'WOAD3QN-RP': '#85C1E2',
            'GN-DQN': '#F8B500'
        }

        # مارکرهای نمودار
        self.markers = {
            'LEACH': 'o',
            'PEGASIS': 's',
            'OSPF': '^',
            'NN_ILEACH': 'D',
            'DOS-RL': 'v',
            'MSSO-FCM': 'p',
            'PGAECR': '*',
            'WOAD3QN-RP': 'h',
            'GN-DQN': 'X'
        }

    def print_section_header(self, title: str, level: int = 1):
        """چاپ سرتیتر بخش"""
        char = "=" if level == 1 else "-"
        width = 100
        print(f"\n{char * width}")
        print(f"{title.center(width)}")
        print(f"{char * width}\n")

    def run_single_simulation(
        self,
        algorithm,
        config: SimulationConfig,
        max_rounds: int = 500,
        packets_per_round: int = 5,
        verbose: bool = False
    ) -> ProfessionalMetrics:
        """
        اجرای یک شبیه‌سازی کامل برای یک الگوریتم
        Run a complete simulation for one algorithm
        """
        simulator = NetworkSimulator(config)
        simulator.deploy_network()

        metrics = ProfessionalMetrics()

        # ردیابی متغیرها
        total_nodes = config.num_nodes
        half_threshold = total_nodes // 2
        packets_sent = 0
        packets_delivered = 0
        packets_dropped = 0
        total_delay = 0.0
        delays = []
        hop_counts = []

        energy_consumed_nJ = 0.0

        if verbose:
            print(f"🔬 الگوریتم: {algorithm.algorithm_name}")
            print(f"   شبکه: {total_nodes} نود، {config.area_size}×{config.area_size}m²")
            print(f"   انرژی اولیه: {config.initial_energy}J")

        # حلقه شبیه‌سازی
        for round_num in range(1, max_rounds + 1):
            # محاسبه جدول مسیریابی
            try:
                routing_table = algorithm.compute_routing_table(simulator.controller)
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  خطا در راند {round_num}: {str(e)[:50]}")
                break

            # گرفتن نودهای زنده
            alive_nodes = simulator.controller.get_active_sensors()
            if not alive_nodes:
                if metrics.lnd is None:
                    metrics.lnd = round_num - 1
                break

            alive_count = len(alive_nodes)

            # تشخیص رویدادهای طول عمر
            if metrics.fnd is None and alive_count < total_nodes:
                metrics.fnd = round_num
                metrics.stability_period = round_num
                if verbose:
                    print(f"   🔴 FND (مرگ اولین نود) در راند {round_num}")

            if metrics.hnd is None and alive_count <= half_threshold:
                metrics.hnd = round_num
                if verbose:
                    print(f"   🟠 HND (مرگ نیمی از نودها) در راند {round_num}")

            # شبیه‌سازی ارسال بسته
            nodes_to_transmit = alive_nodes[:min(len(alive_nodes), packets_per_round)]

            for node_id in nodes_to_transmit:
                next_hop = routing_table.get(node_id)
                if not next_hop or next_hop not in simulator.controller.nodes:
                    packets_dropped += 1
                    continue

                node = simulator.controller.nodes[node_id]
                next_node = simulator.controller.nodes[next_hop]

                # محاسبه فاصله
                distance = np.sqrt(
                    (node.x - next_node.x) ** 2 +
                    (node.y - next_node.y) ** 2
                )

                # محاسبه انرژی به نانوژول
                tx_energy_nJ = self.energy_model.calculate_tx_energy_nJ(
                    self.energy_model.packet_size, distance
                )
                rx_energy_nJ = self.energy_model.calculate_rx_energy_nJ(
                    self.energy_model.packet_size
                )

                # تبدیل به ژول
                tx_energy_J = self.energy_model.nJ_to_J(tx_energy_nJ)
                rx_energy_J = self.energy_model.nJ_to_J(rx_energy_nJ)

                # مصرف انرژی
                if node.current_energy >= tx_energy_J:
                    node.consume_energy(tx_energy_J)
                    energy_consumed_nJ += tx_energy_nJ
                    packets_sent += 1

                    if next_node.current_energy >= rx_energy_J:
                        next_node.consume_energy(rx_energy_J)
                        energy_consumed_nJ += rx_energy_nJ

                        # محاسبه تأخیر (فرضی: 1ms فی hop)
                        delay_ms = 1.0 + np.random.normal(0, 0.1)
                        delays.append(delay_ms)

                        # اگر به sink رسید
                        if next_hop == 'SINK':
                            packets_delivered += 1
                            hop_counts.append(1)
                        else:
                            hop_counts.append(2)  # فرض: 2 hop تا sink
                    else:
                        packets_dropped += 1
                else:
                    packets_dropped += 1

            # چاپ پیشرفت
            if verbose and (round_num % 100 == 0 or round_num == max_rounds):
                energy_stats = simulator.controller.get_network_energy_statistics()
                print(f"   راند {round_num}/{max_rounds}: {alive_count}/{total_nodes} نود زنده، "
                      f"انرژی متوسط: {energy_stats['average_residual_energy']:.4f}J")

        # تنظیم LND
        if metrics.lnd is None:
            metrics.lnd = max_rounds

        # محاسبه stability و instability period
        if metrics.fnd:
            metrics.stability_period = metrics.fnd
            metrics.instability_period = metrics.lnd - metrics.fnd
        else:
            metrics.stability_period = max_rounds
            metrics.instability_period = 0

        # محاسبه PDR
        if packets_sent > 0:
            metrics.pdr = (packets_delivered / packets_sent) * 100.0

        # محاسبه throughput (فرض: هر راند 1 ثانیه)
        metrics.throughput = packets_delivered / max_rounds

        # محاسبه تأخیر میانگین
        if delays:
            metrics.average_delay = np.mean(delays)
            metrics.jitter = np.std(delays)

        # محاسبه hop count میانگین
        if hop_counts:
            metrics.average_hop_count = np.mean(hop_counts)

        # انرژی
        energy_consumed_J = self.energy_model.nJ_to_J(energy_consumed_nJ)
        metrics.total_energy_consumed_mJ = self.energy_model.nJ_to_milliJ(energy_consumed_nJ)

        if packets_delivered > 0:
            metrics.energy_per_packet_microJ = self.energy_model.nJ_to_microJ(
                energy_consumed_nJ / packets_delivered
            )
            metrics.energy_efficiency = packets_delivered / energy_consumed_J

        # شاخص عدالت
        metrics.jains_fairness_index = simulator.controller.calculate_fairness_index()

        # انرژی باقیمانده
        energy_stats = simulator.controller.get_network_energy_statistics()
        metrics.avg_residual_energy_ratio = energy_stats.get('average_residual_ratio', 0.0)

        # ترافیک
        metrics.total_packets_sent = packets_sent
        metrics.total_packets_delivered = packets_delivered
        metrics.total_packets_dropped = packets_dropped

        # مقیاس‌پذیری
        alive_nodes_final = simulator.controller.get_active_sensors()
        metrics.network_efficiency = len(alive_nodes_final) / total_nodes

        return metrics

    def run_density_analysis(self):
        """
        سناریو 1: تحلیل چگالی شبکه
        Scenario 1: Network Density Analysis

        بررسی رفتار الگوریتم‌ها با تعداد نودهای مختلف
        Analyze algorithm behavior with varying node counts
        """
        self.print_section_header(
            "سناریو 1: تحلیل چگالی شبکه - Scenario 1: Density Analysis"
        )

        node_counts = [50, 100, 150, 200, 250]
        algorithms = [
            LEACH(),
            PEGASIS(),
            OSPF(),
            NN_ILEACH(),
            DOS_RL(),
            MSSO_FCM(),
            PGAECR(),
            WOAD3QN_RP(),
            GN_DQN(),
        ]

        results = defaultdict(lambda: defaultdict(list))

        for node_count in node_counts:
            print(f"\n📊 تعداد نودها: {node_count} نود")
            print(f"   Node Count: {node_count} nodes")

            # تنظیمات
            config = SimulationConfig(
                num_nodes=node_count,
                area_size=100.0,
                sink_position=(50.0, 50.0),
                comm_range=30.0,
                initial_energy=0.5,
                max_rounds=300,
                seed=42
            )

            for algo in algorithms:
                print(f"   🔬 {algo.algorithm_name}...", end=' ')
                metrics = self.run_single_simulation(algo, config, max_rounds=300)

                # ذخیره نتایج
                results[algo.algorithm_name]['node_count'].append(node_count)
                results[algo.algorithm_name]['fnd'].append(metrics.fnd or 300)
                results[algo.algorithm_name]['pdr'].append(metrics.pdr)
                results[algo.algorithm_name]['energy_efficiency'].append(metrics.energy_efficiency)
                results[algo.algorithm_name]['throughput'].append(metrics.throughput)
                results[algo.algorithm_name]['delay'].append(metrics.average_delay)

                print(f"✓ (FND={metrics.fnd or 'N/A'}, PDR={metrics.pdr:.1f}%)")

        self.results['density'] = dict(results)
        return results

    def run_traffic_analysis(self):
        """
        سناریو 2: تحلیل ترافیک متغیر
        Scenario 2: Variable Traffic Analysis

        بررسی رفتار الگوریتم‌ها با بارهای ترافیکی مختلف
        Analyze algorithm behavior with varying traffic loads
        """
        self.print_section_header(
            "سناریو 2: تحلیل ترافیک متغیر - Scenario 2: Traffic Analysis"
        )

        traffic_levels = {
            'Low': 3,      # 3 بسته در هر راند
            'Medium': 5,   # 5 بسته در هر راند
            'High': 10     # 10 بسته در هر راند
        }

        algorithms = [
            LEACH(),
            PEGASIS(),
            OSPF(),
            NN_ILEACH(),
            DOS_RL(),
            MSSO_FCM(),
            PGAECR(),
            WOAD3QN_RP(),
            GN_DQN(),
        ]

        results = defaultdict(lambda: defaultdict(list))

        config = SimulationConfig(
            num_nodes=100,
            area_size=100.0,
            sink_position=(50.0, 50.0),
            comm_range=30.0,
            initial_energy=0.5,
            max_rounds=300,
            seed=42
        )

        for traffic_name, packets_per_round in traffic_levels.items():
            print(f"\n📊 بار ترافیک: {traffic_name} ({packets_per_round} بسته/راند)")
            print(f"   Traffic Load: {traffic_name} ({packets_per_round} packets/round)")

            for algo in algorithms:
                print(f"   🔬 {algo.algorithm_name}...", end=' ')
                metrics = self.run_single_simulation(
                    algo, config, max_rounds=300, packets_per_round=packets_per_round
                )

                results[algo.algorithm_name]['traffic_level'].append(traffic_name)
                results[algo.algorithm_name]['fnd'].append(metrics.fnd or 300)
                results[algo.algorithm_name]['pdr'].append(metrics.pdr)
                results[algo.algorithm_name]['energy_efficiency'].append(metrics.energy_efficiency)
                results[algo.algorithm_name]['throughput'].append(metrics.throughput)
                results[algo.algorithm_name]['energy_consumed'].append(metrics.total_energy_consumed_mJ)

                print(f"✓ (PDR={metrics.pdr:.1f}%, Throughput={metrics.throughput:.2f})")

        self.results['traffic'] = dict(results)
        return results

    def run_complete_comparison(self):
        """
        سناریو 3: مقایسه کامل
        Scenario 3: Complete Comparison

        مقایسه جامع همه الگوریتم‌ها در شرایط استاندارد
        Comprehensive comparison of all algorithms under standard conditions
        """
        self.print_section_header(
            "سناریو 3: مقایسه جامع - Scenario 3: Complete Comparison"
        )

        algorithms = [
            LEACH(),
            PEGASIS(),
            OSPF(),
            NN_ILEACH(),
            DOS_RL(),
            MSSO_FCM(),
            PGAECR(),
            WOAD3QN_RP(),
            GN_DQN(),
        ]

        config = SimulationConfig(
            num_nodes=100,
            area_size=100.0,
            sink_position=(50.0, 50.0),
            comm_range=30.0,
            initial_energy=0.5,
            max_rounds=500,
            seed=42
        )

        print(f"📊 شرایط شبیه‌سازی:")
        print(f"   • نودها: {config.num_nodes}")
        print(f"   • ناحیه: {config.area_size}×{config.area_size}m²")
        print(f"   • انرژی اولیه: {config.initial_energy}J")
        print(f"   • راندهای شبیه‌سازی: {config.max_rounds}")
        print(f"   • مدل انرژی: First-Order Radio Model")
        print(f"     - E_elec: {self.energy_model.E_elec} nJ/bit")
        print(f"     - ε_fs: {self.energy_model.epsilon_fs} pJ/bit/m²")
        print(f"     - ε_mp: {self.energy_model.epsilon_mp} pJ/bit/m⁴")

        results = {}

        for algo in algorithms:
            print(f"\n🔬 {algo.algorithm_name}")
            print(f"   {algo.get_description()}")
            metrics = self.run_single_simulation(algo, config, max_rounds=500, verbose=False)
            results[algo.algorithm_name] = metrics

            print(f"   ✓ FND: {metrics.fnd or 'N/A'} راند")
            print(f"   ✓ PDR: {metrics.pdr:.2f}%")
            print(f"   ✓ کارایی انرژی: {metrics.energy_efficiency:.2f} بسته/ژول")
            print(f"   ✓ توان عبور: {metrics.throughput:.2f} بسته/ثانیه")

        self.results['complete'] = results
        return results

    def generate_plots(self):
        """تولید نمودارها"""
        self.print_section_header("تولید نمودارهای تحلیلی - Generating Analysis Plots")

        output_dir = Path("simulation_results")
        output_dir.mkdir(exist_ok=True)

        # نمودار 1: FND vs Density
        if 'density' in self.results:
            self.plot_density_analysis(output_dir)

        # نمودار 2: Traffic Analysis
        if 'traffic' in self.results:
            self.plot_traffic_analysis(output_dir)

        # نمودار 3: Complete Comparison
        if 'complete' in self.results:
            self.plot_complete_comparison(output_dir)

        print(f"\n✅ نمودارها در پوشه '{output_dir}' ذخیره شدند")

    def plot_density_analysis(self, output_dir: Path):
        """نمودار تحلیل چگالی"""
        results = self.results['density']

        # Figure 1: FND vs Node Count
        plt.figure(figsize=(12, 8))
        for algo_name, data in results.items():
            plt.plot(
                data['node_count'],
                data['fnd'],
                marker=self.markers.get(algo_name, 'o'),
                color=self.colors.get(algo_name, 'gray'),
                label=algo_name,
                linewidth=2,
                markersize=8
            )
        plt.xlabel('تعداد نودها - Node Count', fontsize=12, fontweight='bold')
        plt.ylabel('FND (راند) - FND (Rounds)', fontsize=12, fontweight='bold')
        plt.title('تحلیل طول عمر شبکه بر حسب چگالی\nNetwork Lifetime vs Density',
                  fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best', fontsize=10)
        plt.tight_layout()
        plt.savefig(output_dir / 'density_fnd.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Figure 2: PDR vs Node Count
        plt.figure(figsize=(12, 8))
        for algo_name, data in results.items():
            plt.plot(
                data['node_count'],
                data['pdr'],
                marker=self.markers.get(algo_name, 'o'),
                color=self.colors.get(algo_name, 'gray'),
                label=algo_name,
                linewidth=2,
                markersize=8
            )
        plt.xlabel('تعداد نودها - Node Count', fontsize=12, fontweight='bold')
        plt.ylabel('PDR (%)', fontsize=12, fontweight='bold')
        plt.title('نسبت تحویل بسته بر حسب چگالی\nPacket Delivery Ratio vs Density',
                  fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best', fontsize=10)
        plt.tight_layout()
        plt.savefig(output_dir / 'density_pdr.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("   ✓ نمودارهای تحلیل چگالی ذخیره شد")

    def plot_traffic_analysis(self, output_dir: Path):
        """نمودار تحلیل ترافیک"""
        results = self.results['traffic']

        # Figure: Energy Consumption vs Traffic
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        traffic_labels = ['Low', 'Medium', 'High']
        x_pos = np.arange(len(traffic_labels))
        width = 0.08

        for i, (algo_name, data) in enumerate(results.items()):
            offset = (i - len(results)/2) * width
            ax1.bar(x_pos + offset, data['energy_consumed'], width,
                   label=algo_name, color=self.colors.get(algo_name, 'gray'))
            ax2.bar(x_pos + offset, data['pdr'], width,
                   label=algo_name, color=self.colors.get(algo_name, 'gray'))

        ax1.set_xlabel('بار ترافیک - Traffic Load', fontweight='bold')
        ax1.set_ylabel('مصرف انرژی (mJ) - Energy (mJ)', fontweight='bold')
        ax1.set_title('مصرف انرژی بر حسب ترافیک\nEnergy Consumption vs Traffic', fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(traffic_labels)
        ax1.legend(fontsize=8, ncol=2)
        ax1.grid(True, alpha=0.3, axis='y')

        ax2.set_xlabel('بار ترافیک - Traffic Load', fontweight='bold')
        ax2.set_ylabel('PDR (%)', fontweight='bold')
        ax2.set_title('نسبت تحویل بسته بر حسب ترافیک\nPDR vs Traffic', fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(traffic_labels)
        ax2.legend(fontsize=8, ncol=2)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_dir / 'traffic_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("   ✓ نمودارهای تحلیل ترافیک ذخیره شد")

    def plot_complete_comparison(self, output_dir: Path):
        """نمودار مقایسه کامل"""
        results = self.results['complete']

        # Prepare data
        algo_names = list(results.keys())
        metrics_data = {
            'FND': [results[a].fnd or 500 for a in algo_names],
            'PDR (%)': [results[a].pdr for a in algo_names],
            'Energy Eff.\n(pkt/J)': [results[a].energy_efficiency for a in algo_names],
            'Throughput\n(pkt/s)': [results[a].throughput for a in algo_names],
        }

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.ravel()

        for idx, (metric_name, values) in enumerate(metrics_data.items()):
            ax = axes[idx]
            colors_list = [self.colors.get(name, 'gray') for name in algo_names]
            bars = ax.bar(range(len(algo_names)), values, color=colors_list, edgecolor='black', linewidth=1.5)

            ax.set_xlabel('الگوریتم - Algorithm', fontweight='bold', fontsize=11)
            ax.set_ylabel(metric_name, fontweight='bold', fontsize=11)
            ax.set_title(f'مقایسه {metric_name}\nComparison of {metric_name}',
                        fontweight='bold', fontsize=12)
            ax.set_xticks(range(len(algo_names)))
            ax.set_xticklabels(algo_names, rotation=45, ha='right', fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=8, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_dir / 'complete_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("   ✓ نمودارهای مقایسه کامل ذخیره شد")

    def generate_report(self):
        """تولید گزارش جامع"""
        self.print_section_header("تولید گزارش جامع - Generating Comprehensive Report")

        report_file = Path("COMPREHENSIVE_SIMULATION_REPORT.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# گزارش جامع شبیه‌سازی الگوریتم‌های مسیریابی WSN-SDN\n")
            f.write("# Comprehensive Simulation Report - WSN-SDN Routing Algorithms\n\n")
            f.write(f"**تاریخ:** 1404/11/12 - 2026-01-31\n\n")
            f.write("---\n\n")

            # سناریو 1: چگالی
            if 'density' in self.results:
                f.write("## سناریو 1: تحلیل چگالی شبکه\n")
                f.write("## Scenario 1: Network Density Analysis\n\n")
                f.write("### نتایج:\n\n")
                f.write("| الگوریتم | 50 نود | 100 نود | 150 نود | 200 نود | 250 نود |\n")
                f.write("|----------|--------|---------|---------|---------|----------|\n")

                for algo_name, data in self.results['density'].items():
                    f.write(f"| {algo_name} |")
                    for fnd in data['fnd']:
                        f.write(f" {fnd} |")
                    f.write("\n")
                f.write("\n")

            # سناریو 2: ترافیک
            if 'traffic' in self.results:
                f.write("## سناریو 2: تحلیل ترافیک متغیر\n")
                f.write("## Scenario 2: Variable Traffic Analysis\n\n")

            # سناریو 3: مقایسه کامل
            if 'complete' in self.results:
                f.write("## سناریو 3: مقایسه کامل\n")
                f.write("## Scenario 3: Complete Comparison\n\n")
                f.write("| الگوریتم | FND | PDR (%) | کارایی انرژی | توان عبور |\n")
                f.write("|----------|-----|---------|---------------|------------|\n")

                for algo_name, metrics in self.results['complete'].items():
                    f.write(f"| {algo_name} | {metrics.fnd or 'N/A'} | "
                           f"{metrics.pdr:.2f} | {metrics.energy_efficiency:.2f} | "
                           f"{metrics.throughput:.2f} |\n")
                f.write("\n")

        print(f"   ✓ گزارش در '{report_file}' ذخیره شد")


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """اجرای اصلی"""
    print("="*100)
    print("شبیه‌سازی جامع و تخصصی الگوریتم‌های مسیریابی WSN-SDN".center(100))
    print("Comprehensive Professional Simulation of WSN-SDN Routing Algorithms".center(100))
    print("="*100)
    print("\nسطح: دکتری / پروفسوری - Level: PhD / Professorial")
    print("تاریخ: 1404/11/12 - 2026-01-31\n")

    simulator = ComprehensiveProfessionalSimulator()

    # سناریو 1: تحلیل چگالی
    print("\n🚀 شروع سناریو 1: تحلیل چگالی...")
    simulator.run_density_analysis()

    # سناریو 2: تحلیل ترافیک
    print("\n🚀 شروع سناریو 2: تحلیل ترافیک...")
    simulator.run_traffic_analysis()

    # سناریو 3: مقایسه کامل
    print("\n🚀 شروع سناریو 3: مقایسه کامل...")
    simulator.run_complete_comparison()

    # تولید نمودارها
    print("\n🎨 تولید نمودارها...")
    simulator.generate_plots()

    # تولید گزارش
    print("\n📄 تولید گزارش جامع...")
    simulator.generate_report()

    print("\n" + "="*100)
    print("✅ شبیه‌سازی کامل شد!".center(100))
    print("✅ Simulation Completed!".center(100))
    print("="*100)
    print("\n📁 خروجی‌ها:")
    print("   • نمودارها: simulation_results/")
    print("   • گزارش: COMPREHENSIVE_SIMULATION_REPORT.md")
    print()


if __name__ == "__main__":
    main()
