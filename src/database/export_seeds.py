#!/usr/bin/env python3
"""
Exports structured JSON records into data/generated/
"""
import csv
import json
import os

DIR = "./data/generated"
TABLES = [
    "applicants", "insured_assets", "products", "coverage_options",
    "risk_factors", "quotes", "underwriting_decisions", "policies",
    "endorsements", "renewals"
]


def export_json():
    for table in TABLES:
        csv_path = os.path.join(DIR, f"{table}.csv")
        json_path = os.path.join(DIR, f"{table}.json")
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8") as f:
                data = list(csv.DictReader(f))
            with open(json_path, mode="w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    print("[SUCCESS] All 10 entity JSON files exported into data/generated/")


if __name__ == "__main__":
    export_json()
