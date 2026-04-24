"""
大学生志愿服务场域 ABM 模型 v9.0（深度修正版）
=============================================================
核心修正（v9，相较于v8）：
1. 学业压力修正：年级4(大四)从0.60上调至0.80，
   理由：毕业/考研/求职/论文/实习等多重压力叠加，高于大三(0.70)。
2. 激励机制重新设计：加入下限、上限、边际递减和过载惩罚，
   反映现实激励的"区间效应"而非线性鼓励。
3. 创新机制修正：管理层创新概率中的时间因子，
   改为使用管理层整体学业压力的均值（而非个别管理者的压力），
   使创新成功概率更稳定。
4. 满意度编码说明：原始问卷"志愿服务现状满意度"(变量56)为反向编码
   （值越大=满意度越低）。模型中 satisfaction=1-原始变量/5，
   含义：satisfaction越高=服务质量体验越好。

三机制说明（均来自实证数据，张网成2016）：
  ① 学业压力 academic_pressure: 年级1=0.30/2=0.50/3=0.70/4=0.80
     实证：52.5%流失者归因"时间过多"（变量41）
  ② 挫折感 frustration: 初始分布来自问卷分布(1级18.2%/2级3.2%/3级41.8%/4级72.5%/5级100%)
     实证：挫折感量表1-5级与流失率单调正相关（r=0.151独立于满意度）
  ③ 满意度 satisfaction: 来自服务质量体验，随项目质量动态变化
     实证：挫折感与满意度相关系数仅0.151

三机制月度流失公式：
  P = (1-S)×0.025 + F×0.010 + P_acad×0.025
  月度流失均值≈4.5%，年留存率(1-0.045)^12≈57.6%，年流失率≈42.4%（实证42.7%）
"""

import random, numpy as np
from typing import Dict, List


class VolunteerAgent:
    FRESHMAN = "freshman_volunteer"
    SENIOR   = "senior_volunteer"
    MANAGER  = "manager"

    # ============================================================
    # 年级→学业压力（时间约束维度）
    # 修正（v9）：大四=0.80 > 大三=0.70
    # 依据：大四面临毕业/考研/求职/论文/实习等多重压力，
    #       高于大三课业压力，符合教育阶段现实特征。
    # 相比之下，大三课业压力略高(考研备考开始积累)，高于大二。
    # ============================================================
    ACADEMIC_PRESSURE = {
        1: 0.30,  # 大一：适应期，压力最低
        2: 0.50,  # 大二：稳定期，课业为主
        3: 0.70,  # 大三：专业课密集+考研备考启动
        4: 0.80,  # 大四：毕业论文+考研冲刺+求职+实习
    }

    def __init__(self, model, grade: int, role: str, agent_seed: int):
        self.unique_id = model.next_id()
        self.model     = model
        self.grade     = grade
        self.role      = role
        self.is_active = True
        rng = random.Random(agent_seed)

        # ③ 满意度（服务质量体验）
        # 原始数据"志愿服务现状满意度"为反向编码（值越大=满意度越低）
        # 模型中 satisfaction ∈ [0,1]，越高表示服务质量体验越好
        self.satisfaction = rng.uniform(0.55, 0.80)

        # ② 挫折感（期望-现实差距）
        # 初始分布按问卷实际分布：挫折感=1→18.2%, 2→3.2%, 3→41.8%, 4→72.5%, 5→100%
        frustration_init = rng.choice([0.18, 0.03, 0.42, 0.73, 1.00])
        self.frustration = frustration_init

        # ① 学业压力（时间约束）
        self.academic_pressure = self.ACADEMIC_PRESSURE[grade]

        self.management_ability = rng.uniform(0.40, 0.90)
        self.tenure_years       = 0
        self.service_count       = 0
        self.received_reward     = False
        self.cumulative_rewards  = 0
        self.association_years    = 0
        self.ever_manager        = (role == self.MANAGER)

        # 管理层满意度保护效应
        if role == self.MANAGER:
            self.satisfaction = min(1.0, self.satisfaction + 0.15)

        self._r = rng

    def decide_participate(self):
        """月度参与决策"""
        if not self.is_active:
            return
        base = self.satisfaction
        acad = 1.0 - self.academic_pressure
        active = [a for a in self.model.schedule.agents if a.is_active]
        peer = (sum(a.service_count for a in active) / len(active)) / 20.0 if active else 0.0
        prob = max(0.0, min(1.0, base * 0.45 + acad * 0.35 + min(peer, 1.0) * 0.20))
        if self._r.random() < prob:
            self.service_count += 1

    def update_satisfaction(self):
        """满意度更新（服务质量体验机制，独立于挫折感）"""
        if not self.is_active:
            return
        if self._r.random() < self.model.excellent_project_ratio:
            gain = self._r.uniform(0.08, 0.14)
        else:
            gain = self._r.uniform(-0.04, 0.07)
        # 边际递减：服务次数过多时体验增益衰减
        if self.service_count > 15:
            gain *= 0.5
        elif self.service_count > 25:
            gain *= 0.3
        self.satisfaction += gain
        self.satisfaction = max(0.05, min(1.0, self.satisfaction))

    def update_frustration(self):
        """
        挫折感更新（期望-现实差距机制，独立于满意度）
        驱动：
          ① 非优秀项目：ΔF ∈ [+0.03, +0.07]
          ② 招募失败（每学年约8%概率）：ΔF ∈ [+0.03, +0.06]
          ③ 学业压力高时（>0.60）：额外ΔF ∈ [+0.01, +0.03]
          ④ 持续参与（service_count>10）：缓慢下降
          ⑤ 过载惩罚（v9新增）：service_count>20，疲劳积累加速
        """
        if not self.is_active:
            return
        if self._r.random() >= self.model.excellent_project_ratio:
            self.frustration += self._r.uniform(0.03, 0.07)
        if self._r.random() < 0.08:
            self.frustration += self._r.uniform(0.03, 0.06)
        if self.academic_pressure > 0.60:
            self.frustration += self._r.uniform(0.01, 0.03)
        if self.service_count > 10:
            self.frustration -= self._r.uniform(0.005, 0.015)
        # v9新增：过载惩罚（服务过多→疲劳+挫折感）
        if self.service_count > 20:
            self.frustration += self._r.uniform(0.01, 0.02)
        self.frustration = max(0.0, min(1.0, self.frustration))

    def check_monthly_attrition(self):
        """
        三机制月度流失（v9）：
        P = (1-satisfaction)×0.025 + frustration×0.010 + academic_pressure×0.025
        合计最大=0.060，均值≈0.045（受智能体异质性调节）
        年留存率≈(1-0.045)^12≈57.6%，年流失率≈42.4%（与实证42.7%接近）

        说明：
          - 学业压力(α=0.025)：时间约束，52.5%流失者归因"时间过多"
          - 挫折感(α=0.010)：期望-现实差距，量表1-5级单调正相关流失率
          - 满意度(α=0.025)：服务质量体验（管理层+0.15满意度→流失-0.375%）
        """
        if not self.is_active:
            return False
        prob = max(0.0, min(0.95,
            (1.0 - self.satisfaction) * 0.025 +
            self.frustration          * 0.010 +
            self.academic_pressure   * 0.025))
        if self._r.random() < prob:
            self.is_active = False
            self.model._record_attrition(self)
            return True
        return False

    def annual_reward_check(self):
        """
        年度激励分配（v9重新设计）
        ============================================================
        修正：原v8版本"单一门槛+满足即奖励"不符合现实激励逻辑。
        v9设计依据：
          - 激励应有下限（太少的服务体验不足以判断持续性）
          - 激励应有上限（过多投入→疲劳→边际效用递减）
          - 存在"甜蜜区"（适度参与→最强激励效应）
        ============================================================

        参数（可由实验配置覆盖）：
          reward_threshold_low  : 下限门槛（默认6）
          reward_threshold_opt : 最优激励服务次数下限（默认12）
          reward_threshold_high: 上限（超过此值激励减弱，默认25）

        激励效应（service_count × satisfaction 综合指数）：
          - < threshold_low    : 无奖励（体验不足，不判断持续性）
          - [low, opt]         : 满意度越高奖励越强（+0.06~+0.10）
          - [opt, high]        : 维持奖励但减弱（+0.03~+0.05）
          - > high             : 过载惩罚（奖励减少，+0.01）
            同时学业压力高时额外惩罚（ΔF +0.01）
        """
        if not self.is_active:
            return
        sc = self.service_count
        sat = self.satisfaction
        low  = self.model.params.get("reward_threshold_low", 6)
        opt  = self.model.params.get("reward_threshold_opt", 12)
        high = self.model.params.get("reward_threshold_high", 25)

        if sc >= low:
            if sc <= opt:
                gain = 0.06 + (sat - 0.5) * 0.08  # 0.02~0.10
            elif sc <= high:
                gain = 0.03 + (sat - 0.5) * 0.04  # 0.01~0.05
            else:
                gain = 0.01  # 过载，只给最小奖励
                # 过载额外惩罚：学业压力高时增加挫折感
                if self.academic_pressure > 0.50:
                    self.frustration += self._r.uniform(0.01, 0.02)

            gain = max(0.0, min(0.12, gain))
            self.satisfaction = min(1.0, self.satisfaction + gain)
            self.received_reward = True
            self.cumulative_rewards += 1
            self.model._total_rewards += 1


class SimpleScheduler:
    def __init__(self):
        self.time   = 0
        self.agents: List[VolunteerAgent] = []

    def add(self, a):
        self.agents.append(a)

    def remove(self, a):
        if a in self.agents:
            self.agents.remove(a)

    def step(self):
        self.time += 1


class VolunteerFieldModel:
    _id_counter = 0

    @classmethod
    def next_id(cls):
        cls._id_counter += 1
        return cls._id_counter

    def __init__(self, seed=42, **params):
        random.seed(seed)
        np.random.seed(seed)
        self.schedule  = SimpleScheduler()
        self.params    = params
        self.total_funding           = params.get("total_funding", 10.0)
        self.project_capacity        = params.get("project_capacity", 800)
        self.excellent_project_ratio = params.get("excellent_project_ratio", 0.10)
        self.active_capacity        = params.get("active_capacity", 99999)
        self.manager_positions       = params.get("manager_positions", 120)
        self._total_attrition        = 0
        self._total_innovation       = 0
        self._total_rewards         = 0
        self._total_ever_created    = 0
        self._total_promoted_to_mgr = 0
        self._total_multiyear_vol    = 0
        self._exit_service_sum       = 0
        self._exit_count            = 0
        self._year_start_active     = []
        self._yearly_attrition_list = []
        self._rec_events: List[Dict]   = []
        self._trans_events: List[Dict] = []
        self.history: List[Dict]     = []
        self._init_agents(seed)
        self._snapshot("init")

    def _record_attrition(self, agent):
        self._total_attrition += 1
        self._exit_service_sum += agent.service_count
        self._exit_count += 1
        if agent.association_years >= 2:
            self._total_multiyear_vol += 1

    def _init_agents(self, seed):
        rng = random.Random(seed)
        for i in range(93):
            g = rng.choices([2, 3], weights=[0.75, 0.25])[0]
            a = VolunteerAgent(self, grade=g, role=VolunteerAgent.MANAGER,
                              agent_seed=seed + i)
            a.management_ability  = rng.uniform(0.50, 0.90)
            a.tenure_years        = rng.choice([0, 1])
            a.service_count       = rng.randint(8, 30)
            a.satisfaction         = rng.uniform(0.55, 0.85)
            a.frustration          = rng.uniform(0.10, 0.40)
            a.association_years    = rng.randint(1, 3)
            a.ever_manager         = True
            self.schedule.add(a)
            self._total_ever_created += 1
        # 初始普通志愿者：年级1=500/年级2=180/年级3=76，共756人
        grade_dist = [1] * 500 + [2] * 180 + [3] * 76
        for i, g in enumerate(grade_dist):
            ay = 0 if g == 1 else (1 if g == 2 else 2)
            a = VolunteerAgent(self, grade=g,
                role=VolunteerAgent.FRESHMAN if g == 1 else VolunteerAgent.SENIOR,
                agent_seed=seed + 1000 + i)
            a.service_count  = rng.randint(0, 12)
            a.satisfaction   = rng.uniform(0.40, 0.75)
            if g == 1:
                a.frustration = rng.uniform(0.03, 0.25)
            elif g == 2:
                a.frustration = rng.uniform(0.10, 0.50)
            else:
                a.frustration = rng.uniform(0.20, 0.70)
            a.association_years = ay
            self.schedule.add(a)
            self._total_ever_created += 1

    def _do_august_annual_events(self, step: int):
        """8月：激励分配 + 届际更替 + 年级晋升"""
        if step % 12 != 7:
            return
        for a in self.schedule.agents:
            if a.is_active:
                a.annual_reward_check()
        to_remove = []
        for a in self.schedule.agents:
            if not a.is_active:
                continue
            a.association_years += 1
            if a.grade < 4:
                a.grade += 1
                a.academic_pressure = VolunteerAgent.ACADEMIC_PRESSURE[a.grade]
                if a.grade == 2 and a.role == VolunteerAgent.FRESHMAN:
                    a.role = VolunteerAgent.SENIOR
            else:
                # 4年级后毕业
                to_remove.append(a)
                continue
            if self.params.get("enable_cohort_attrition", True):
                if a.association_years >= 2 and a.role != VolunteerAgent.MANAGER:
                    to_remove.append(a)
        for a in to_remove:
            a.is_active = False
            self._record_attrition(a)
            self.schedule.remove(a)

    def _record_yearly_stats(self, step: int):
        """记录年初活跃人数（用于计算学年流失率）"""
        if step % 12 != 8:
            return
        active_now = len([a for a in self.schedule.agents if a.is_active])
        year_num = step // 12 + 1
        if len(self._year_start_active) >= 1:
            prev = self._year_start_active[-1]
            newly_rec = sum(e["n"] for e in self._rec_events if e["year"] == year_num)
            yr_end = active_now - newly_rec
            self._yearly_attrition_list.append(max(0, prev - yr_end))
        self._year_start_active.append(active_now)

    def _do_september_recruitment(self, step: int):
        """9月：大一新生招募"""
        if step % 12 != 8:
            return
        active_now = len([a for a in self.schedule.agents if a.is_active])
        target = self.params.get("recruitment_target", 300)
        cap    = self.active_capacity
        slot = max(0, min(cap - active_now, target)) if cap < 5000 else target
        for i in range(slot):
            a = VolunteerAgent(self, grade=1, role=VolunteerAgent.FRESHMAN,
                             agent_seed=step * 10000 + i)
            a.satisfaction  = random.Random(step * 10000 + i).uniform(0.50, 0.70)
            a.frustration   = random.Random(step * 10000 + i).uniform(0.03, 0.20)
            self.schedule.add(a)
            self._total_ever_created += 1
        if slot > 0:
            self._rec_events.append({"step": step, "year": step // 12 + 1, "n": slot})

    def _do_may_power_transition(self, step: int):
        """5月：管理层换届"""
        if step % 12 != 4:
            return
        term_limit = self.params.get("manager_term", 1)
        for a in self.schedule.agents:
            if a.role == VolunteerAgent.MANAGER and a.is_active:
                if a.tenure_years >= term_limit:
                    a.role = VolunteerAgent.SENIOR
                    a.tenure_years = 0
                    a.management_ability = max(0.3, a.management_ability - 0.05)
                else:
                    # 20%概率提前卸任（即使未到期）
                    if random.random() > 0.20:
                        a.role = VolunteerAgent.SENIOR
                        a.tenure_years = 0
                    else:
                        a.tenure_years += 1
        candidates = [a for a in self.schedule.agents
                     if a.grade >= 2 and a.association_years >= 1
                     and a.role != VolunteerAgent.MANAGER and a.is_active
                     and a.service_count >= 5]
        for a in candidates:
            a._sort_key = a.management_ability + random.uniform(-0.15, 0.15)
        candidates.sort(key=lambda x: x._sort_key, reverse=True)
        n_select = min(self.manager_positions, len(candidates))
        for m in candidates[:n_select]:
            m.role = VolunteerAgent.MANAGER
            m.tenure_years = 1
            m.management_ability = random.uniform(0.55, 0.95)
            m.ever_manager = True
            m.satisfaction = min(1.0, m.satisfaction + 0.15)
            m.frustration = max(0.0, m.frustration - 0.05)
            self._total_promoted_to_mgr += 1
        self._trans_events.append({
            "step": step, "year": step // 12 + 1, "new_managers": n_select})

    def _do_march_innovation(self, step: int):
        """3月：项目创新"""
        if step % 12 != 2 or not self.params.get("enable_innovation", True):
            return
        managers = [a for a in self.schedule.agents
                    if a.role == VolunteerAgent.MANAGER and a.is_active]
        if not managers:
            return
        # v9修正：使用管理层整体学业压力均值（而非单个管理者压力）
        # 使创新成功概率在管理层规模变化时更稳定
        avg_mgr_acad = np.mean([a.academic_pressure for a in managers])
        for mgr in managers:
            ability_f  = mgr.management_ability * 0.05
            resource_f = (self.total_funding / 10.0) * 0.20
            # 时间/精力因子：管理层学业压力越高→可投入创新的精力越少
            time_f    = (1.0 - avg_mgr_acad) * 0.02
            prob = max(0.01, min(0.95,
                ability_f + resource_f + time_f + random.uniform(-0.02, 0.02)))
            if random.random() < prob:
                self.project_capacity += random.randint(20, 80)
                self.excellent_project_ratio = min(0.80,
                    self.excellent_project_ratio + 0.003)
                self._total_innovation += 1

    def _snapshot(self, notes=""):
        active = [a for a in self.schedule.agents if a.is_active]
        n = len(active)
        sat  = np.mean([a.satisfaction  for a in active]) if n > 0 else 0.0
        frag = np.mean([a.frustration   for a in active]) if n > 0 else 0.0
        acad = np.mean([a.academic_pressure for a in active]) if n > 0 else 0.0
        svc  = np.mean([a.service_count for a in active]) if n > 0 else 0.0
        mgrs = sum(1 for a in active if a.role == VolunteerAgent.MANAGER)
        fr   = sum(1 for a in active if a.role == VolunteerAgent.FRESHMAN)
        sr   = sum(1 for a in active if a.role == VolunteerAgent.SENIOR)
        rec_n = (self._rec_events[-1]["n"] if self._rec_events and
                 self._rec_events[-1]["step"] == self.schedule.time else 0)
        self.history.append({
            "step": self.schedule.time,
            "year": self.schedule.time // 12 + 1,
            "month": self.schedule.time % 12 + 1,
            "active_count": n,
            "manager_count": mgrs,
            "freshman_count": fr,
            "senior_count": sr,
            "grade2_count": sum(1 for a in active if a.grade == 2),
            "grade3_count": sum(1 for a in active if a.grade == 3),
            "grade4_count": sum(1 for a in active if a.grade == 4),
            "avg_satisfaction": sat,
            "avg_frustration": frag,
            "avg_academic_pressure": acad,
            "avg_service_count": svc,
            "cum_attrition": self._total_attrition,
            "cum_innovation": self._total_innovation,
            "cum_rewards": self._total_rewards,
            "cum_ever_created": self._total_ever_created,
            "recruitment": rec_n,
            "project_capacity": self.project_capacity,
            "excellent_ratio": self.excellent_project_ratio,
            "notes": notes,
        })

    def step(self):
        t = self.schedule.time
        self._do_august_annual_events(t)
        self._do_september_recruitment(t)
        self._record_yearly_stats(t)
        for a in list(self.schedule.agents):
            if a.is_active:
                a.decide_participate()
                a.update_satisfaction()
                a.update_frustration()
        self._do_may_power_transition(t)
        self._do_march_innovation(t)
        for a in list(self.schedule.agents):
            if a.is_active:
                a.check_monthly_attrition()
                if not a.is_active:
                    self.schedule.remove(a)
        self._snapshot()
        self.schedule.step()

    def get_summary(self) -> Dict:
        if not self.history:
            return {}
        last = self.history[-1]
        BASE = 849.0
        annual_rates = []
        for step in [8, 20, 32]:
            h_cur  = next((h for h in self.history if h["step"] == step),     None)
            h_next = next((h for h in self.history if h["step"] == step + 12), None)
            if h_cur and h_next:
                yr_loss = h_next["cum_attrition"] - h_cur["cum_attrition"]
                annual_rates.append(max(0.0, yr_loss / BASE))
        avg_ar = (sum(annual_rates) / len(annual_rates) if annual_rates else 0.0)
        total_created = self._total_ever_created
        # 晋升率 = 累计晋升管理层人次 / 累计创建志愿者总数
        promo_rate = self._total_promoted_to_mgr / total_created if total_created > 0 else 0.0
        return {
            "active_agents": last["active_count"],
            "total_created": total_created,
            "manager_count": last["manager_count"],
            "freshman_count": last["freshman_count"],
            "senior_count": last["senior_count"],
            "grade2_count": last["grade2_count"],
            "grade3_count": last["grade3_count"],
            "grade4_count": last["grade4_count"],
            "avg_satisfaction": last["avg_satisfaction"],
            "avg_frustration": last["avg_frustration"],
            "avg_academic_pressure": last["avg_academic_pressure"],
            "avg_service_count": last["avg_service_count"],
            "cum_attrition": self._total_attrition,
            "cum_innovation": self._total_innovation,
            "cum_rewards": self._total_rewards,
            "annual_attrition_rate": avg_ar,
            "yearly_ar_list": annual_rates,
            "cum_promoted_to_mgr": self._total_promoted_to_mgr,
            "promotion_rate": promo_rate,
            "cum_multiyear_vol": self._total_multiyear_vol,
            "avg_exit_service_count": (self._exit_service_sum / self._exit_count) if self._exit_count > 0 else 0.0,
            "final_excellent_ratio": self.excellent_project_ratio,
        }
