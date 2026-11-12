"""
Benchmark & Performance Metrics Suite
"""
import csv
import os

DIR = "./underwriting_data"


def compute_metrics():
    with open(os.path.join(DIR, "quotes.csv")) as f:
        quotes = {q["quote_id"]: q for q in csv.DictReader(f)}
    with open(os.path.join(DIR, "underwriting_decisions.csv")) as f:
        decisions = {d["quote_id"]: d for d in csv.DictReader(f)}
    with open(os.path.join(DIR, "ground_truth.csv")) as f:
        ground_truth = list(csv.DictReader(f))

    total_quotes = len(quotes)
    stp_count = sum(1 for d in decisions.values(
    ) if d["authority_level"] == "STP_SYSTEM" and d["decision"] == "AUTO_APPROVE")
    referrals = sum(1 for d in decisions.values()
                    if d["decision"] == "REFERRAL")
    declines = sum(1 for d in decisions.values() if d["decision"] == "DECLINE")
    stp_rate = (stp_count / total_quotes) * 100

    print("================ UNDERWRITING KPI METRICS ================")
    print(f"Total Submissions Evaluated:             {total_quotes}")
    print(f"Straight-Through Processing (STP) Rate:  {stp_rate:.2f}%")
    print(f"Referral Review Count (L1 & SVP):        {referrals}")
    print(f"Declined Submissions:                    {declines}")
    print(f"Injected Ground Truth Anomalies:         {len(ground_truth)}")
    print("=========================================================")


if __name__ == "__main__":
    compute_metrics()
