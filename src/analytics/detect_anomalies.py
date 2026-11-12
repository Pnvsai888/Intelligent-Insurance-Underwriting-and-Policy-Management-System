#!/usr/bin/env python3
"""
Anomaly Detection & Ground-Truth Benchmark Engine (Section 5 Compliance)
Scans datasets to detect the 5 negative scenarios and calculates:
- True Positives (TP)
- False Positives (FP)
- False Negatives (FN)
- True Negatives (TN)
- Precision, Recall, and F1-Score
"""

import csv
import os
from datetime import datetime
from decimal import Decimal

DIR = "./underwriting_data"


def load_csv(filename):
    with open(os.path.join(DIR, filename), mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_anomaly_detection_benchmark():
    # 1. Load data
    quotes = {q["quote_id"]: q for q in load_csv("quotes.csv")}
    decisions = {d["quote_id"]: d for d in load_csv(
        "underwriting_decisions.csv")}
    products = {p["product_id"]: p for p in load_csv("products.csv")}
    policies = load_csv("policies.csv")
    endorsements = load_csv("endorsements.csv")
    renewals = load_csv("renewals.csv")
    ground_truth = {gt["record_id"]: gt["issue_type"]
                    for gt in load_csv("ground_truth.csv")}

    detected_anomalies = {}  # record_id -> detected issue_type

    # ----------------------------------------------------
    # Detector 1: Policy issued without acceptance/approval
    # ----------------------------------------------------
    for p in policies:
        pid = p["policy_id"]
        qid = p["quote_id"]
        quote = quotes.get(qid)
        if quote and quote["status"] != "APPROVED":
            detected_anomalies[pid] = "ISSUED_WITHOUT_APPROVAL"

    # ----------------------------------------------------
    # Detector 2: Premium outside defined rate formula
    # ----------------------------------------------------
    for p in policies:
        pid = p["policy_id"]
        qid = p["quote_id"]
        quote = quotes.get(qid)
        if quote and pid not in detected_anomalies:
            expected_prem = Decimal(quote["calculated_premium"])
            actual_prem = Decimal(p["total_premium"])
            if expected_prem != actual_prem:
                detected_anomalies[pid] = "PREMIUM_FORMULA_MISMATCH"

    # ----------------------------------------------------
    # Detector 3: Endorsement exceeds product limit
    # ----------------------------------------------------
    policy_map = {p["policy_id"]: p for p in policies}
    for e in endorsements:
        eid = e["endorsement_id"]
        pol = policy_map.get(e["policy_id"])
        if pol:
            prod = products.get(pol["product_id"])
            quote = quotes.get(pol["quote_id"])
            if prod and quote:
                original_si = Decimal(quote["sum_insured"])
                delta_si = Decimal(e["delta_sum_insured"])
                max_si = Decimal(prod["max_sum_insured"])
                if (original_si + delta_si) > max_si:
                    detected_anomalies[eid] = "ENDORSEMENT_EXCEEDS_CAPACITY"

    # ----------------------------------------------------
    # Detector 4: Renewal generated for cancelled policy
    # ----------------------------------------------------
    for r in renewals:
        rid = r["renewal_id"]
        prior_pol = policy_map.get(r["prior_policy_id"])
        if prior_pol and prior_pol["policy_status"] == "CANCELLED":
            detected_anomalies[rid] = "RENEWAL_GENERATED_ON_CANCELLED_POLICY"

    # ----------------------------------------------------
    # Detector 5: Overlapping policy periods
    # ----------------------------------------------------
    # Check renewals that bound new policies
    date_fmt = "%Y-%m-%d"
    for r in renewals:
        if r["new_policy_id"] and r["new_policy_id"] in policy_map:
            new_pol = policy_map[r["new_policy_id"]]
            prior_pol = policy_map[r["prior_policy_id"]]
            new_eff = datetime.strptime(new_pol["effective_date"], date_fmt)
            prior_exp = datetime.strptime(
                prior_pol["expiration_date"], date_fmt)
            if new_eff < prior_exp:
                detected_anomalies[new_pol["policy_id"]
                                   ] = "OVERLAPPING_POLICY_PERIOD"

    # ----------------------------------------------------
    # Benchmark against Ground Truth (Evaluation Metrics)
    # ----------------------------------------------------
    all_evaluated_record_ids = (
        set(p["policy_id"] for p in policies) |
        set(e["endorsement_id"] for e in endorsements) |
        set(r["renewal_id"] for r in renewals)
    )

    tp = 0  # True Positive: in ground truth and detected correctly
    fp = 0  # False Positive: detected as anomaly but not in ground truth
    fn = 0  # False Negative: in ground truth but not detected
    tn = 0  # True Negative: clean record and not detected

    category_stats = {
        "ISSUED_WITHOUT_APPROVAL": {"TP": 0, "FP": 0, "FN": 0},
        "PREMIUM_FORMULA_MISMATCH": {"TP": 0, "FP": 0, "FN": 0},
        "ENDORSEMENT_EXCEEDS_CAPACITY": {"TP": 0, "FP": 0, "FN": 0},
        "RENEWAL_GENERATED_ON_CANCELLED_POLICY": {"TP": 0, "FP": 0, "FN": 0},
        "OVERLAPPING_POLICY_PERIOD": {"TP": 0, "FP": 0, "FN": 0},
    }

    for rid in all_evaluated_record_ids:
        actual_anomaly = ground_truth.get(rid)
        predicted_anomaly = detected_anomalies.get(rid)

        if actual_anomaly and predicted_anomaly:
            if actual_anomaly == predicted_anomaly:
                tp += 1
                category_stats[actual_anomaly]["TP"] += 1
            else:
                # Misclassified anomaly category
                fp += 1
                fn += 1
        elif not actual_anomaly and predicted_anomaly:
            fp += 1
            category_stats[predicted_anomaly]["FP"] += 1
        elif actual_anomaly and not predicted_anomaly:
            fn += 1
            category_stats[actual_anomaly]["FN"] += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision +
                                     recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / \
        len(all_evaluated_record_ids) if all_evaluated_record_ids else 0.0

    print("===============================================================")
    print("        ANOMALY & EXCEPTION DETECTION BENCHMARK REPORT         ")
    print("===============================================================")
    print(
        f"Total Operational Records Audited:      {len(all_evaluated_record_ids)}")
    print(f"Total Injected Ground Truth Anomalies:  {len(ground_truth)}")
    print(f"Total Anomalies Flagged by Engine:      {len(detected_anomalies)}")
    print("---------------------------------------------------------------")
    print(f"True Positives  (TP) : {tp:<6} | False Positives (FP) : {fp}")
    print(f"False Negatives (FN) : {fn:<6} | True Negatives  (TN) : {tn}")
    print("---------------------------------------------------------------")
    print(f"Precision : {precision:.4f} ({precision * 100:.2f}%)")
    print(f"Recall    : {recall:.4f} ({recall * 100:.2f}%)")
    print(f"F1-Score  : {f1:.4f} ({f1 * 100:.2f}%)")
    print(f"Accuracy  : {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print("---------------------------------------------------------------")
    print("PER-CATEGORY DETECTION BREAKDOWN:")
    for cat, stats in category_stats.items():
        print(
            f" - {cat:<38}: TP={stats['TP']:<2} FP={stats['FP']:<2} FN={stats['FN']:<2}")
    print("===============================================================")


if __name__ == "__main__":
    run_anomaly_detection_benchmark()
