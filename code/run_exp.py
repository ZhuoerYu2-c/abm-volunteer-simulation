#!/usr/bin/env python3
"""
实验运行器：8实验 × N_RUNS × 60步（v9.0）
=============================================================
v9新增实验说明：
  exp5  减少招募（仅降招募目标）→ 检验"少招人"的纯粹效应
  exp6  容量控制（不加容量上限）→ 检验容量上限的纯粹效应
  exp7  招募+容量双重干预（v8的exp5）→ 综合效应
  exp8  区间激励（设下限+上限+过载惩罚）→ 与exp4单一门槛对比

实验组设计：
  基线 vs 无届际更替 vs 延长任期 vs 增加经费
  vs 强化激励（v8风格，单一门槛）vs 招募减少（仅目标）
  vs 容量控制（仅上限）vs 招募+容量双重干预
"""
import sys, os, time, pickle, multiprocessing as mp
from functools import partial

sys.path.insert(0, os.path.dirname(__file__))
from abm_model import VolunteerFieldModel

# 结果保存到 code/ 的上一级 results/ 目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "all_results.pkl")
N_RUNS = 15        # 每实验重复次数
MAX_STEPS = 60      # 5学年

# ============================================================
# 8个实验配置（v9）
# ============================================================
EXPERIMENTS = {
    # ---- 基线（校准）----
    "exp0_calibration": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        # 激励参数（v9区间激励默认值）
        "reward_threshold_low": 6,   # 下限门槛
        "reward_threshold_opt": 12,  # 最优激励下限
        "reward_threshold_high": 25, # 上限（超过则激励减弱）
    },
    # ---- 无届际更替----
    "exp1_no_cohort": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": False,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 6,
        "reward_threshold_opt": 12,
        "reward_threshold_high": 25,
    },
    # ---- 延长管理层任期----
    "exp2_extended_term": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 2,  # 2年任期
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 6,
        "reward_threshold_opt": 12,
        "reward_threshold_high": 25,
    },
    # ---- 增加活动经费----
    "exp3_more_funding": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 20.0,  # 翻倍
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 6,
        "reward_threshold_opt": 12,
        "reward_threshold_high": 25,
    },
    # ---- 强化激励（v8风格：单一低门槛）----
    "exp4_strong_reward_v8": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        # v8风格：单一门槛（无区间效应）
        "reward_threshold_low": 10,
        "reward_threshold_opt": 99999,  # 无上限区
        "reward_threshold_high": 99999,
    },
    # ---- 招募减少（仅降低招募目标）----
    # 目的：分离"少招人"与"容量上限"的单独效应
    "exp5_less_recruit_only": {
        "seed": 42,
        "recruitment_target": 200,  # 减少招募目标
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,  # 无容量上限
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 6,
        "reward_threshold_opt": 12,
        "reward_threshold_high": 25,
    },
    # ---- 容量控制（仅加容量上限）----
    # 目的：检验"总量管控"是否比"减少招募"更有效
    "exp6_capacity_limit_only": {
        "seed": 42,
        "recruitment_target": 300,  # 不减少招募
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 700,     # 仅加容量上限
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 6,
        "reward_threshold_opt": 12,
        "reward_threshold_high": 25,
    },
    # ---- 招募+容量双重干预（v8 exp5）----
    "exp7_less_recruit_and_cap": {
        "seed": 42,
        "recruitment_target": 200,  # 减少招募
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 700,     # 加容量上限
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 6,
        "reward_threshold_opt": 12,
        "reward_threshold_high": 25,
    },
}

EXP_LABELS = {
    "exp0_calibration":         "基线（校准）",
    "exp1_no_cohort":           "无届际更替",
    "exp2_extended_term":        "延长管理层任期",
    "exp3_more_funding":         "增加活动经费",
    "exp4_strong_reward_v8":     "强化激励（单一门槛）",
    "exp5_less_recruit_only":    "减少招募（仅目标）",
    "exp6_capacity_limit_only":  "容量控制（仅上限）",
    "exp7_less_recruit_and_cap": "减少招募+容量双重",
}


def run_one_replication(exp_key: str, rep: int, n_steps: int = MAX_STEPS) -> dict:
    """单次重复"""
    cfg = EXPERIMENTS[exp_key].copy()
    base_seed = cfg.pop("seed", 42)
    seed = base_seed + rep * 7
    model = VolunteerFieldModel(seed=seed, **cfg)
    for i in range(n_steps):
        model.step()
    s = model.get_summary()
    return {
        "exp_key": exp_key,
        "rep": rep,
        "seed": seed,
        "history": model.history,
        "summary": s,
    }


def run_experiment(exp_key: str, n_runs: int) -> dict:
    reps = [run_one_replication(exp_key, r) for r in range(n_runs)]
    return {"exp_key": exp_key, "replications": reps}


def run_all_experiments(n_runs: int = N_RUNS) -> dict:
    exp_keys = list(EXPERIMENTS.keys())
    t0 = time.time()
    with mp.Pool(min(8, mp.cpu_count())) as pool:
        results = pool.map(partial(run_experiment, n_runs=n_runs), exp_keys)
    elapsed = time.time() - t0
    out = {"experiments": results, "n_runs": n_runs, "n_steps": MAX_STEPS,
           "elapsed_seconds": elapsed, "exp_labels": EXP_LABELS}
    with open(RESULTS_PATH, "wb") as f:
        pickle.dump(out, f)
    return out


if __name__ == "__main__":
    n_runs = N_RUNS
    if "--runs" in sys.argv:
        idx = sys.argv.index("--runs")
        n_runs = int(sys.argv[idx + 1])

    print(f"启动实验: 8实验 × {n_runs}次重复 × {MAX_STEPS}步")
    print(f"CPU核心数: {mp.cpu_count()}")
    print("-" * 50)
    sys.stdout.flush()

    results = run_all_experiments(n_runs=n_runs)
    print(f"\n完成！耗时: {results['elapsed_seconds']:.1f}秒")
    print(f"结果保存至: {RESULTS_PATH}")
    print()
    for exp_res in results["experiments"]:
        ek = exp_res["exp_key"]
        summaries = [r["summary"] for r in exp_res["replications"]]
        avg_ar   = sum(s["annual_attrition_rate"] for s in summaries) / len(summaries)
        avg_act  = sum(s["active_agents"]         for s in summaries) / len(summaries)
        avg_mgr  = sum(s["manager_count"]          for s in summaries) / len(summaries)
        avg_inv  = sum(s["cum_innovation"]         for s in summaries) / len(summaries)
        avg_promo= sum(s.get("promotion_rate",0)   for s in summaries) / len(summaries)
        label = EXP_LABELS.get(ek, ek)
        print(f"{label}: active={avg_act:.0f}, mgr={avg_mgr:.1f}, "
              f"ar={avg_ar:.3f}, innov={avg_inv:.0f}, promo={avg_promo:.3f}")
    sys.stdout.flush()
