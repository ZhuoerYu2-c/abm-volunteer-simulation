# 文件清单与说明

本文档列出仓库中所有文件的用途、来源与状态。

## 文件树

```
abm-volunteer-simulation/
├── paper/                     # 论文正文
│   ├── paper_final.tex        # [主] 正式版论文LaTeX源码
│   ├── report.tex             # [工作] 工作版论文（供修改）
│   ├── report.pdf             # [自动] report.tex编译产物
│   ├── report_v10.tex         # [存档] 中间版本
│   ├── refs.bib               # BibTeX参考文献数据库
│   ├── fig_calibration.png   # [自动] 校准图表
│   ├── fig_mechanisms.png    # [自动] 机制图表
│   └── fig_sensitivity.png   # [自动] 敏感性分析图表
│
├── code/                      # 模型代码
│   ├── abm_model.py           # [主] ABM核心模型（Mesa框架）
│   ├── reproduce_empirical.py # [主] 实证数据分析
│   ├── run_exp.py            # [主] 仿真实验主脚本
│   └── run_figures.py        # [主] 图表生成脚本
│
├── data/                      # 数据目录
│   └── empirical/             # 实证分析数据
│       ├── 09_three_regression_comparison_final.csv   # [生成] 三套稳健性回归结果
│       ├── 10_frustration_attrition_crosstab.csv     # [生成] 挫折感×流失交叉表
│       ├── 11_descriptive_statistics.csv             # [生成] 描述性统计
│       ├── deprecated_logistic_regression_output.csv # [废弃] 旧版回归输出
│       ├── deprecated_logistic_regression_reproduced.csv  # [废弃] 旧版回归复现
│       └── "大学生志愿者挫折反应及对策调查数据.sav"  # [原始] SPSS格式（需pyreadstat）
│           "大学生志愿者挫折反应及对策调查"数据.sav   # [原始] 同上（引号版本）
│           大学生志愿者挫折反应及对策调查数据.csv    # [原始] CSV格式
│
├── results/                   # 仿真结果
│   ├── all_results.pkl       # [生成] 所有实验结果（pickle，含8组×多次重复）
│   ├── 00_experiment_summary_v9.2_final.csv  # [生成] 实验汇总表
│   ├── 00_experiment_summary_v9.2.csv        # [存档] 中间版本
│   ├── 00_experiment_summary_corrected.csv   # [存档] 修正版
│   ├── 02_model_parameters.csv               # [生成] 模型参数表
│   ├── fig1_overall_trends.png    # [生成] 活跃人数年度趋势
│   ├── fig2_individual_behaviors.png  # [生成] 个体行为轨迹
│   ├── fig3_population_pyramid.png    # [生成] 人口金字塔
│   ├── fig4_calibration.png            # [生成] 校准验证图
│   ├── fig5_mechanisms.png             # [生成] 三机制效应图
│   └── fig6_sensitivity.png            # [生成] 敏感性分析图
│
├── docs/                      # 文档
│   ├── model_specification.md # 模型规范（ODD协议）
│   ├── replication_guide.md  # 复现指南
│   └── method_notes.md       # 方法说明
│
├── verification_package/      # 存档：v9.2最终验证包
│   ├── 3_model_code/         # 旧版模型代码
│   ├── 4_experiment_results/  # 旧版结果
│   ├── 6_report/             # 旧版论文
│   └── verify_results.py     # 旧版验证脚本
│
├── archive/                  # 历史版本归档
│   └── verification_package_v*.zip  # 各版本zip包
│
├── .gitignore                # Git忽略配置
├── requirements.txt          # pip依赖
├── environment.yml           # Conda环境配置
├── CHANGELOG.md              # 版本变更记录
├── CHANGELOG_v9.md          # [存档] 历史版本记录
├── FILES.md                 # 本文件
├── README.md                # 项目说明
└── verify_results.py        # 根目录验证脚本
```

## 文件状态说明

- **[主]**：核心交付文件，手写或主要编写的代码
- **[生成]**：由脚本自动生成，不可手动编辑
- **[废弃]**：历史文件，已被新版本替代
- **[存档]**：历史版本备份
- **[原始]**：原始数据文件，来自外部来源
- **[自动]**：编译/构建自动生成

## 外部数据来源

- **大学生志愿者挫折反应及对策调查数据**（张网成，2016）
  - 原始样本：592份，有效样本：572份
  - 格式：SPSS .sav + CSV
  - 存储：`data/empirical/` 目录
  - 引用：张网成. (2016). 大学生志愿者挫折反应及对策调查数据. 北京师范大学.

## 生成文件一览

运行 `python code/run_exp.py` 后自动生成：

| 文件 | 内容 | 大小参考 |
|------|------|---------|
| `results/all_results.pkl` | 8组实验全部原始结果 | ~1.6 MB |
| `results/00_experiment_summary_*.csv` | 实验汇总表 | ~2 KB |
| `results/fig*.png` | 6张图表 | 各~200-500 KB |

运行 `python code/reproduce_empirical.py` 后自动生成：

| 文件 | 内容 |
|------|------|
| `data/empirical/09_three_regression_comparison_final.csv` | 三套稳健性回归 |
| `data/empirical/10_frustration_attrition_crosstab.csv` | 交叉表 |
| `data/empirical/11_descriptive_statistics.csv` | 描述统计 |

## Git 历史关键节点

| 提交 | 说明 |
|------|------|
| `2275a62` | refactor: 重构为正式学术仓库结构 (v9.2-final) |
| `60ec4c3` | 初始化：论文初稿+ABM模型 |
