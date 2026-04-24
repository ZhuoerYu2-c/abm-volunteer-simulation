# CHANGELOG

## [v9.2-final] - 2026-04-24 傍晚

### 仓库结构重构（Phase 1 完成）

**新目录结构**：
```
paper/           # 论文全文（LaTeX + PDF）
code/            # 模型代码（abm_model.py + 实验/绘图/复现脚本）
data/empirical/  # 实证数据与回归结果
results/         # 实验结果（PKL + CSV + PNG图表）
archive/         # 归档旧版本
```

**文件清理**：
- 归档 `verification_package v2/v3/v4` 全部旧版本
- 删除根目录重复脚本（abm_v2.py, gen_report.py, main.py）
- 删除旧 report_backup.tex 等
- deprecated 文件已明确标注

**脚本路径统一**：
- `code/run_exp.py`：结果保存至 `../results/`
- `code/run_figures.py`：从 `../results/` 读取 PKL，图表输出至 `../results/`
- `code/reproduce_empirical.py`：从 `../data/empirical/` 读取数据，输出至 `../data/empirical/`
- 根目录 `verify_results.py`：从 `results/` 读取 PKL

**三个脚本全部跑通**：
- `code/reproduce_empirical.py`：✅ 成功输出回归表 + 交叉表 + 描述性统计
- `code/run_figures.py`：✅ 成功生成 6 张图至 results/
- `verify_results.py`：✅ 快速验证通过

---

## [v9.2-patch1] - 2026-04-24 傍晚

### ABM代码4个bug修复
1. **挫折感初始化**：等概率`choice`→加权抽样`choices(weights=[40,120,208,160,24])`
2. **满意度更新if/elif顺序**：修正为先检查`>25`再`>15`
3. **任期弹性20%标注**：代码注释+报告正文说明为"制度弹性设计"
4. **创新公式统一**：代码与论文公式一致（`(1-avg)×0.02`）

### 报告文字数字同步（基于v9.2-patch1实际结果）
- 基线：AR 42.8→43.0%，管理90.9→88.8
- 无届际：管理83.4→78.1
- 延长：管理97.9→93.3
- 减少招募：AR 34.8→34.6%
- 双重干预：AR 33.1→32.9%

### 实证文件清理
- 现行表1来源：`09_three_regression_comparison_final.csv`
- 废弃文件标注 `deprecated_` 前缀

---

## [v9.2] - 2026-04-24 下午

初稿完成，包含 8 组仿真实验 + 实证分析 + 完整报告。

