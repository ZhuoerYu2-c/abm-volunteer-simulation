# 大学生志愿服务场域ABM仿真验证包（v9.2 完整版）
==================================================

## 目录结构
```
verification_package/
├── 1_original_data/
│   ├── 大学生志愿者挫折反应及对策调查数据.sav
│   ├── 大学生志愿者挫折反应及对策调查数据.csv
│   ├── 大学生志愿者挫折反应及对策调查数据_含备注.xlsx
│   ├── 大学生志愿参与阶梯式下跌的现象分析.docx
│   ├── logistic_regression_output.csv
│   └── logistic_regression_reproduced.csv
│
├── 2_empirical_analysis/
│   ├── 01_descriptive_statistics.csv
│   ├── 02_frustration_vs_attrition.csv
│   ├── 03_attrition_reasons.csv
│   ├── 04_attrition_vs_non_attrition_comparison.csv
│   ├── 05_correlation_matrix.csv
│   ├── 06_logistic_regression_reproduced.csv
│   ├── 07_factor_scores_F1_F2.csv
│   ├── 08_robustness_regression.csv       ← 旧版（废弃）
│   └── 09_three_regression_comparison.csv ← 新增三套稳健性回归
│       10_frustration_attrition_crosstab.csv
│       11_descriptive_stats_main.csv
│
├── 3_model_code/
│   ├── abm_model.py      # v9.0（含区间激励、年4=0.80修正）
│   ├── run_exp.py        # v9（8实验×15次MC）
│   └── run_figures.py    # 6图生成
│
├── 4_experiment_results/
│   ├── all_results.pkl
│   ├── 00_experiment_summary_v9.2.csv     ← v9.2完整结果
│   └── 02_model_parameters.csv
│
├── 5_figures/           # 6张PNG图表
│
├── 6_report/
│   ├── report.tex        # v9.2（14页）
│   └── report.pdf
│
├── CHANGELOG.md          # 完整修改记录
├── README.md
└── verify_results.py
```

## 核心实验结果（v9.2，15次MC均值）

| 实验 | 学年AR | 管理层 | 活跃 | 晋升率 | 优秀项目 |
|------|--------|--------|------|--------|---------|
| 基线（校准） | 42.8%±0.2 | 90.9±2.9 | 605±4 | 25.5% | 41.8% |
| 无届际更替 | 40.9%±0.3 | 83.4±3.5 | 801±6 | 25.5% | 40.3% |
| 延长任期 | 42.8%±0.3 | 97.9±2.4 | 614±3 | 25.5% | 44.1% |
| 增加经费 | 42.3%±0.3 | 92.3±4.2 | 624±5 | 25.5% | 70.1% |
| 单一门槛激励 | 42.8%±0.2 | 92.0±3.7 | 606±5 | 25.5% | 41.9% |
| 减少招募目标 | 34.8%±0.3 | 84.9±3.0 | 426±4 | 32.4% | 41.9% |
| 容量控制 | 37.3%±0.2 | 92.1±4.7 | 607±5 | 27.3% | 41.6% |
| 双重干预 | 33.1%±0.1 | 85.5±2.9 | 426±3 | 33.4% | 42.1% |

## v9.2 相比 v8.2 的主要修正

### 数据层面
- **三套稳健性回归**：原始552行 / 去重137行 / 加权频数
  - 挫折感效应稳健（β≈1.49, p<0.001）
  - 高年级效应去重后不显著（p=0.445）
  - 管理层效应方向与原始报告相反（回归中为正）
- **删除四年级样本**：大四12人+本科以上8人（样本过小）

### 模型层面
- **年级4学业压力**：0.60 → 0.80（高于大三0.70，符合现实）
- **区间激励设计**：下限（6次）/ 最优区（6-12次）/ 上限（>25次过载惩罚）
- **招募实验拆解**：减少招募目标 / 容量上限 / 双重干预三个单因素实验

### 论文层面
- 新增：参数来源表（表3）
- 新增：学业压力敏感性分析表（表2）
- 新增：22篇参考文献（含志愿留任/ABM方法文献）
- 结论语气统一（"较好校准"等）

## 独立验证步骤

```bash
# 1. 安装依赖
conda install python=3.10 numpy matplotlib pandas statsmodels openpyxl scipy -y

# 2. 复现实证分析
python reproduce_empirical.py

# 3. 运行模型
python run_exp.py --runs 15

# 4. 生成图表
python run_figures.py

# 5. 编译报告
xelatex report.tex
```

## 数据质量说明
- 原始572行：139种记录各精确重复4次，去重后137条唯一记录
- 描述性统计以572行报告（均值不变）
- 回归分析以137条唯一记录为独立样本
- 标准误和显著性在解读时需保持审慎
