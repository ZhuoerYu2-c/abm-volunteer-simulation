# 模型规范说明（ODD协议）

本模型遵循 Grimm 等人（2020）提出的 ODD（Overview, Design concepts, Details）协议进行规范化描述。

## 目的（Purpose）

模型旨在再现高校志愿服务场域的年级梯度流失格局，探索学业压力、挫折感与满意度三个机制的独立与交互效应，并评估不同干预策略对成员流失率、管理层结构与组织创新的影响。

## 实体与尺度（Entities and Scales）

### 智能体类型

- **普通志愿者（VolunteerAgent）**：具有年级、学业压力、满意度、挫折感等状态变量
- **管理层（ManagerAgent）**：继承自志愿者，额外具有管理能力变量，可发起组织创新活动

### 时间尺度

- 模拟时间单位：1个月（30天）
- 总模拟时长：60个月（5学年）
- 招募时间：每年9月
- 晋升时间：每年5月
- 流失评估：每月

## 状态变量（State Variables）

每个志愿者智能体的核心状态变量：

| 变量 | 类型 | 取值范围 | 说明 |
|------|------|---------|------|
| `grade` | int | 1-4 | 当前年级 |
| `frustration` | float | [0, 1] | 挫折感水平 |
| `satisfaction` | float | [0, 1] | 满意度水平 |
| `academic_pressure` | float | [0, 1] | 学业压力水平 |
| `service_count` | int | ≥0 | 累计服务次数 |
| `is_manager` | bool | — | 是否担任管理层 |
| `months_as_manager` | int | ≥0 | 担任管理层月数 |
| `innovation_count` | int | ≥0 | 发起创新活动次数 |

## 行为规则（Process Overview and Scheduling）

### 每月执行顺序

1. **学业压力更新**（每月初）
   - 根据年级设定学业压力水平
   - 年级1: 0.30, 年级2: 0.50, 年级3: 0.70, 年级4: 0.80
   - 每3个月自动晋升年级（暑假）

2. **服务质量评估**（每月）
   - 随机抽取服务质量评分 $q \sim U[0.7, 1.0]$
   - 更新满意度 $\Delta S = q \times (1 - S_t) \times 0.10$（服务量≤15）
   - 服务量>25时，$\Delta S$ 缩减至30%
   - 服务量15-25时，$\Delta S$ 缩减至50%

3. **挫折感更新**（每月）
   - 基础增量：$\Delta F_{\text{base}} = P_{\text{acad}} \times 0.01$
   - 期望落差：$\Delta F_{\text{gap}} = \max(0, 0.50 - S_t) \times 0.03$
   - 管理层减免：担任管理层期间 $\Delta F$ 减少50%
   - 满意度过高减免：$S_t > 0.80$ 时 $\Delta F$ 减少30%

4. **流失决策**（每月）
   - 流失概率：$P_{\text{attrition}} = (1 - \bar{S}) \times 0.025 + \bar{F} \times 0.010 + P_{\text{acad}} \times 0.025$
   - 其中 $\bar{S}$、$\bar{F}$ 为最近3个月的滑动均值
   - 管理层成员额外降低流失概率10%

5. **创新活动**（仅管理层，每月）
   - 创新概率：$P_{\text{innovation}} = \min(0.95, A_{\text{mgr}} \times 0.05 + \frac{R}{10} \times 0.20 + (1 - \bar{P}^{\text{acad}}_{\text{mgr}}) \times 0.02)$
   - $R$ 为活动经费（万元），$A_{\text{mgr}}$ 为管理能力

6. **年级晋升**（每年5月）
   - 从高年级志愿者（grade ≥ 2）中晋升满意度最高者
   - 晋升条件：满意度 > 0.70，无违纪记录
   - 晋升奖励：满意度+0.15，挫折感-0.05
   - 管理层任期默认1年，20%概率提前卸任

7. **年度招募**（每年9月）
   - 按招募目标参数招募新生
   - 新生初始状态：grade=1, frustration~[0.03,1.00]按分布抽样，satisfaction~[0.40,0.70]均匀分布

## 设计概念（Design Concepts）

### 理论基础

- **场域理论**（Bourdieu, 1984）：场域是具有相对自主性的社会空间，行动者在其中围绕资本竞争
- **结构化理论**（Giddens, 1984）：结构既是行动的中介，又是行动的产物——行动与结构相互建构

### 三机制的操作化

- **学业压力**：通过年级变量间接测量，年级越高压力越大（反映课业、升学、就业等多重压力叠加）
- **挫折感**：通过期望-现实差距的动态累积建模，反映服务质量体验与预期的偏离
- **满意度**：通过服务质量评分与服务量的非线性函数动态更新

### emergence（涌现）

模型关注以下宏观涌现现象：
- 年级梯度流失格局（高年级流失率显著高于低年级）
- 组织层级结构的稳定与变迁
- 激励政策的非线性区间效应

## 参数来源（Initialization and Input）

详见论文正文表2"模型参数来源分类表"。

## 参考文献

Grimm, V., Railsback, S. F., \& Vincenot, A. E. (2020). OODD: The ODD+D protocol for describing agent-based models. *Journal of Artificial Societies and Social Simulation*, 23(2), 1-26.
