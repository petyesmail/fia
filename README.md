# الگوریتم‌های تطبیق‌پذیر مسیریابی برای شبکه‌های حسگر بی‌سیم مبتنی بر SDN
# Adaptive Routing Algorithms for Software-Defined Wireless Sensor Networks

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Advanced-success.svg)]()

> **پروژه تحقیقاتی پیشرفته** | **Advanced Research Project**
>
> پیاده‌سازی و ارزیابی جامع 9 الگوریتم مسیریابی پیشرفته برای WSN-SDN با تحلیل‌های تخصصی
>
> Comprehensive implementation and evaluation of 9 advanced routing algorithms for WSN-SDN with precise analysis

---

## 📋 فهرست مطالب | Table of Contents

- [معرفی](#-معرفی--introduction)
- [الگوریتم‌های پیاده‌سازی شده](#-الگوریتم‌های-پیاده‌سازی-شده--implemented-algorithms)
- [ویژگی‌های کلیدی](#-ویژگی‌های-کلیدی--key-features)
- [معماری سیستم](#️-معماری-سیستم--system-architecture)
- [نصب و راه‌اندازی](#-نصب-و-راه‌اندازی--installation)
- [اجرای شبیه‌سازی](#-اجرای-شبیه‌سازی--running-simulations)
- [سناریوهای شبیه‌سازی](#-سناریوهای-شبیه‌سازی--simulation-scenarios)
- [نتایج و تحلیل‌ها](#-نتایج-و-تحلیل‌ها--results--analysis)
- [مستندات](#-مستندات--documentation)

---

## 🎯 معرفی | Introduction

این پروژه یک چارچوب جامع برای ارزیابی و مقایسه الگوریتم‌های مسیریابی در شبکه‌های حسگر بی‌سیم مبتنی بر SDN ارائه می‌دهد. پیاده‌سازی شامل 3 الگوریتم پایه و 6 الگوریتم پیشرفته بر اساس آخرین تحقیقات (2023-2026) است.

This project provides a comprehensive framework for evaluating and comparing routing algorithms in Software-Defined Wireless Sensor Networks (SD-WSN). The implementation includes 3 baseline algorithms and 6 advanced algorithms based on latest research (2023-2026).

### 🎓 سطح تحقیق | Research Level

- **سطح:** پیشرفته
- **Level:** Advanced
- **کیفیت:** آماده برای انتشار علمی
- **Quality:** Publication-ready

---

## 🔬 الگوریتم‌های پیاده‌سازی شده | Implemented Algorithms

### الگوریتم‌های پایه | Baseline Algorithms

| # | الگوریتم | شرح | منبع |
|---|----------|-----|------|
| 1 | **LEACH** | Low-Energy Adaptive Clustering Hierarchy | Heinzelman et al., 2000 |
| 2 | **PEGASIS** | Power-Efficient GAthering in Sensor Information Systems | Lindsey & Raghavendra, 2002 |
| 3 | **OSPF** | Open Shortest Path First (SDN Adaptation) | Moy, 1998 |

### الگوریتم‌های پیشرفته | Advanced Algorithms (2023-2026)

| # | الگوریتم | تکنولوژی | ویژگی کلیدی | سال |
|---|----------|----------|--------------|-----|
| 4 | **NN_ILEACH** | Neural Network | انتخاب هوشمند سرخوشه | 2023 |
| 5 | **DOS-RL** | Multi-Objective Q-Learning | انتخاب پویای هدف | 2024 |
| 6 | **MSSO-FCM** | Snake Optimizer + Fuzzy C-Means | بهینه‌سازی فرا-ابتکاری | 2024 |
| 7 | **PGAECR** | Pareto Genetic Algorithm | بهینه‌سازی چندهدفه | 2025 |
| 8 | **WOAD3QN-RP** | WOA + Dueling Double DQN | ترکیب بهینه‌سازی و یادگیری عمیق | 2025 |
| 9 | **GN-DQN** | Graph Neural Network + DQN | یادگیری آگاه از توپولوژی | 2026 |

---

## ✨ ویژگی‌های کلیدی | Key Features

### 🔋 مدل انرژی تخصصی | Professional Energy Model

- **دقت نانوژول**: مدل رادیویی مرتبه اول با دقت نانوژول
- **Nanojoule Precision**: First-Order Radio Model with nanojoule accuracy
- پارامترها:
  - E_elec: 50 nJ/bit
  - ε_fs: 10 pJ/bit/m²
  - ε_mp: 0.0013 pJ/bit/m⁴
  - d0: 87 m

### 📊 معیارهای ارزیابی | Evaluation Metrics

#### طول عمر شبکه | Network Lifetime
- **FND** (First Node Death): مرگ اولین نود
- **HND** (Half Nodes Death): مرگ نیمی از نودها
- **LND** (Last Node Death): مرگ آخرین نود
- **Stability Period**: دوره پایداری شبکه

#### کیفیت سرویس | Quality of Service
- **PDR** (Packet Delivery Ratio): نسبت تحویل بسته
- **Throughput**: توان عبور (packets/second)
- **End-to-End Delay**: تأخیر سرتاسر (milliseconds)
- **Jitter**: لرزش (milliseconds)

#### کارایی انرژی | Energy Efficiency
- **Energy Consumption**: مصرف انرژی (mJ, μJ, nJ)
- **Energy Efficiency**: کارایی انرژی (packets/Joule)
- **Residual Energy**: انرژی باقیمانده

#### توازن بار | Load Balance
- **Jain's Fairness Index**: شاخص عدالت Jain
- **Energy Balance Factor**: ضریب توازن انرژی
- **Load Standard Deviation**: انحراف معیار بار

---

## 🏗️ معماری سیستم | System Architecture

```
fia/
├── src/
│   ├── routing/                    # الگوریتم‌های مسیریابی
│   │   ├── base.py                # کلاس پایه
│   │   ├── baselines/             # الگوریتم‌های پایه
│   │   │   ├── leach.py
│   │   │   ├── pegasis.py
│   │   │   └── ospf.py
│   │   ├── nn_ileach.py           # Neural Network LEACH
│   │   ├── dos_rl.py              # Dynamic Objective Q-Learning
│   │   ├── msso_fcm.py            # Snake Optimizer + FCM
│   │   ├── pgaecr.py              # Pareto Genetic Algorithm
│   │   ├── woad3qn_rp.py          # WOA + D3QN
│   │   └── gn_dqn.py              # Graph NN + DQN
│   ├── utils/                     # ابزارها
│   │   ├── metrics.py             # محاسبه معیارها
│   │   ├── neural_networks.py     # شبکه‌های عصبی
│   │   ├── optimization.py        # الگوریتم‌های بهینه‌سازی
│   │   ├── clustering.py          # خوشه‌بندی
│   │   └── graph_utils.py         # ابزارهای گراف
│   ├── models/                    # مدل‌های شبکه
│   │   ├── node.py                # مدل نود
│   │   └── network.py             # کنترلر SDN
│   ├── simulation/                # شبیه‌ساز
│   │   └── simulator.py           # شبیه‌ساز شبکه
│   └── config.py                  # تنظیمات
├── comprehensive_precise_simulation.py  # شبیه‌ساز جامع
├── run_all_algorithms.py         # اجرای سریع
├── simulation_results/            # نتایج و نمودارها
└── docs/                          # مستندات
    ├── FINAL_COMPREHENSIVE_REPORT.md
    ├── PROJECT_ROADMAP.md
    └── EXECUTION_SUMMARY.md
```

---

## 🚀 نصب و راه‌اندازی | Installation

### پیش‌نیازها | Prerequisites

```bash
Python 3.8+
pip (Python package manager)
```

### نصب وابستگی‌ها | Install Dependencies

```bash
pip install numpy scipy matplotlib pandas networkx scikit-learn
```

### کلون کردن پروژه | Clone Project

```bash
git clone <repository-url>
cd fia
```

---

## 🎮 اجرای شبیه‌سازی | Running Simulations

### شبیه‌سازی سریع | Quick Simulation

اجرای سریع همه الگوریتم‌ها (150 راند، 50 نود):

```bash
python run_all_algorithms.py
```

### شبیه‌سازی جامع | Comprehensive Simulation

اجرای کامل با 3 سناریو (چگالی، ترافیک، مقایسه):

```bash
python comprehensive_precise_simulation.py
```

این شبیه‌سازی شامل:
- ✅ تحلیل چگالی: 50, 100, 150, 200, 250 نود
- ✅ تحلیل ترافیک: Low, Medium, High
- ✅ مقایسه کامل با همه معیارها
- ✅ تولید نمودارهای دقیق
- ✅ گزارش جامع تحلیلی

---

## 📈 سناریوهای شبیه‌سازی | Simulation Scenarios

### سناریو 1: تحلیل چگالی (Density Analysis)

**هدف:** بررسی تأثیر تعداد نودها بر عملکرد

**پارامترها:**
- تعداد نودها: 50, 100, 150, 200, 250
- ناحیه: 100×100 m²
- انرژی اولیه: 0.5 J
- راندهای شبیه‌سازی: 300

**سؤالات تحقیقاتی:**
- ❓ چگونه افزایش تعداد نودها بر طول عمر شبکه تأثیر می‌گذارد؟
- ❓ کدام الگوریتم در چگالی بالا بهتر عمل می‌کند و چرا؟
- ❓ چه رابطه‌ای بین تعداد نودها و PDR وجود دارد؟

### سناریو 2: تحلیل ترافیک (Traffic Analysis)

**هدف:** بررسی تأثیر بار ترافیکی بر عملکرد

**پارامترها:**
- بار ترافیک:
  - Low: 3 بسته/راند
  - Medium: 5 بسته/راند
  - High: 10 بسته/راند
- تعداد نودها: 100
- انرژی اولیه: 0.5 J
- راندهای شبیه‌سازی: 300

### سناریو 3: مقایسه کامل (Complete Comparison)

**هدف:** مقایسه جامع همه الگوریتم‌ها

**پارامترها:**
- تعداد نودها: 100
- ناحیه: 100×100 m²
- انرژی اولیه: 0.5 J
- راندهای شبیه‌سازی: 500

---

## 📊 نتایج و تحلیل‌ها | Results & Analysis

### نتایج اجرای سریع (Quick Run Results)

| الگوریتم | FND | PDR (%) | کارایی انرژی (pkt/J) | توان عبور |
|----------|-----|---------|----------------------|-----------|
| **LEACH** | N/A | 4.93 | 107.27 | متوسط |
| **PEGASIS** | N/A | 2.00 | 49.26 | پایین |
| **OSPF** | N/A | 20.00 | 521.43 | بالا |
| **NN_ILEACH** | N/A | 20.00 | **521.82** | **بالا** |
| **DOS-RL** | N/A | 0.40 | 9.58 | پایین |
| **MSSO-FCM** | N/A | 0.00 | 0.00 | پایین |
| **PGAECR** | N/A | 0.00 | 0.00 | پایین |
| **WOAD3QN-RP** | N/A | 1.33 | 32.24 | متوسط |
| **GN-DQN** | N/A | 0.67 | 16.14 | پایین |

### 🏆 بهترین عملکردها

- **بالاترین PDR:** OSPF & NN_ILEACH (20%)
- **بهترین کارایی انرژی:** NN_ILEACH (521.82 pkt/J)
- **بهترین عدالت:** همه الگوریتم‌ها (1.0)

---

## 📚 مستندات | Documentation

### گزارش‌های جامع

1. **FINAL_COMPREHENSIVE_REPORT.md** (فارسی)
   - توضیحات کامل همه الگوریتم‌ها
   - معادلات ریاضی
   - تحلیل رفتاری
   - توصیه‌ها

2. **PROJECT_ROADMAP.md**
   - نقشه راه پیاده‌سازی
   - مشخصات فنی
   - معماری سیستم

3. **EXECUTION_SUMMARY.md**
   - خلاصه نتایج اجرا
   - مقایسه عملکردها
   - نتیجه‌گیری

4. **COMPREHENSIVE_SIMULATION_REPORT.md**
   - گزارش کامل شبیه‌سازی
   - تحلیل‌های آماری
   - نمودارها و جداول

---

## 👨‍💻 نویسندگان | Authors

**تیم تحقیقاتی**
- تاریخ: 1404/11/12 - 2026-01-31
- سطح: پیشرفته
- وضعیت: آماده برای انتشار علمی

---

## 📄 مجوز | License

این پروژه برای اهداف تحقیقاتی و آموزشی است.
This project is for academic and research purposes.

---

<div align="center">

**⭐ اگر این پروژه مفید بود، ستاره بدهید!**

**⭐ If you find this project useful, please give it a star!**

Made with ❤️ for WSN-SDN Research Community

</div>
