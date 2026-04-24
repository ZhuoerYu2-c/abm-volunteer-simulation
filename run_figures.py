#!/usr/bin/env python3
"""
生成5张可视化图表：
fig1: 活跃人数年度趋势（6实验）
fig2: 人员结构演变（管理层/新生/老生）
fig3: 政策效果对比（6实验雷达图）
fig4: 校准验证（目标值 vs 模拟值）
fig5: 机制效应汇总（届际更替/经费/任期/招募的边际效应）
"""
import sys, os, pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.dirname(__file__) or "."
RESULTS_PATH = os.path.join(OUTPUT_DIR, "all_results.pkl")

EXP_COLORS = {
    "exp0_calibration": "#2196F3",   # 蓝
    "exp1_no_cohort":   "#FF5722",   # 红
    "exp2_extended_term": "#4CAF50", # 绿
    "exp3_more_funding": "#FF9800",  # 橙
    "exp4_strong_reward": "#9C27B0",  # 紫
    "exp5_less_recruit": "#009688",   # 青
}
EXP_LABELS_CN = {
    "exp0_calibration": "基线（校准）",
    "exp1_no_cohort": "无届际更替",
    "exp2_extended_term": "延长管理层任期",
    "exp3_more_funding": "增加活动经费",
    "exp4_strong_reward": "强化激励政策",
    "exp5_less_recruit": "减少招募规模",
}


def load_results():
    if not os.path.exists(RESULTS_PATH):
        print(f"错误: 结果文件不存在 {RESULTS_PATH}")
        sys.exit(1)
    with open(RESULTS_PATH, "rb") as f:
        return pickle.load(f)


def aggregate(results):
    """对每个实验，计算均值和标准差"""
    agg = {}
    for exp in results["experiments"]:
        ek = exp["exp_key"]
        reps = exp["replications"]
        n_steps = results.get("n_steps", 60)

        # 按step聚合
        active_by_step   = {s: [] for s in range(0, n_steps + 1)}
        mgr_by_step      = {s: [] for s in range(0, n_steps + 1)}
        sat_by_step      = {s: [] for s in range(0, n_steps + 1)}
        fr_by_step       = {s: [] for s in range(0, n_steps + 1)}
        sr_by_step       = {s: [] for s in range(0, n_steps + 1)}

        for rep in reps:
            h = rep["history"]
            for rec in h:
                step = rec["step"]
                if step in active_by_step:
                    active_by_step[step].append(rec["active_count"])
                    mgr_by_step[step].append(rec["manager_count"])
                    sat_by_step[step].append(rec["avg_satisfaction"])
                    fr_by_step[step].append(rec["freshman_count"])
                    sr_by_step[step].append(rec["senior_count"])

        agg[ek] = {
            "active_mean":  {s: np.mean(v) for s, v in active_by_step.items() if v},
            "active_std":   {s: np.std(v)  for s, v in active_by_step.items() if v},
            "mgr_mean":     {s: np.mean(v) for s, v in mgr_by_step.items() if v},
            "sat_mean":     {s: np.mean(v) for s, v in sat_by_step.items() if v},
            "fr_mean":      {s: np.mean(v) for s, v in fr_by_step.items() if v},
            "sr_mean":      {s: np.mean(v) for s, v in sr_by_step.items() if v},
            "summaries":    [r["summary"] for r in reps],
        }
    return agg


def plot_fig1_trends(agg, results, out_dir):
    """图1：活跃人数年度趋势（6实验，阴影为±1标准差）"""
    n_steps = results.get("n_steps", 60)
    steps = sorted(agg["exp0_calibration"]["active_mean"].keys())
    years = [f"Y{(s // 12) + 1}\nM{(s % 12) + 1}" for s in steps]
    # 9月标注
    sep_steps = [s for s in steps if s % 12 == 8]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 上图：所有实验
    ax = axes[0]
    for ek in ["exp0_calibration", "exp1_no_cohort", "exp2_extended_term",
               "exp3_more_funding", "exp4_strong_reward", "exp5_less_recruit"]:
        mean = agg[ek]["active_mean"]
        std  = agg[ek]["active_std"]
        ms = [mean[s] for s in steps]
        ss = [std[s] for s in steps]
        xs = list(range(len(steps)))
        color = EXP_COLORS[ek]
        label = EXP_LABELS_CN[ek]
        ax.plot(xs, ms, color=color, lw=2, label=label)
        ax.fill_between(xs, [m - s for m, s in zip(ms, ss)],
                        [m + s for m, s in zip(ms, ss)],
                        color=color, alpha=0.15)

    # 标注9月
    for sp in sep_steps:
        idx = steps.index(sp)
        ax.axvline(idx, color="gray", lw=0.8, ls="--", alpha=0.5)
        ax.text(idx, ax.get_ylim()[0] if ax.get_ylim()[0] > 0 else 0,
                f"Y{sp//12+1}9月", ha="center", fontsize=7, color="gray")

    ax.set_ylabel("活跃志愿者人数", fontsize=12)
    ax.set_title("图1 活跃志愿者人数的年度演变趋势\n（阴影为±1标准差，垂直虚线为每年9月招募时点）", fontsize=13)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, len(steps) - 1)

    # 下图：基线 vs 无届际更替（聚焦对比）
    ax2 = axes[1]
    for ek, ls in [("exp0_calibration", "-"), ("exp1_no_cohort", "--")]:
        mean = agg[ek]["active_mean"]
        ms = [mean[s] for s in steps]
        ax2.plot(list(range(len(steps))), ms, color=EXP_COLORS[ek],
                lw=2.5, ls=ls, label=EXP_LABELS_CN[ek])
    for sp in sep_steps:
        idx = steps.index(sp)
        ax2.axvline(idx, color="gray", lw=0.8, ls="--", alpha=0.5)
    ax2.set_ylabel("活跃人数", fontsize=11)
    ax2.set_xlabel("模拟步数（每月一步）", fontsize=11)
    ax2.set_title("基线 vs 无届际更替：届际更替机制对协会规模的影响", fontsize=12)
    ax2.legend(loc="upper right", fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(list(range(len(steps))))
    ax2.set_xticklabels([f"M{(s%12)+1}" if s%12 in [0,6] else "" for s in steps], fontsize=7)

    plt.tight_layout()
    path = os.path.join(out_dir, "fig1_overall_trends.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  保存: {path}")


def plot_fig2_structure(agg, results, out_dir):
    """图2：人员结构演变（管理层/新生/老生的堆叠面积图）"""
    n_steps = results.get("n_steps", 60)
    steps = sorted(agg["exp0_calibration"]["active_mean"].keys())
    xs = list(range(len(steps)))

    # 使用基线实验
    mgr  = [agg["exp0_calibration"]["mgr_mean"].get(s, 0) for s in steps]
    fr   = [agg["exp0_calibration"]["fr_mean"].get(s, 0) for s in steps]
    sr   = [agg["exp0_calibration"]["sr_mean"].get(s, 0) for s in steps]

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.stackplot(xs, mgr, fr, sr,
                 labels=["管理层", "大一新生", "高年级志愿者"],
                 colors=[EXP_COLORS["exp0_calibration"],
                         "#90CAF9", "#FFCC80"],
                 alpha=0.85)
    # 9月标注
    for sp in [s for s in steps if s % 12 == 8]:
        idx = steps.index(sp)
        ax.axvline(idx, color="gray", lw=1, ls="--", alpha=0.6)
        ax.text(idx, 50, f"Y{sp//12+1}9月", fontsize=8, color="gray",
                rotation=90, va="bottom")

    ax.set_xlim(0, len(steps) - 1)
    ax.set_ylabel("志愿者人数", fontsize=12)
    ax.set_xlabel("模拟步数", fontsize=12)
    ax.set_title("图2 基线实验人员结构演变\n（堆叠面积图：管理层+大一新生+高年级志愿者）", fontsize=13)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(out_dir, "fig2_structure.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  保存: {path}")


def plot_fig3_policy_comparison(agg, results, out_dir):
    """图3：政策效果对比（多维度雷达图 + 柱状图）"""
    summaries = {ek: agg[ek]["summaries"] for ek in agg}

    # 6个实验的关键指标均值
    metrics = {
        "学年流失率": [],
        "管理层人数": [],
        "活跃人数":   [],
        "年创新次数": [],
        "满意度":    [],
    }
    labels = []
    for ek in EXP_LABELS_CN:
        reps = summaries[ek]
        if not reps:
            continue
        s = reps[0]
        ar = np.mean([r["annual_attrition_rate"] for r in reps])
        mgr = np.mean([r["manager_count"] for r in reps])
        act = np.mean([r["active_agents"] for r in reps])
        innov = np.mean([r["cum_innovation"] for r in reps]) / 3  # 3年平均
        sat = np.mean([r["avg_satisfaction"] for r in reps])
        metrics["学年流失率"].append(ar)
        metrics["管理层人数"].append(mgr)
        metrics["活跃人数"].append(act)
        metrics["年创新次数"].append(innov)
        metrics["满意度"].append(sat)
        labels.append(EXP_LABELS_CN[ek])

    # 柱状图对比
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    metric_titles = list(metrics.keys())
    for i, (mt, ax) in enumerate(zip(metric_titles, axes.flat)):
        vals = metrics[mt]
        bars = ax.bar(range(len(vals)), vals,
                      color=[EXP_COLORS[ek] for ek in EXP_LABELS_CN],
                      alpha=0.85, edgecolor="white", lw=0.5)
        ax.set_xticks(range(len(vals)))
        short_map = {
            '基线（校准）': '基线', '无届际更替': '无届际', '延长管理层任期': '延长任期',
            '增加活动经费': '更多经费', '强化激励政策': '强化激励', '减少招募规模': '少招募'
        }
        ax.set_xticklabels([short_map.get(l, l[:4]) for l in labels], fontsize=9, rotation=35, ha="right")
        ax.set_title(mt, fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")
        # 标注数值
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals) * 0.01,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=8)
        # 参考线（基线值）
        if i < len(vals):
            baseline = vals[0]
            ax.axhline(baseline, color="gray", ls="--", lw=1, alpha=0.6)

    axes.flat[-1].axis("off")  # 留空
    plt.suptitle("图3 政策实验多维度效果对比\n（各指标以基线实验为参考，虚线为基线值）",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "fig3_policy_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  保存: {path}")


def plot_fig4_calibration(agg, out_dir):
    """图4：校准验证（目标值 vs 模拟值，误差条）"""
    # 目标值（来自文献）
    targets = {
        "学年流失率": (0.40, "目标≈40%"),
        "管理层人数": (93,    "目标≈93人"),
        "活跃人数":   (674,   "目标≈674人"),
    }

    # 基线实验的模拟值
    reps0 = agg["exp0_calibration"]["summaries"]
    sim = {
        "学年流失率": np.mean([r["annual_attrition_rate"] for r in reps0]),
        "管理层人数": np.mean([r["manager_count"] for r in reps0]),
        "活跃人数":   np.mean([r["active_agents"] for r in reps0]),
    }
    sim_std = {
        "学年流失率": np.std([r["annual_attrition_rate"] for r in reps0]),
        "管理层人数": np.std([r["manager_count"] for r in reps0]),
        "活跃人数":   np.std([r["active_agents"] for r in reps0]),
    }

    mt_names = list(targets.keys())
    target_vals = [targets[m][0] for m in mt_names]
    sim_vals    = [sim[m] for m in mt_names]
    sim_err     = [sim_std[m] for m in mt_names]

    # 归一化（转换为相对误差%）
    norm_t = [100.0 for _ in mt_names]
    norm_s = [sim_vals[i] / target_vals[i] * 100.0 if target_vals[i] > 0 else 0
              for i in range(len(mt_names))]
    norm_e = [sim_err[i] / target_vals[i] * 100.0 if target_vals[i] > 0 else 0
              for i in range(len(mt_names))]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：绝对值对比
    ax = axes[0]
    x = np.arange(len(mt_names))
    width = 0.35
    ax.bar(x - width / 2, target_vals, width, label="文献目标值",
           color="#90A4AE", alpha=0.8, edgecolor="white")
    ax.bar(x + width / 2, sim_vals, width, yerr=sim_err,
           label="模拟均值±标准差", color=EXP_COLORS["exp0_calibration"],
           alpha=0.8, edgecolor="white", capsize=5)
    ax.set_xticks(x)
    ax.set_xticklabels(mt_names, fontsize=11)
    ax.set_ylabel("数值", fontsize=11)
    ax.set_title("校准验证：目标值 vs 模拟值", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    for i, (t, s) in enumerate(zip(target_vals, sim_vals)):
        ax.text(i - width/2, t + 2, f"{t:.1f}", ha="center", fontsize=9)
        ax.text(i + width/2, s + sim_err[i] + 5, f"{s:.1f}", ha="center", fontsize=9)

    # 右图：归一化相对误差
    ax2 = axes[1]
    colors = ["#4CAF50" if abs(n - 100) < 20 else "#FF5722" for n in norm_s]
    bars = ax2.bar(mt_names, [abs(n - 100) for n in norm_s],
                   color=colors, alpha=0.8, edgecolor="white")
    ax2.axhline(20, color="red", ls="--", lw=1.5, label="±20%误差线")
    ax2.axhline(0, color="gray", ls="-", lw=0.5)
    ax2.set_ylabel("相对误差 (%)", fontsize=11)
    ax2.set_title("模拟值相对目标值的误差率", fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis="y")
    for bar, ns in zip(bars, norm_s):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                abs(ns - 100) + 1,
                f"{abs(ns-100):.1f}%", ha="center", fontsize=9)

    plt.suptitle("图4 模型校准验证（绿色：误差<20%；红色：误差≥20%）",
                 fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    path = os.path.join(out_dir, "fig4_calibration.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  保存: {path}")


def plot_fig5_mechanisms(agg, out_dir):
    """图5：机制效应汇总（政策敏感性分析）"""
    summaries = {ek: agg[ek]["summaries"] for ek in agg}
    exps_order = ["exp0_calibration", "exp1_no_cohort", "exp2_extended_term",
                  "exp3_more_funding", "exp4_strong_reward", "exp5_less_recruit"]
    labels = [EXP_LABELS_CN[ek] for ek in exps_order]
    colors = [EXP_COLORS[ek] for ek in exps_order]

    ar_vals  = [np.mean([r["annual_attrition_rate"] for r in summaries[ek]]) * 100
                for ek in exps_order]
    mgr_vals = [np.mean([r["manager_count"] for r in summaries[ek]])
                for ek in exps_order]
    in_vals  = [np.mean([r["cum_innovation"] for r in summaries[ek]]) / 3
                for ek in exps_order]

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    for ax, vals, ylabel, title in zip(
        axes,
        [ar_vals, mgr_vals, in_vals],
        ["学年流失率 (%)", "管理层人数", "年均创新次数"],
        ["a) 学年流失率", "b) 管理层人数", "c) 年均项目创新次数"]
    ):
        bars = ax.bar(range(len(vals)), vals, color=colors, alpha=0.85,
                      edgecolor="white", lw=0.5)
        ax.set_xticks(range(len(vals)))
        short_map = {
            '基线（校准）': '基线', '无届际更替': '无届际', '延长管理层任期': '延长任期',
            '增加活动经费': '更多经费', '强化激励政策': '强化激励', '减少招募规模': '少招募'
        }
        short_labels = [short_map.get(l, l[:4]) for l in labels]
        ax.set_xticklabels(short_labels, fontsize=10, rotation=35, ha="right")
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals) * 0.02,
                    f"{v:.1f}", ha="center", va="bottom", fontsize=9)
        # 标注基线值
        ax.axhline(vals[0], color="gray", ls="--", lw=1, alpha=0.5)

    plt.suptitle("图5 机制效应汇总\n各政策对核心指标的边际效应（虚线=基线）",
                  fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    path = os.path.join(out_dir, "fig5_mechanisms.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  保存: {path}")


def run_sensitivity_experiments(out_dir):
    """运行敏感性分析实验并生成图6"""
    import sys, os
    sys.path.insert(0, out_dir)
    from abm_model import VolunteerFieldModel
    import numpy as np

    print("  运行敏感性分析实验（这需要约60秒）...")

    def single_run(params, steps=60, seed=42):
        model = VolunteerFieldModel(seed=seed, **params)
        for _ in range(steps):
            model.step()
        return model.get_summary()

    # 基准参数
    BASE = dict(
        recruitment_target=300,
        total_funding=10.0,
        manager_term=1,
        reward_threshold_low=20,
        enable_cohort_attrition=True,
        active_capacity=99999,
        innovation_base_prob=0.05,
        monthly_attrition_sat=0.065,
        monthly_attrition_acad=0.030,
        academic_pressure_grade1=0.30,
        academic_pressure_grade2=0.50,
        academic_pressure_grade3=0.70,
        academic_pressure_grade4=0.60,
        satisfaction_gain=0.05,
        satisfaction_loss=0.03,
        reward_sat_boost=0.08,
        enable_innovation=True,
        excellent_project_ratio=0.10,
        project_capacity=800,
        initial_managers=93,
    )

    # 敏感性实验：学业压力曲线变化
    acad_sensitivity = {}
    for g3_delta in [-0.10, 0, +0.10]:
        p = dict(BASE)
        p["academic_pressure_grade3"] = 0.70 + g3_delta
        reps = [single_run(p, seed=42+i) for i in range(5)]
        key = f"大三压力={0.70+g3_delta:.2f}"
        acad_sensitivity[key] = {
            "ar": np.mean([r["annual_attrition_rate"] for r in reps]),
            "ar_std": np.std([r["annual_attrition_rate"] for r in reps]),
        }

    # 敏感性实验：招募规模变化
    recruit_sensitivity = {}
    for target in [150, 200, 250, 300, 400]:
        p = dict(BASE)
        p["recruitment_target"] = target
        p["active_capacity"] = 900 if target < 300 else 99999
        reps = [single_run(p, seed=42+i) for i in range(5)]
        recruit_sensitivity[target] = {
            "active": np.mean([r["active_agents"] for r in reps]),
            "ar": np.mean([r["annual_attrition_rate"] for r in reps]),
        }

    # 敏感性实验：激励阈值变化
    reward_sensitivity = {}
    for thresh in [10, 15, 20, 25, 30]:
        p = dict(BASE)
        p["reward_threshold_low"] = thresh
        reps = [single_run(p, seed=42+i) for i in range(5)]
        reward_sensitivity[thresh] = {
            "sat": np.mean([r["avg_satisfaction"] for r in reps]),
            "rewards": np.mean([r["cum_rewards"] for r in reps]),
        }

    # 生成图6
    import matplotlib.pyplot as plt
    matplotlib.use('Agg')
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 左图：学业压力敏感性
    ax = axes[0]
    keys = list(acad_sensitivity.keys())
    vals = [acad_sensitivity[k]["ar"]*100 for k in keys]
    errs = [acad_sensitivity[k]["ar_std"]*100 for k in keys]
    colors = ["#4CAF50", "#2196F3", "#FF5722"]
    bars = ax.bar(keys, vals, yerr=errs, color=colors, alpha=0.8, capsize=5, edgecolor="white")
    ax.set_ylabel("学年流失率 (%)", fontsize=11)
    ax.set_title("学业压力敏感性分析", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, v+0.5, f"{v:.1f}%", ha="center", fontsize=10)

    # 中图：招募规模敏感性
    ax = axes[1]
    targets = sorted(recruit_sensitivity.keys())
    ar_vals = [recruit_sensitivity[t]["ar"]*100 for t in targets]
    act_vals = [recruit_sensitivity[t]["active"] for t in targets]
    ax2 = ax.twinx()
    ax.bar([str(t) for t in targets], ar_vals, color="#FF9800", alpha=0.7, label="学年流失率")
    ax2.plot([str(t) for t in targets], act_vals, "o-", color="#2196F3", linewidth=2, markersize=6, label="活跃人数")
    ax.set_xlabel("年度招募目标（人）", fontsize=11)
    ax.set_ylabel("学年流失率 (%)", fontsize=11, color="#FF9800")
    ax2.set_ylabel("活跃人数", fontsize=11, color="#2196F3")
    ax.set_title("招募规模敏感性分析", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, labels1+labels2, fontsize=9, loc="upper right")

    # 右图：激励阈值敏感性
    ax = axes[2]
    thresh_keys = sorted(reward_sensitivity.keys())
    sat_vals = [reward_sensitivity[t]["sat"] for t in thresh_keys]
    rew_vals = [reward_sensitivity[t]["rewards"] for t in thresh_keys]
    ax3 = ax.twinx()
    ax.plot([str(t) for t in thresh_keys], sat_vals, "s-", color="#4CAF50", linewidth=2, markersize=7, label="平均满意度")
    ax3.plot([str(t) for t in thresh_keys], rew_vals, "^-", color="#9C27B0", linewidth=2, markersize=7, label="累计激励次数")
    ax.set_xlabel("激励阈值", fontsize=11)
    ax.set_ylabel("平均满意度", fontsize=11, color="#4CAF50")
    ax3.set_ylabel("累计激励次数", fontsize=11, color="#9C27B0")
    ax.set_title("激励阈值敏感性分析", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    lines3, labels3 = ax.get_legend_handles_labels()
    lines4, labels4 = ax3.get_legend_handles_labels()
    ax.legend(lines3+lines4, labels3+labels4, fontsize=9, loc="upper right")

    plt.suptitle("图6 敏感性分析：关键参数变化对核心指标的影响", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "fig6_sensitivity.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  保存: {path}")
    return path
def generate_all_figures():
    print("加载实验结果...")
    results = load_results()
    agg = aggregate(results)
    out_dir = OUTPUT_DIR

    print("生成图表...")
    plot_fig1_trends(agg, results, out_dir)
    plot_fig2_structure(agg, results, out_dir)
    plot_fig3_policy_comparison(agg, results, out_dir)
    plot_fig4_calibration(agg, out_dir)
    plot_fig5_mechanisms(agg, out_dir)
    run_sensitivity_experiments(out_dir)
    print("图表生成完成！")


if __name__ == "__main__":
    generate_all_figures()

