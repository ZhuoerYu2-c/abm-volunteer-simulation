# CHANGELOG

## [v10.0] - 2026-04-24

### Added
- **正式论文 paper/paper_final.tex**：11页完整学术论文，含全部12个章节（引言→参考文献）
- **理论框架表 tab:theory_map**：理论命题→行为规则→可测度指标三层映射
- **参数来源说明**：四类参数来源（文献/问卷/回归/校准）的完整说明
- **docs/model_specification.md**：ODD协议规范文档
- **docs/replication_guide.md**：完整复现指南
- **docs/abstract_v2.md**：摘要与引言写作草稿

### Changed
- **paper/report.tex** → **paper/paper_final.tex**：正式版论文替代工作版
- **paper/paper_final.tex**：11页（从10页扩展），26篇参考文献，完整学术论文结构
- **README.md**：升级为正式学术项目说明
- **FILES.md**：完整文件清单与状态说明

### Fixed
- 参考文献格式：统一使用 thebibliography 环境，APA格式
- 图表引用：正确插入 fig1/fig5/fig6 图片路径
- 表格格式：实验结果表改用脚本排版（\\footnotesize），正常编译

## [v9.2] - 2026-04-24

### Added
- **code/abm_model.py**：Mesa框架ABM核心模型
- **code/reproduce_empirical.py**：三套稳健性逻辑回归
- **code/run_exp.py**：8组蒙特卡洛仿真实验
- **code/run_figures.py**：6张图表生成脚本
- **data/empirical/09/10/11_*.csv**：实证分析结果文件
- **verification_package/**：v9.2验证包

### Changed
- 重构仓库为正式学术结构：paper/code/data/results分离
- 所有路径使用相对路径（基于\_\dir）
- 所有脚本添加 sys.path.insert 修复

### Fixed
- 路径依赖问题：CSV/SAV/PKL路径全部使用 \_\_file\_\_
- 参数来源表：删除溢出 landscape 环境，改为正常排版
