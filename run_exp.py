#!/usr/bin/env python3
"""
实验运行器：6实验 × N_RUNS × 60步
60步 = 5学年（获得4个完整学年流失率）
"""
import sys, os, time, pickle, multiprocessing as mp
from functools import partial

sys.path.insert(0, os.path.dirname(__file__))
from abm_model import VolunteerFieldModel

OUTPUT_DIR = os.path.dirname(__file__)
RESULTS_PATH = os.path.join(OUTPUT_DIR, "all_results.pkl")
N_RUNS = 15        # 每实验重复次数（可在命令行用 --runs N 覆盖）
MAX_STEPS = 60     # 5学年

# ============================================================
# 6个实验配置
# ============================================================
EXPERIMENTS = {
    "exp0_calibration": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 20,
    },
    "exp1_no_cohort": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": False,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 20,
    },
    "exp2_extended_term": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 2,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 20,
    },
    "exp3_more_funding": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 20.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 20,
    },
    "exp4_strong_reward": {
        "seed": 42,
        "recruitment_target": 300,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 99999,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 10,
    },
    "exp5_less_recruit": {
        "seed": 42,
        "recruitment_target": 200,
        "enable_cohort_attrition": True,
        "manager_term": 1,
        "active_capacity": 700,
        "total_funding": 10.0,
        "manager_positions": 120,
        "enable_innovation": True,
        "reward_threshold_low": 20,
    },
}

EXP_LABELS = {
    "exp0_calibration": "基线（校准）",
    "exp1_no_cohort": "无届际更替",
    "exp2_extended_term": "延长管理层任期",
    "exp3_more_funding": "增加活动经费",
    "exp4_strong_reward": "强化激励政策",
    "exp5_less_recruit": "减少招募规模",
}


def run_one_replication(exp_key: str, rep: int, n_steps: int = MAX_STEPS) -> dict:
    """单次重复：seed = base_seed + rep*7（保证MC独立性）"""
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
    """一个实验，n_runs次重复"""
    reps = []
    for r in range(n_runs):
        res = run_one_replication(exp_key, r)
        reps.append(res)
    return {"exp_key": exp_key, "replications": reps}


def run_all_experiments(n_runs: int = N_RUNS) -> dict:
    """6实验并行（各实验顺序跑n_runs次）"""
    exp_keys = list(EXPERIMENTS.keys())
    n_workers = min(6, mp.cpu_count())
    t0 = time.time()

    with mp.Pool(n_workers) as pool:
        tasks = [exp_key for exp_key in exp_keys]
        results = pool.map(partial(run_experiment, n_runs=n_runs), tasks)

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

    print(f"启动实验: 6实验 × {n_runs}次重复 × {MAX_STEPS}步")
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
        avg_ar = sum(s["annual_attrition_rate"] for s in summaries) / len(summaries)
        avg_active = sum(s["active_agents"] for s in summaries) / len(summaries)
        avg_mgr = sum(s["manager_count"] for s in summaries) / len(summaries)
        avg_innov = sum(s["cum_innovation"] for s in summaries) / len(summaries)
        label = EXP_LABELS.get(ek, ek)
        print(f"{label}: active={avg_active:.0f}, mgr={avg_mgr:.1f}, "
              f"ar={avg_ar:.3f}, innov={avg_innov:.0f}")
    sys.stdout.flush()
