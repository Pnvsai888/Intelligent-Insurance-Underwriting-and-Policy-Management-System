#!/usr/bin/env python3
"""
Underwriting & Policy Lifecycle Executive Dashboard (Step 17)
"""
import json
import os

METRICS_PATH = "./outputs/evaluation_metrics.json"


def render_dashboard():
    if not os.path.exists(METRICS_PATH):
        print("[ERROR] Please run src/analytics/generate_outputs.py first.")
        return

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    kpis = data["underwriting_kpis"]
    anom = data["anomaly_detection_benchmark"]

    print("=" * 66)
    print("      YOTTAFLEX INSURANCE UNDERWRITING & LIFECYCLE DASHBOARD      ")
    print("=" * 66)
    print(f"  Deterministic System Seed : {data['seed']}")
    print(f"  Execution Scale Target    : {data['system_scale'].upper()}")
    print("-" * 66)
    print("  SUBMISSION & UNDERWRITING TRIAGE")
    print(
        f"  • Total Submissions Evaluated  : {kpis['total_submissions_evaluated']:,}")
    print(
        f"  • Straight-Through (STP) Rate  : {kpis['straight_through_processing_rate_pct']:.2f}% ({kpis['straight_through_processing_count']:,} auto-approved)")
    print(f"  • Manual Referrals (L1 / SVP)  : {kpis['referral_count']:,}")
    print(f"  • Declined Submissions         : {kpis['decline_count']:,}")
    print("-" * 66)
    print("  ANOMALY DETECTION & EXCEPTION BENCHMARK")
    print(
        f"  • Total Operations Audited     : {anom['total_records_audited']:,}")
    print(
        f"  • Ground Truth Defect Cases    : {anom['true_positives'] + anom['false_negatives']}")
    print(
        f"  • Confusion Matrix             : TP={anom['true_positives']} | FP={anom['false_positives']} | FN={anom['false_negatives']} | TN={anom['true_negatives']}")
    print(f"  • Detection Precision          : {anom['precision'] * 100:.2f}%")
    print(f"  • Detection Recall             : {anom['recall'] * 100:.2f}%")
    print(f"  • Balanced F1-Score            : {anom['f1_score']:.4f}")
    print(f"  • Overall Pipeline Accuracy    : {anom['accuracy'] * 100:.2f}%")
    print("=" * 66)


if __name__ == "__main__":
    render_dashboard()
