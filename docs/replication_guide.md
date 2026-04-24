# 复现指南

本文档说明如何复现本研究的所有结果。

## 环境要求

- Python 3.8+
- 推荐使用 conda 环境（见 `environment.yml`）

### 依赖包

```
mesa >= 3.0.0
numpy >= 1.21.0
pandas >= 1.3.0
scipy >= 1.7.0
scikit-learn >= 1.0.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
openpyxl >= 3.0.0
```

## 复现步骤

### 步骤1：配置环境

```bash
# 克隆仓库
git clone https://github.com/ZhuoerYu2-c/abm-volunteer-simulation.git
cd abm-volunteer-simulation

# 创建conda环境
conda env create -f environment.yml
conda activate abm-volunteer

# 或使用pip
pip install -r requirements.txt
```

### 步骤2：实证分析

```bash
cd code/
python reproduce_empirical.py
```

输出：
- `data/empirical/09_three_regression_comparison_final.csv`
- `data/empirical/10_frustration_attrition_crosstab.csv`
- `data/empirical/11_descriptive_statistics.csv`

### 步骤3：运行仿真实验

```bash
python run_exp.py
```

输出：
- `results/all_results.pkl`（包含所有实验的原始结果）
- `results/00_experiment_summary_v9.2_final.csv`
- `results/02_model_parameters.csv`

运行时间：约2分钟（8组实验 × 15次重复 × 60步）

### 步骤4：生成图表

```bash
python run_figures.py
```

输出：
- `results/fig1_overall_trends.png`
- `results/fig2_individual_behaviors.png`
- `results/fig3_population_pyramid.png`
- `results/fig4_calibration.png`
- `results/fig5_mechanisms.png`
- `results/fig6_sensitivity.png`

### 步骤5：验证结果

```bash
python verify_results.py
```

### 步骤6：编译论文

```bash
cd paper/
xelatex paper_final.tex
```

需要 XeLaTeX 发行版（如 TeX Live 2023+）和 ctex 宏包。

## 关键文件说明

| 文件 | 说明 |
|------|------|
| `code/abm_model.py` | ABM核心模型类（VolunteerAgent, ManagerAgent, VolunteeringFieldModel） |
| `code/run_exp.py` | 实验配置与执行脚本，定义8组实验的参数设置 |
| `code/reproduce_empirical.py` | 实证数据分析脚本，包含三套稳健性回归 |
| `code/run_figures.py` | 图表生成脚本 |
| `data/empirical/` | 处理后的实证数据CSV |
| `results/all_results.pkl` | 所有实验结果的pickle格式存储 |

## 参数校准说明

基线模型通过以下方式校准至实证值（学年流失率≈43%）：

1. **挫折感初始分布**：按问卷频率加权抽样（[40,120,208,160,24]）
2. **满意度初始范围**：[0.40, 0.70]（调参使流失率≈43%）
3. **月度流失系数**：（$\alpha_S=0.025, \alpha_F=0.010, \alpha_P=0.025$）组合调参
4. **学业压力赋值**：年级1:0.30, 年级2:0.50, 年级3:0.70, 年级4:0.80（文献推断+合理性）

## 敏感性分析

运行敏感性分析：

```bash
python -c "
from run_exp import run_all_experiments, N_REPS, N_STEPS
results = run_all_experiments()
print('Sensitivity baseline:', results['baseline']['attrition_rate'])
"
```

## 数据限制

- 原始数据（张网成2016）存在大量精确重复记录（572条中139种组合各重复约4次）
- 大四（12人）及研究生（8人）样本量过少，主分析限于本科1-3年级
- 实证学年流失率来自横截面调查，存在回忆偏差风险

## 常见问题

**Q: xelatex编译失败？**
A: 确保安装完整版 TeX Live（包含 ctex 宏包）。macOS 可用 MacTeX，Linux 用 texlive-latexextra。

**Q: 运行报错"ModuleNotFoundError: No module named 'mesa'"？**
A: 激活正确的 conda 环境，或 `pip install mesa`。

**Q: pickle 文件无法读取？**
A: 确保 Python 版本一致（3.8-3.10推荐）。pickle 与 pickle5 格式兼容。
