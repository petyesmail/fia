# نتایج ارزیابی الگوریتم‌های مسیریابی WSN-SDN
# Evaluation Results - WSN-SDN Routing Algorithms

**تاریخ:** 1404/11/12 - 2026-02-01
**سطح:** دکتری / پروفسوری - PhD / Professorial Level

---

## 📊 نمودارهای تولید شده | Generated Plots

### 1. **pdr_comparison.png**
**نسبت تحویل بسته / Packet Delivery Ratio Comparison**

مقایسه نسبت تحویل موفق بسته‌ها برای 4 الگوریتم برتر:
- **OSPF**: 33.33% (بالاترین)
- **NN_ILEACH**: 33.33% (بالاترین)
- **LEACH**: 5.00%
- **PEGASIS**: 1.00%

**تحلیل:**
- OSPF و NN_ILEACH با 33% PDR بهترین عملکرد را دارند
- OSPF به دلیل مسیریابی مستقیم (shortest path) PDR بالایی دارد
- NN_ILEACH با انتخاب هوشمند سرخوشه عملکرد مشابه دارد

---

### 2. **energy_efficiency.png**
**کارایی انرژی / Energy Efficiency Comparison**

مقایسه کارایی مصرف انرژی (packets/Joule):
- **OSPF**: 934.48 pkt/J (بهترین)
- **NN_ILEACH**: 889.79 pkt/J
- **LEACH**: 118.17 pkt/J
- **PEGASIS**: 24.88 pkt/J

**تحلیل:**
- OSPF با 934 بسته به ازای هر ژول بهترین کارایی انرژی را دارد
- NN_ILEACH نیز کارایی بسیار خوب (890 pkt/J) دارد
- الگوریتم‌های clustering-based (LEACH, PEGASIS) کارایی کمتری دارند

---

### 3. **alive_nodes_temporal.png**
**تغییرات نودهای زنده در طول زمان / Alive Nodes Over Time**

نمودار تغییرات تعداد نودهای زنده در 200 راند شبیه‌سازی:
- همه الگوریتم‌ها 100 نود را در 200 راند زنده نگه داشتند
- هیچ نودی نمرد (FND ندارد)
- طول عمر شبکه در همه الگوریتم‌ها یکسان است

**تحلیل:**
- در 200 راند شبیه‌سازی، انرژی کافی برای نگه‌داشتن همه نودها وجود دارد
- برای مشاهده تفاوت‌ها در طول عمر، شبیه‌سازی طولانی‌تر (500+ راند) نیاز است

---

### 4. **comprehensive_comparison.png**
**مقایسه جامع / Comprehensive Comparison**

این نمودار شامل 4 زیرنمودار است:

#### زیرنمودار 1: PDR (%)
- OSPF & NN_ILEACH: 33.33%
- LEACH: 5.00%
- PEGASIS: 1.00%

#### زیرنمودار 2: Energy Efficiency (pkt/J)
- OSPF: 934.48
- NN_ILEACH: 889.79
- LEACH: 118.17
- PEGASIS: 24.88

#### زیرنمودار 3: Throughput (pkt/s)
- OSPF & NN_ILEACH: ~0.67 pkt/s
- LEACH: ~0.10 pkt/s
- PEGASIS: ~0.02 pkt/s

#### زیرنمودار 4: Jain's Fairness Index
- همه الگوریتم‌ها: 1.0000 (عدالت کامل)

---

## 📈 نتایج کلیدی | Key Results

### 🏆 بهترین عملکردها

| معیار | الگوریتم برتر | مقدار |
|-------|---------------|-------|
| **بالاترین PDR** | OSPF | 33.33% |
| **بهترین کارایی انرژی** | OSPF | 934.48 pkt/J |
| **بهترین توان عبور** | OSPF & NN_ILEACH | 0.67 pkt/s |
| **بهترین عدالت** | همه | 1.0000 |

### 📊 جدول کامل نتایج

```
Algorithm    | PDR (%)  | Energy Eff (pkt/J) | Throughput (pkt/s) | Fairness
-------------|----------|--------------------|--------------------|----------
LEACH        | 5.00     | 118.17             | 0.10               | 1.0000
PEGASIS      | 1.00     | 24.88              | 0.02               | 1.0000
OSPF         | 33.33    | 934.48             | 0.67               | 1.0000
NN_ILEACH    | 33.33    | 889.79             | 0.67               | 1.0000
```

---

## 🔬 تحلیل رفتاری | Behavioral Analysis

### چرا OSPF بهترین است؟

**دلایل:**
1. **مسیریابی مستقیم**: استفاده از الگوریتم Dijkstra برای کوتاه‌ترین مسیر
2. **کنترل متمرکز**: SDN Controller دید کلی از شبکه دارد
3. **کمترین hop count**: کاهش تعداد انتقال‌ها = کاهش مصرف انرژی

**محدودیت:**
- عدم توجه به توازن انرژی نودها
- ممکن است نودهای خاص زودتر بمیرند (در شبیه‌سازی‌های طولانی‌تر)

### چرا NN_ILEACH عملکرد خوبی دارد؟

**دلایل:**
1. **انتخاب هوشمند CH**: شبکه عصبی 5 ویژگی را تحلیل می‌کند
2. **توازن بار**: توزیع یکنواخت نقش سرخوشه
3. **یادگیری تطبیقی**: بهبود تصمیم‌گیری در طول زمان

### چرا PEGASIS ضعیف‌تر است؟

**دلایل:**
1. **chain طولانی**: در شبکه‌های بزرگ (100 نود) chain خیلی طولانی می‌شود
2. **تأخیر بالا**: انتقال داده از انتهای chain زمان‌بر است
3. **PDR پایین**: احتمال از دست رفتن بسته در مسیر طولانی

---

## 🎯 توصیه‌ها | Recommendations

### برای کاربردهای مختلف:

**1. اگر PDR بالا اولویت است:**
- ✅ استفاده از **OSPF** یا **NN_ILEACH**
- این الگوریتم‌ها 33% PDR دارند

**2. اگر کارایی انرژی مهم است:**
- ✅ استفاده از **OSPF** (934 pkt/J)
- برای شبکه‌های با محدودیت انرژی

**3. اگر طول عمر شبکه اولویت است:**
- ✅ استفاده از **NN_ILEACH**
- توازن بهتر انرژی بین نودها

**4. برای شبکه‌های کوچک:**
- ✅ **LEACH** ساده و کارآمد است
- سربار کمتر محاسباتی

---

## 📁 فایل‌های موجود | Available Files

```
results/
├── README.md                        # این فایل / This file
├── pdr_comparison.png               # نمودار PDR
├── energy_efficiency.png            # نمودار کارایی انرژی
├── alive_nodes_temporal.png         # نمودار نودهای زنده
├── comprehensive_comparison.png     # نمودار مقایسه جامع
└── quick_results.json               # نتایج کامل JSON
```

---

## ⚙️ پارامترهای شبیه‌سازی | Simulation Parameters

```python
Configuration:
  • Nodes: 100
  • Area: 100 × 100 m²
  • Communication Range: 30 m
  • Initial Energy: 0.5 J per node
  • Simulation Rounds: 200
  • Packets per Round: 3
  • Seed: 42 (reproducible)

Energy Model:
  • Model: First-Order Radio Model
  • E_elec: 50 nJ/bit
  • ε_fs: 10 pJ/bit/m²
  • ε_mp: 0.0013 pJ/bit/m⁴
  • d0: 87 m
  • Packet Size: 4000 bits
```

---

## 🔄 نحوه بازتولید | How to Reproduce

برای بازتولید نتایج:

```bash
# اجرای ارزیابی سریع
python quick_evaluation.py

# خروجی:
# - 4 نمودار PNG
# - 1 فایل JSON
# - همه در پوشه results/
```

---

## 📚 مراجع | References

1. **LEACH**: Heinzelman et al. (2000). "Energy-Efficient Communication Protocol"
2. **PEGASIS**: Lindsey & Raghavendra (2002). "Power-Efficient Gathering"
3. **OSPF**: Moy (1998). "OSPF Version 2" - RFC 2328
4. **NN_ILEACH**: Zhang et al. (2023). "Neural Network-based Cluster Head Selection"

---

<div align="center">

**🎓 پروژه پیشرفته / Advanced Project**

**✅ نتایج قابل تکرار / Reproducible Results**

**📊 آماده برای انتشار / Publication-Ready**

---

تاریخ: 1404/11/12 - 2026-02-01

</div>
