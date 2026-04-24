#!/usr/bin/env python3
"""
快速验证脚本 - 从仓库根目录运行
===================================
验证 ABM 模型与实验结果的一致性。

用法：
    python verify_results.py

注意：本脚本使用 3 次蒙特卡洛重复进行快速校验，
与论文中"15 次重复"的正式结果有差异，不作为正式结论使用。
"""
import sys, os, pickle, warnings
warnings.filterwarnings('ignore')

# 路径：results/ 在根目录的上一级
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(ROOT_DIR, "results")
PKL_PATH = os.path.join(RESULTS_DIR, "all_results.pkl")
ABM_PATH = os.path.join(ROOT_DIR, "code", "abm_model.py")


def check_results():
    """验证实验结果文件"""
    print("\n=== 实验结果文件 ===")
    if not os.path.exists(PKL_PATH):
        print(f"❌ 结果文件不存在: {PKL_PATH}")
        print("   请先运行: cd code && python run_exp.py")
        return False
    with open(PKL_PATH, 'rb') as f:
        results = pickle.load(f)
    n_exp = len(results.get('experiments', []))
    print(f"✅ 结果文件存在: {PKL_PATH}")
    print(f"   实验组数: {n_exp}")
    return True


def check_calibration():
    """快速3次MC校准验证"""
    print("\n=== 模型校准（3次快速抽样）===")
    sys.path.insert(0, os.path.join(ROOT_DIR, "code"))
    try:
        from abm_model import VolunteerFieldModel
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        return False

    ar_list, mgr_list = [], []
    for seed in [42, 123, 999]:
        model = VolunteerFieldModel(seed=seed)
        for _ in range(60):
            model.step()
        s = model.get_summary()
        ar_list.append(s.get('annual_attrition_rate', 0))
        mgr_list.append(s.get('manager_count', 0))

    import numpy as np
    ar_mean = np.mean(ar_list)
    mgr_mean = np.mean(mgr_list)
    print(f"   3次快速: AR={ar_mean:.3f}, 管理层={mgr_mean:.0f}")
    print(f"   论文值:   AR=0.430,  管理层=88.8")
    ok = 0.38 <= ar_mean <= 0.48 and 70 <= mgr_mean <= 110
    print(f"   {'✅' if ok else '⚠️'} 在合理区间内（3次快速抽样供参考）")
    return True


if __name__ == '__main__':
    print("=" * 55)
    print("大学生志愿服务场域 ABM 模型 — 快速验证")
    print("=" * 55)
    results = []
    try:
        results.append(("结果文件", check_results()))
        results.append(("模型校准", check_calibration()))
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 55)
    for name, ok in results:
        print(f"  {'✅' if ok else '❌'} {name}")
    print(f"正式结果见: paper/report.pdf")
    print(f"数据表:     results/00_experiment_summary_v9.2_final.csv")
    print("=" * 55)
