# 大学生志愿服务场域行动—结构互构：基于多智能体仿真的政策实验研究

**Action-Structure Interplay in University Volunteering Field: An Agent-Based Policy Experiment**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 项目概述

本研究整合场域理论与行动—结构互构框架，利用大学生志愿服务调查数据（张网成，2016）进行参数校准，构建了基于多智能体仿真（Agent-Based Modeling, ABM）的志愿服务场域动态演化模型。研究系统探索了学业压力、挫折感与满意度三个机制对成员流失的独立与交互效应，并通过8组蒙特卡洛仿真实验评估不同干预策略的效应与机制。

**核心发现：**
- 学业压力与挫折感构成成员流失的双轨驱动机制（独立效应）
- 减少招募规模是最具杠杆效应的单一干预手段（学年流失率从43.0%降至34.6%）
- 激励政策存在非线性区间效应（存在服务量下限与上限）
- 取消届际更替限制呈现"短期改善、长期恶化"的逆转模式

## 目录结构

```
abm-volunteer-simulation/
├── paper/
│   ├── paper_final.tex      # 论文LaTeX源码（正式版）
│   ├── report.tex           # 论文LaTeX源码（工作版）
│   ├── report.pdf           # 编译PDF
│   ├── refs.bib             # 参考文献数据库
│   └── fig*.png             # 图表文件
├── code/
│   ├── abm_model.py         # ABM核心模型（Mesa框架）
│   ├── reproduce_empirical.py  # 实证数据分析脚本
│   ├── run_exp.py           # 仿真实验主脚本（8组实验）
│   └── run_figures.py       # 图表生成脚本
├── data/
│   └── empirical/
│       ├── 09_three_regression_comparison_final.csv  # 三套回归结果
│       ├── 10_frustration_attrition_crosstab.csv    # 挫折感×流失交叉表
│       ├── 11_descriptive_statistics.csv            # 描述性统计
│       └── deprecated_*                              # 已废弃的中间结果
├── results/
│   ├── all_results.pkl      # 所有实验结果（pickle格式）
│   ├── fig1_overall_trends.png
│   ├── fig2_individual_behaviors.png
│   ├── fig3_population_pyramid.png
│   ├── fig4_calibration.png
│   ├── fig5_mechanisms.png
│   ├── fig6_sensitivity.png
│   ├── 00_experiment_summary_v9.2_final.csv
│   └── 02_model_parameters.csv
├── docs/
│   ├── model_specification.md   # 模型规范（ODD协议）
│   ├── replication_guide.md      # 复现指南
│   └── method_notes.md          # 方法说明
├── verification_package/         # 存档：v9.2最终版验证包
├── archive/                     # 旧版本归档
├── .gitignore
├── requirements.txt             # Python依赖
├── environment.yml              # Conda环境
├── CHANGELOG.md
├── FILES.md
└── verify_results.py            # 根目录验证脚本
```

## 研究方法

本研究采用"实证分析 + ABM仿真"的混合方法路径：

1. **实证分析**：对572份大学生志愿者问卷进行三套稳健性逻辑回归，识别流失的关键预测变量并估计效应量
2. **ABM建模**：基于Mesa框架构建志愿服务场域多智能体仿真模型，以实证数据驱动参数校准
3. **政策实验**：通过8组蒙特卡洛仿真实验系统评估不同干预策略的效应与机制

### ABM模型三机制

| 机制 | 行为规则 | 核心参数 |
|------|----------|----------|
| 学业压力 | 压力随年级线性增长（年级1: 0.30 → 年级4: 0.80） | $P_{\text{acad}}$ |
| 挫折感 | 期望-现实差距累积，过度投入加速积累 | $\Delta F = P_{\text{acad}} \times 0.01 + \max(0, 0.50 - S_t) \times 0.03$ |
| 满意度 | 服务质量体验动态更新，服务量超载后递减 | $\Delta S = q \times (1 - S_t) \times 0.10$ |

## 快速运行

### 环境配置

```bash
# 方法1: pip
pip install mesa numpy pandas scipy scikit-learn matplotlib seaborn openpyxl

# 方法2: Conda
conda env create -f environment.yml
conda activate abm-volunteer
```

### 运行全部实验

```bash
cd code/
python run_exp.py
```

这将运行8组仿真实验（约需2分钟），生成结果文件至 `results/`。

### 仅生成图表

```bash
python run_figures.py
```

### 实证分析

```bash
python reproduce_empirical.py
```

### 验证结果

```bash
python verify_results.py
```

## 主要结果

| 实验 | 学年流失率 | 管理层人数 | 活跃人数 | 创新次数 | 晋升率 |
|------|-----------|-----------|---------|---------|-------|
| 基线（校准） | 43.0% | 88.8 | 605 | 105 | 25.5% |
| 减少招募目标 | **34.6%** | 78.3 | 420 | 106 | **32.4%** |
| 双重干预 | **32.9%** | 79.9 | 422 | 105 | **33.3%** |
| 容量控制 | 37.5% | 91.4 | 609 | 105 | 27.2% |
| 无届际更替 | 40.5% | 78.1 | 801 | 101 | 25.5% |

*注：所有结果为15次蒙特卡洛重复均值*

## 数据说明

- **实证数据**：张网成（2016）《大学生志愿者挫折反应及对策调查数据》，原始样本592份，有效样本572份（本科1-3年级552份）
- **数据限制**：原始572条记录中存在大量精确重复记录，去重后唯一记录137条；大四及研究生样本量过少（各不足20人），主分析限于本科1-3年级
- **原始数据**（如需申请）：请联系原作者

## 引用本项目

```bibtex
@misc{zhangwangcheng2016,
  author = {张网成},
  title = {大学生志愿者挫折反应及对策调查数据},
  year = {2016},
  institution = {北京师范大学},
  address = {北京}
}

@article{fei2025abm,
  title = {大学生志愿服务场域的行动与结构互构——基于多智能体仿真的政策实验研究},
  author = {张网成 and 牛雪霏 and Zhuoer Yu},
  journal = {待投稿},
  year = {2025}
}
```

## 许可证

本项目采用 [MIT License](LICENSE)。数据版权由原始数据提供方所有。

## 联系方式

- 通信作者：Yu Zhuoer (yzhuoer@example.edu)
- 机构：Department of Computer Science, Malmö University
