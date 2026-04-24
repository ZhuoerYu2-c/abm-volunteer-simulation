# 大学生志愿服务场域ABM仿真验证包（v9.2 完整版）

## 目录结构
```
verification_package/
├── 1_original_data/
│   ├── 大学生志愿者挫折反应及对策调查数据.sav
│   ├── 大学生志愿者挫折反应及对策调查数据.csv
│   ├── 大学生志愿者挫折反应及对策调查数据_含备注.xlsx
│   ├── 大学生志愿参与阶梯式下跌的现象分析.docx
│   ├── deprecated_logistic_regression_output.csv   ← 废弃（旧模型）
│   └── deprecated_logistic_regression_reproduced.csv ← 废弃（旧模型）
│
├── 2_empirical_analysis/
│   ├── 09_three_regression_comparison_final.csv ← 现行表1来源
│   ├── deprecated_08_robustness_regression.csv    ← 废弃（已被09替代）
│   ├── 01_descriptive_statistics.csv
│   ├── 02_frustration_vs_attrition.csv
│   ├── 03_attrition_reasons.csv
│   ├── 04_attrition_vs_non_attrition_comparison.csv
│   ├── 05_correlation_matrix.csv
│   ├── 06_logistic_regression_reproduced.csv
│   ├── 07_factor_scores_F1_F2.csv
│   └── 10_frustration_attrition_crosstab.csv
│
├── 3_model_code/
│   ├── abm_model.py      # v9.2（含全部bug修复）
│   ├── run_exp.py        # 8实验×15次MC
│   └── run_figures.py    # 6图（支持多种路径）
│
├── 4_experiment_results/
│   ├── all_results.pkl          # 最新实验结果（v9.2）
│   └── 00_experiment_summary_v9.2.csv
│
├── 5_figures/           # 6张PNG图表
├── 6_report/
│   ├── report.tex        # v9.2（14页）
│   └── report.pdf
│
├── reproduce_empirical.py  # 一键复现脚本（v9.2，已修正路径）
├── verify_results.py      # 验证脚本（v9.2，已修正路径/键名）
├── CHANGELOG.md
└── README.md
```

## 核心实验结果（v9.2，15次MC均值）

| 实验 | 学年AR | 管理层 | 活跃 | 晋升率 | 优秀项目 |
|------|--------|--------|------|--------|---------|
| 基线（校准） | 42.8% | 90.9 | 605 | 25.5% | 41.8% |
| 无届际更替 | 40.9% | 83.4 | 801 | 25.5% | 40.3% |
| 延长任期 | 42.8% | 97.9 | 614 | 25.5% | 44.1% |
| 增加经费 | 42.3% | 92.3 | 624 | 25.5% | 70.1% |
| 单一门槛激励 | 42.8% | 92.0 | 606 | 25.5% | 41.9% |
| 减少招募目标 | 34.8% | 84.9 | 426 | 32.4% | 41.9% |
| 容量控制 | 37.3% | 92.1 | 607 | 27.3% | 41.6% |
| 双重干预 | 33.1% | 85.5 | 426 | 33.4% | 42.1% |

## 独立验证步骤

```bash
# 1. 安装依赖
conda install python=3.10 mesa numpy matplotlib pandas statsmodels openpyxl scipy -y

# 2. 复现实证分析（从原始数据→表1回归）
python reproduce_empirical.py

# 3. 运行实验（8实验×15次MC，约60秒）
python run_exp.py --runs 15

# 4. 生成图表
python run_figures.py

# 5. 编译报告
xelatex report.tex

# 6. 快速验证
python verify_results.py
```

## v9.2 本次修正内容

### ABM代码修复（4个bug）
1. **挫折感初始化**：从等概率choice改为加权抽样（按问卷实际频率40/120/208/160/24）
2. **满意度更新**：修正if/elif顺序（>25在前，否则永远触发不到）
3. **创新公式**：代码与论文一致（无冗余/5）
4. **任期弹性**：20%提前卸任已标注（不是严格"到期才卸任"）

### 报告文字同步
- 基线管理层：90.7→90.9
- 届际更替：82.6→83.4
- 延长任期：95.3→97.9
- 双重干预解释：从"与exp5相同"改为"略强但边际小"

### 实证文件清理
- 废弃文件已明确标注deprecated前缀
- 现行表1来源：`09_three_regression_comparison_final.csv`

## 数据质量说明
- 原始572行：139种记录各精确重复4次，去重后137条唯一记录
- 描述性统计以572行报告；回归分析以137条唯一记录为独立样本
