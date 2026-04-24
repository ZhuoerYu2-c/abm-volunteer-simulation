# 最终文件清单（v9.2-final）

## 正式保留文件

### paper/
| 文件 | 说明 | 来源 |
|------|------|------|
| `report.tex` | 论文 LaTeX 源码（v9.2，14页） | 主线 |
| `report.pdf` | 编译后 PDF | 主线 |

### code/
| 文件 | 说明 | 备注 |
|------|------|------|
| `abm_model.py` | ABM 模型主体（v9.2，含全部 bug 修复） | 主线 |
| `run_exp.py` | 仿真实验脚本（8组×15次MC） | 主线 |
| `run_figures.py` | 图表生成脚本（6张图+敏感性分析） | 主线 |
| `reproduce_empirical.py` | 实证分析复现脚本 | 主线 |

### data/empirical/
| 文件 | 说明 | 备注 |
|------|------|------|
| `09_three_regression_comparison_final.csv` | **表1 现行来源**（三套稳健性回归） | 主线 |
| `10_frustration_attrition_crosstab.csv` | 挫折感×流失率交叉表 | 主线 |
| `01_descriptive_statistics.csv` | 描述性统计 | 主线 |
| `02_frustration_vs_attrition.csv` | 挫折感与流失关系 | 主线 |
| `03_attrition_reasons.csv` | 流失原因分布 | 主线 |
| `04_attrition_vs_non_attrition_comparison.csv` | 流失/留存对比 | 主线 |
| `05_correlation_matrix.csv` | 相关矩阵 | 主线 |
| `06_logistic_regression_reproduced.csv` | logistic 回归复现 | 主线 |
| `07_factor_scores_F1_F2.csv` | 因子得分 | 主线 |
| `大学生志愿者挫折反应及对策调查数据.csv` | 原始数据（572行） | 原始 |
| `大学生志愿者挫折反应及对策调查数据_含备注.xlsx` | 变量说明 | 原始 |

### data/empirical/（deprecated/归档）
| 文件 | 说明 | 原因 |
|------|------|------|
| `deprecated_08_robustness_regression.csv` | 旧稳健性回归（已被09替代） | 废弃 |
| `deprecated_logistic_regression_output.csv` | 旧 logistic 输出 | 废弃 |
| `deprecated_logistic_regression_reproduced.csv` | 旧 logistic 复现 | 废弃 |

### results/
| 文件 | 说明 | 备注 |
|------|------|------|
| `all_results.pkl` | **完整实验结果**（8组×15次MC） | 主线 |
| `00_experiment_summary_v9.2_final.csv` | **结果汇总表** | 主线 |
| `fig1_overall_trends.png` | 活跃人数年度趋势 | 主线 |
| `fig2_structure.png` | 人员结构演变 | 主线 |
| `fig3_policy_comparison.png` | 政策效果对比 | 主线 |
| `fig4_calibration.png` | 校准验证 | 主线 |
| `fig5_mechanisms.png` | 机制效应 | 主线 |
| `fig6_sensitivity.png` | 敏感性分析 | 主线 |

### results/deprecated/
| 文件 | 说明 | 原因 |
|------|------|------|
| `00_experiment_summary_corrected.csv` | 旧汇总表 | 被 v9.2_final 替代 |
| `02_model_parameters.csv` | 旧参数表 | 与最新参数有差异 |

### docs/reproducibility/
（待补充：方法说明文档、参数来源文档）

### 根目录
| 文件 | 说明 |
|------|------|
| `README.md` | 项目说明 |
| `CHANGELOG.md` | 版本记录 |
| `requirements.txt` | pip 依赖 |
| `environment.yml` | conda 环境 |
| `.gitignore` | Git 忽略规则 |
| `verify_results.py` | 快速验证脚本 |
| `FILES.md` | 本清单 |

## 已删除/归档

| 内容 | 位置 |
|------|------|
| verification_package v2/v3/v4（全部旧版本） | → `archive/deprecated_versions/` |
| 根目录重复脚本（abm_v2.py, gen_report.py, main.py） | → `archive/deprecated_root/` |
| 旧 report_backup.tex, report_backup2.tex | → `archive/deprecated_root/` |
| 旧论文 PDF（paper_*.pdf） | → `archive/deprecated_root/` |

## 结果链路（PKL→CSV→正文表格 100% 一致）

```
all_results.pkl
    ↓ (run_exp.py 输出)
00_experiment_summary_v9.2_final.csv
    ↓ (手动填入)
report.tex 表4 + 正文数字
    ↓ (xelatex)
report.pdf
```
