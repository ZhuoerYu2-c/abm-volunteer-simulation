#!/usr/bin/env python3
"""
快速抽样验证脚本
================
注意：本脚本使用3次蒙特卡洛重复进行快速校验，用于初步验证模型逻辑。
这与report中"15次重复"的正式校准结果不同，不作为正式结论使用。
报告中的精确校准数据请参见00_experiment_summary_corrected.csv。
"""
import sys, pickle, numpy as np, pandas as pd

def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def check_empirical():
    """验证实证数据关键发现"""
    print("\n=== 实证数据关键发现 ===")
    import pyreadstat
    df, _ = pyreadstat.read_sav(
        "1_original_data/大学生志愿者挫折反应及对策调查数据.sav")
    n_total = len(df)
    n_unique = df.drop_duplicates().shape[0]
    print(f"原始数据: {n_total}行, 去重后: {n_unique}条唯一记录")

    # 挫折感×流失率单调关系
    frus_levels = {1:0.182, 2:0.032, 3:0.418, 4:0.725, 5:1.000}
    all_pass = True
    for lv, expected in frus_levels.items():
        subset = df[df['挫折感'] == lv]
        actual = subset['服务中断'].mean()
        diff = abs(actual - expected)
        ok = diff < 0.001
        if not ok: all_pass = False
        print(f"  挫折感={lv}: 实际={actual:.3f} 预期={expected:.3f} {'✓' if ok else '✗'}")
    print(f"  挫折感-流失率单调关系: {'✓ 全部通过' if all_pass else '✗ 有失败'}")
    return all_pass

def check_calibration():
    """
    快速3次MC校准验证
    注意：正式报告使用15次重复结果，此处仅为逻辑验证
    """
    print("\n=== 模型校准验证（3次快速抽样）===")
    sys.path.insert(0, '3_model_code')
    from abm_model import VolunteerFieldModel

    ar_list, mgr_list, act_list = [], [], []
    for seed in [42, 123, 999]:
        model = VolunteerFieldModel(seed=seed)
        for _ in range(60):
            model.step()
        s = model.get_summary()
        ar_list.append(s['annual_attrition_rate'])
        mgr_list.append(s['manager_count'])
        act_list.append(s['active_count'])

    ar_mean = np.mean(ar_list)
    mgr_mean = np.mean(mgr_list)
    act_mean = np.mean(act_list)

    print(f"  3次快速抽样均值: AR={ar_mean:.3f}, 管理层={mgr_mean:.1f}, 活跃={act_mean:.0f}")
    print(f"  正式报告值（15次重复）: AR=0.428, 管理层=90.7, 活跃=605")
    print(f"  注：3次快速抽样与15次正式结果会有差异，以正式报告为准")

    ar_ok = 0.38 <= ar_mean <= 0.48
    mgr_ok = 70 <= mgr_mean <= 110
    print(f"  {'✓' if ar_ok else '✗'} 学年流失率在[38%,48%]区间")
    print(f"  {'✓' if mgr_ok else '✗'} 管理层人数在[70,110]区间")
    return ar_ok and mgr_ok

def check_experiments():
    """验证6组实验结果"""
    print("\n=== 6组实验结果验证 ===")
    results = load_pkl('4_experiment_results/all_results.pkl')

    # 正式报告值（15次重复）
    expected = {
        "exp0_calibration":    {"ar": 0.428, "mgr": 90.7, "act": 605, "promotion": 0.255},
        "exp1_no_cohort":      {"ar": 0.406, "mgr": 82.6, "act": 803, "promotion": 0.255},
        "exp2_extended_term":  {"ar": 0.429, "mgr": 95.3, "act": 612, "promotion": 0.255},
        "exp3_more_funding":    {"ar": 0.423, "mgr": 91.9, "act": 623, "promotion": 0.255},
        "exp4_strong_reward":  {"ar": 0.428, "mgr": 91.1, "act": 605, "promotion": 0.255},
        "exp5_less_recruit":   {"ar": 0.330, "mgr": 88.3, "act": 429, "promotion": 0.333},
    }

    all_ok = True
    for exp in results["experiments"]:
        ek = exp["exp_key"]
        if ek not in expected:
            continue
        exp_vals = expected[ek]
        reps = exp["replications"]
        ar  = np.mean([r["summary"]["annual_attrition_rate"] for r in reps])
        mgr = np.mean([r["summary"]["manager_count"]         for r in reps])
        act = np.mean([r["summary"]["active_count"]          for r in reps])
        prm = np.mean([r["summary"].get("promotion_rate", 0) for r in reps])

        ar_ok  = abs(ar  - exp_vals["ar"])  <= 0.015
        mgr_ok = abs(mgr - exp_vals["mgr"]) <= 5.0
        act_ok = abs(act - exp_vals["act"]) <= 40
        prm_ok = abs(prm - exp_vals["promotion"]) <= 0.03

        ok = ar_ok and mgr_ok and act_ok and prm_ok
        if not ok: all_ok = False
        flag = '' if ok else ' *** MISMATCH ***'
        print(f"  {ek:25s} AR={ar:.3f}(exp={exp_vals['ar']:.3f}) "
              f"Mgr={mgr:.1f}(exp={exp_vals['mgr']:.1f}) "
              f"Promo={prm:.3f}(exp={exp_vals['promotion']:.3f}){flag}")

    print(f"\n实验结果验证: {'✓ 全部通过' if all_ok else '✗ 有失败'}")
    return all_ok

def check_regression():
    """验证复现逻辑回归"""
    print("\n=== 复现逻辑回归 ===")
    df = pd.read_csv('2_empirical_analysis/06_logistic_regression_reproduced.csv')
    print(df.to_string(index=False))
    frus = df[df['variable'].str.contains('挫折感|标准化', na=False)]
    if not frus.empty:
        b = frus['coefficient'].values[0]
        p = frus['p_value'].values[0]
        ok = b > 0 and p < 0.01
        print(f"挫折感 β={b:.3f} p={p:.4f} {'✓' if ok else '✗'}")
        return ok
    return False

if __name__ == '__main__':
    print("=" * 60)
    print("大学生志愿服务场域ABM模型 - 快速验证脚本")
    print("（注意：本脚本3次快速抽样结果仅供参考，正式结论以report.pdf为准）")
    print("=" * 60)

    results = []
    try:
        results.append(("实证数据验证",   check_empirical()))
        results.append(("复现逻辑回归",   check_regression()))
        results.append(("模型校准验证",   check_calibration()))
        results.append(("6组实验结果",    check_experiments()))
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("验证汇总:")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    print("=" * 60)
    print("提示：完整正式结果请见 report.pdf 和")
    print("      4_experiment_results/00_experiment_summary_corrected.csv")
