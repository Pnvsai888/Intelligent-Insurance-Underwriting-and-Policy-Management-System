#!/usr/bin/env python3
"""
Synthetic Data Generation Engine (Section 4 Compliance)
Usage:
    python generate_data.py --scale starter --seed 20261022
    python generate_data.py --scale full --seed 20261022
"""

import argparse
import csv
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

# Product Lines & Master Rules
PRODUCTS = [
    {
        "product_id": "PRD-PROP-01",
        "product_name": "Commercial Property Shield",
        "target_asset_type": "COMMERCIAL_PROPERTY",
        "min_credit_score": 600,
        "max_loss_count": 2,
        "max_sum_insured": Decimal("50000000.00"),
        "base_rate": Decimal("0.0200")
    },
    {
        "product_id": "PRD-AUTO-01",
        "product_name": "Fleet & Auto Complete",
        "target_asset_type": "PRIVATE_VEHICLE",
        "min_credit_score": 580,
        "max_loss_count": 3,
        "max_sum_insured": Decimal("15000000.00"),
        "base_rate": Decimal("0.0350")
    },
    {
        "product_id": "PRD-CYBR-01",
        "product_name": "Cyber Threat Defense",
        "target_asset_type": "CYBER_INFRASTRUCTURE",
        "min_credit_score": 650,
        "max_loss_count": 1,
        "max_sum_insured": Decimal("30000000.00"),
        "base_rate": Decimal("0.0250")
    }
]

COVERAGE_OPTIONS = [
    {"coverage_id": "COV-PROP-BASE", "product_id": "PRD-PROP-01",
        "coverage_name": "Building Fire & Perils", "deductible": 50000.00, "coverage_limit": 50000000.00},
    {"coverage_id": "COV-PROP-BI",   "product_id": "PRD-PROP-01",
        "coverage_name": "Business Interruption",   "deductible": 25000.00, "coverage_limit": 10000000.00},
    {"coverage_id": "COV-PROP-EQ",   "product_id": "PRD-PROP-01",
        "coverage_name": "Earthquake & Natural Perils", "deductible": 75000.00, "coverage_limit": 30000000.00},
    {"coverage_id": "COV-AUTO-COLL", "product_id": "PRD-AUTO-01",
        "coverage_name": "Collision & Accidental",   "deductible": 10000.00, "coverage_limit": 15000000.00},
    {"coverage_id": "COV-AUTO-TP",   "product_id": "PRD-AUTO-01",
        "coverage_name": "Third-Party Liability",   "deductible": 5000.00,  "coverage_limit": 10000000.00},
    {"coverage_id": "COV-AUTO-COMP", "product_id": "PRD-AUTO-01",
        "coverage_name": "Comprehensive Theft/Fire", "deductible": 15000.00, "coverage_limit": 12000000.00},
    {"coverage_id": "COV-CYBR-RANS", "product_id": "PRD-CYBR-01", "coverage_name": "Extortion & Ransom",
        "deductible": 100000.00, "coverage_limit": 30000000.00},
    {"coverage_id": "COV-CYBR-BRCH", "product_id": "PRD-CYBR-01",
        "coverage_name": "Data Breach Notification", "deductible": 50000.00, "coverage_limit": 15000000.00},
    {"coverage_id": "COV-CYBR-BI",   "product_id": "PRD-CYBR-01",
        "coverage_name": "Network Interruption",     "deductible": 150000.00, "coverage_limit": 20000000.00},
]

RISK_FACTORS = [
    {"risk_factor_id": "RF-CR-01", "dimension": "CREDIT_TIER",
        "bucket_min": 300, "bucket_max": 579, "multiplier": 1.500},
    {"risk_factor_id": "RF-CR-02", "dimension": "CREDIT_TIER",
        "bucket_min": 580, "bucket_max": 669, "multiplier": 1.200},
    {"risk_factor_id": "RF-CR-03", "dimension": "CREDIT_TIER",
        "bucket_min": 670, "bucket_max": 749, "multiplier": 1.000},
    {"risk_factor_id": "RF-CR-04", "dimension": "CREDIT_TIER",
        "bucket_min": 750, "bucket_max": 850, "multiplier": 0.850},
    {"risk_factor_id": "RF-LH-01", "dimension": "LOSS_HISTORY",
        "bucket_min": 0, "bucket_max": 0, "multiplier": 0.900},
    {"risk_factor_id": "RF-LH-02", "dimension": "LOSS_HISTORY",
        "bucket_min": 1, "bucket_max": 1, "multiplier": 1.150},
    {"risk_factor_id": "RF-LH-03", "dimension": "LOSS_HISTORY",
        "bucket_min": 2, "bucket_max": 2, "multiplier": 1.400},
    {"risk_factor_id": "RF-LH-04", "dimension": "LOSS_HISTORY",
        "bucket_min": 3, "bucket_max": 3, "multiplier": 1.750},
    {"risk_factor_id": "RF-LH-05", "dimension": "LOSS_HISTORY",
        "bucket_min": 4, "bucket_max": 10, "multiplier": 2.200},
    {"risk_factor_id": "RF-AR-01", "dimension": "ASSET_RISK",
        "bucket_min": 1.0, "bucket_max": 2.99, "multiplier": 0.800},
    {"risk_factor_id": "RF-AR-02", "dimension": "ASSET_RISK",
        "bucket_min": 3.0, "bucket_max": 4.99, "multiplier": 0.950},
    {"risk_factor_id": "RF-AR-03", "dimension": "ASSET_RISK",
        "bucket_min": 5.0, "bucket_max": 6.99, "multiplier": 1.100},
    {"risk_factor_id": "RF-AR-04", "dimension": "ASSET_RISK",
        "bucket_min": 7.0, "bucket_max": 8.49, "multiplier": 1.350},
    {"risk_factor_id": "RF-AR-05", "dimension": "ASSET_RISK",
        "bucket_min": 8.5, "bucket_max": 10.0, "multiplier": 1.800},
]


def get_credit_multiplier(score):
    if score is None:
        return Decimal("1.250")
    for rf in RISK_FACTORS:
        if rf["dimension"] == "CREDIT_TIER" and rf["bucket_min"] <= score <= rf["bucket_max"]:
            return Decimal(str(rf["multiplier"]))
    return Decimal("1.000")


def get_loss_multiplier(count):
    for rf in RISK_FACTORS:
        if rf["dimension"] == "LOSS_HISTORY" and rf["bucket_min"] <= count <= rf["bucket_max"]:
            return Decimal(str(rf["multiplier"]))
    return Decimal("2.000")


def calculate_premium(sum_insured, base_rate, credit_score, loss_count, asset_risk_score):
    c_mult = get_credit_multiplier(credit_score)
    l_mult = get_loss_multiplier(loss_count)
    a_mult = (Decimal(str(asset_risk_score)) /
              Decimal("5.000")).quantize(Decimal("0.001"))
    total = sum_insured * base_rate * c_mult * l_mult * a_mult
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_dataset(scale="full", seed=20261022, output_dir="./underwriting_data"):
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    # Volume scales
    if scale == "starter":
        num_applicants = 300
        num_quotes = 400
        num_base_policies = 200
        num_endorsements = 60
        num_renewals = 120
    else:  # full
        num_applicants = 3000
        num_quotes = 4000
        num_base_policies = 2000
        num_endorsements = 600
        num_renewals = 1200

    BASE_DATE = datetime(2026, 1, 1, 9, 0, 0)
    applicants, insured_assets, quotes, uw_decisions = [], [], [], []
    policies, endorsements, renewals, ground_truth = [], [], [], []

    # 1. Applicants
    for i in range(1, num_applicants + 1):
        app_id = f"APP-2026-{i:06d}"
        etype = random.choices(["INDIVIDUAL", "SME", "ENTERPRISE"], weights=[
                               0.45, 0.40, 0.15])[0]
        is_missing_data = (random.random() < 0.02)
        credit_score = None if is_missing_data else random.randint(450, 850)
        loss_history = random.choices([0, 1, 2, 3, 4], weights=[
                                      0.60, 0.25, 0.10, 0.03, 0.02])[0]
        revenue = None if etype == "INDIVIDUAL" else round(
            random.uniform(500000, 100000000), 2)
        jurisdiction = random.choice(["MH", "KA", "DL", "TN", "GJ"])
        created_at = BASE_DATE + \
            timedelta(days=random.randint(0, 180),
                      minutes=random.randint(0, 1440))

        applicants.append({
            "applicant_id": app_id,
            "entity_type": etype,
            "credit_score": credit_score if credit_score is not None else "",
            "loss_history_count_3yr": loss_history,
            "annual_revenue": revenue if revenue is not None else "",
            "jurisdiction": jurisdiction,
            "created_at": created_at.isoformat()
        })

    # 2. Insured Assets
    asset_counter = 1
    for app in applicants:
        num_assets = random.choices([1, 2], weights=[0.8, 0.2])[0]
        for _ in range(num_assets):
            ast_id = f"AST-2026-{asset_counter:06d}"
            asset_counter += 1
            atype = random.choice(
                ["COMMERCIAL_PROPERTY", "PRIVATE_VEHICLE", "CYBER_INFRASTRUCTURE"])
            val_map = {
                "COMMERCIAL_PROPERTY": (5000000, 45000000),
                "PRIVATE_VEHICLE": (400000, 12000000),
                "CYBER_INFRASTRUCTURE": (1000000, 28000000)
            }
            dec_val = round(random.uniform(*val_map[atype]), 2)
            r_score = round(random.uniform(1.5, 9.5), 2)

            insured_assets.append({
                "asset_id": ast_id,
                "applicant_id": app["applicant_id"],
                "asset_type": atype,
                "declared_value": dec_val,
                "construction_type_or_make": "STANDARD_CLASS",
                "asset_risk_score": r_score
            })

    app_lookup = {a["applicant_id"]: a for a in applicants}
    prod_lookup = {p["product_id"]: p for p in PRODUCTS}

    # 3. Quotes & Decisions
    for q_idx in range(1, num_quotes + 1):
        qid = f"QTE-2026-{q_idx:06d}"
        asset = random.choice(insured_assets)
        app = app_lookup[asset["applicant_id"]]
        prod = [p for p in PRODUCTS if p["target_asset_type"]
                == asset["asset_type"]][0]

        sum_insured = Decimal(str(asset["declared_value"]))
        c_score = int(app["credit_score"]
                      ) if app["credit_score"] != "" else None
        l_hist = int(app["loss_history_count_3yr"])
        a_score = Decimal(str(asset["asset_risk_score"]))

        calc_prem = calculate_premium(
            sum_insured, prod["base_rate"], c_score, l_hist, a_score)
        created_dt = datetime.fromisoformat(
            app["created_at"]) + timedelta(days=random.randint(1, 10))
        expires_dt = created_dt + timedelta(days=30)

        referral_reasons = []
        if c_score is None:
            referral_reasons.append("MISSING_CREDIT_DATA")
        elif c_score < prod["min_credit_score"]:
            referral_reasons.append("CREDIT_SCORE_BELOW_PRODUCT_MIN")
        if l_hist > prod["max_loss_count"]:
            referral_reasons.append("EXCESSIVE_LOSS_HISTORY")
        if sum_insured > Decimal("25000000.00"):
            referral_reasons.append("CAPACITY_EXCEEDS_TIER_1")
        if a_score > Decimal("8.00"):
            referral_reasons.append("HIGH_ASSET_RISK_FACTOR")

        dec_id = f"UWD-2026-{q_idx:06d}"
        if not referral_reasons:
            uw_decision, authority, decided_by, quote_status = "AUTO_APPROVE", "STP_SYSTEM", "SYS_RULES_ENGINE", "APPROVED"
        elif "EXCESSIVE_LOSS_HISTORY" in referral_reasons or "CAPACITY_EXCEEDS_TIER_1" in referral_reasons:
            uw_decision, authority, decided_by, quote_status = "REFERRAL", "SENIOR_VP", "EMP_SVP_99", "REFERRED"
        elif "MISSING_CREDIT_DATA" in referral_reasons:
            uw_decision, authority, decided_by, quote_status = "REFERRAL", "UNDERWRITER_L1", "EMP_UW_12", "REFERRED"
        else:
            uw_decision, authority, decided_by, quote_status = "DECLINE", "UNDERWRITER_L1", "EMP_UW_12", "DECLINED"

        quotes.append({
            "quote_id": qid,
            "applicant_id": app["applicant_id"],
            "asset_id": asset["asset_id"],
            "product_id": prod["product_id"],
            "sum_insured": f"{sum_insured:.2f}",
            "calculated_premium": f"{calc_prem:.2f}",
            "status": quote_status,
            "created_at": created_dt.isoformat(),
            "expires_at": expires_dt.isoformat()
        })
        uw_decisions.append({
            "decision_id": dec_id,
            "quote_id": qid,
            "authority_level": authority,
            "decision": uw_decision,
            "reasons": "|".join(referral_reasons) if referral_reasons else "NONE",
            "decided_by": decided_by,
            "decided_at": (created_dt + timedelta(hours=random.randint(1, 24))).isoformat()
        })

    # 4. Policies & Anomalies
    approved_quotes = [q for q in quotes if q["status"] == "APPROVED"]
    non_approved_quotes = [
        q for q in quotes if q["status"] in ["DECLINED", "REFERRED"]]

    # Proportional injection limits
    inj_unauth_count = 15 if scale == "full" else 2
    inj_prem_tamper_count = 10 if scale == "full" else 1

    injected_unauth = non_approved_quotes[:inj_unauth_count]
    eligible_quotes = approved_quotes[:(
        num_base_policies - len(injected_unauth))]
    selected_quotes = eligible_quotes + injected_unauth

    pol_counter = 1
    for q in selected_quotes:
        pol_id = f"POL-2026-{pol_counter:06d}"
        is_anomaly = q["quote_id"] in [x["quote_id"] for x in injected_unauth]

        q_created = datetime.fromisoformat(q["created_at"])
        eff_date = (q_created + timedelta(days=random.randint(2, 10))).date()
        exp_date = eff_date + timedelta(days=365)
        prem = Decimal(q["calculated_premium"])

        if not is_anomaly and pol_counter <= inj_prem_tamper_count:
            prem = (prem * Decimal("0.5")).quantize(Decimal("0.01"))
            ground_truth.append({
                "record_id": pol_id,
                "entity": "Policy",
                "issue_type": "PREMIUM_FORMULA_MISMATCH",
                "description": f"Calculated premium {q['calculated_premium']} tampered to {prem}"
            })

        if is_anomaly:
            ground_truth.append({
                "record_id": pol_id,
                "entity": "Policy",
                "issue_type": "ISSUED_WITHOUT_APPROVAL",
                "description": f"Policy bound against quote status {q['status']}"
            })

        status = "CANCELLED" if (10 < pol_counter <= (
            20 if scale == "starter" else 110)) else "IN_FORCE"
        policies.append({
            "policy_id": pol_id,
            "quote_id": q["quote_id"],
            "applicant_id": q["applicant_id"],
            "asset_id": q["asset_id"],
            "product_id": q["product_id"],
            "effective_date": eff_date.isoformat(),
            "expiration_date": exp_date.isoformat(),
            "total_premium": f"{prem:.2f}",
            "payment_reference": f"TXN-PAY-{pol_counter:08d}",
            "policy_status": status
        })
        pol_counter += 1

    # 5. Endorsements
    end_counter = 1
    inj_end_limit = 10 if scale == "full" else 1
    for pol in policies[:num_endorsements]:
        pid = pol["policy_id"]
        end_id = f"END-{pid}-{end_counter:03d}"
        end_counter += 1
        p_eff = datetime.fromisoformat(pol["effective_date"]).date()
        end_eff = p_eff + timedelta(days=random.randint(30, 200))
        prod = prod_lookup[pol["product_id"]]
        delta_sum = Decimal("2000000.00")

        if end_counter <= (inj_end_limit + 1):
            delta_sum = Decimal("60000000.00")
            ground_truth.append({
                "record_id": end_id,
                "entity": "Endorsement",
                "issue_type": "ENDORSEMENT_EXCEEDS_CAPACITY",
                "description": f"Endorsement delta {delta_sum} exceeds limit {prod['max_sum_insured']}"
            })

        pro_rata_prem = (
            delta_sum * prod["base_rate"] * Decimal("0.5")).quantize(Decimal("0.01"))
        endorsements.append({
            "endorsement_id": end_id,
            "policy_id": pid,
            "endorsement_type": "SUM_INSURED_MODIFICATION",
            "delta_sum_insured": f"{delta_sum:.2f}",
            "pro_rata_premium_adjustment": f"{pro_rata_prem:.2f}",
            "effective_date": end_eff.isoformat(),
            "approved_by": "EMP_UW_12"
        })

    # 6. Renewals
    cancelled_pols = [p for p in policies if p["policy_status"] == "CANCELLED"]
    in_force_pols = [p for p in policies if p["policy_status"] == "IN_FORCE"]

    inj_cancel_renew = 15 if scale == "full" else 2
    inj_overlap_limit = 8 if scale == "full" else 1

    renewal_candidates = in_force_pols[:(
        num_renewals - inj_cancel_renew)] + cancelled_pols[:inj_cancel_renew]
    overlapping_count = 0

    for pol in renewal_candidates:
        pid = pol["policy_id"]
        ren_id = f"REN-{pid}-2027"
        is_cancelled = (pol["policy_status"] == "CANCELLED")
        p_exp = datetime.fromisoformat(pol["expiration_date"]).date()
        offer_expiry = p_exp - timedelta(days=15)
        ren_premium = (Decimal(pol["total_premium"])
                       * Decimal("1.08")).quantize(Decimal("0.01"))

        if is_cancelled:
            ground_truth.append({
                "record_id": ren_id,
                "entity": "Renewal",
                "issue_type": "RENEWAL_GENERATED_ON_CANCELLED_POLICY",
                "description": f"Renewal offer constructed on terminated policy status {pol['policy_status']}"
            })
            r_status = "DECLINED"
        else:
            r_status = random.choices(
                ["BOUND", "OFFERED", "DECLINED"], weights=[0.70, 0.20, 0.10])[0]

        new_pid = ""
        if r_status == "BOUND":
            bound_counter = len(policies) + 1
            new_pid = f"POL-2026-{bound_counter:06d}"

            if overlapping_count < inj_overlap_limit:
                overlapping_count += 1
                new_eff = p_exp - timedelta(days=30)
                ground_truth.append({
                    "record_id": new_pid,
                    "entity": "Policy",
                    "issue_type": "OVERLAPPING_POLICY_PERIOD",
                    "description": f"Policy {new_pid} effective date {new_eff} overlaps prior policy {pid} expiration {p_exp}"
                })
            else:
                new_eff = p_exp

            policies.append({
                "policy_id": new_pid,
                "quote_id": pol["quote_id"],
                "applicant_id": pol["applicant_id"],
                "asset_id": pol["asset_id"],
                "product_id": pol["product_id"],
                "effective_date": new_eff.isoformat(),
                "expiration_date": (new_eff + timedelta(days=365)).isoformat(),
                "total_premium": f"{ren_premium:.2f}",
                "payment_reference": f"TXN-REN-{bound_counter:08d}",
                "policy_status": "IN_FORCE"
            })

        renewals.append({
            "renewal_id": ren_id,
            "prior_policy_id": pid,
            "renewal_status": r_status,
            "renewal_premium": f"{ren_premium:.2f}",
            "offer_expiry_date": offer_expiry.isoformat(),
            "new_policy_id": new_pid
        })

    def export_csv(filename, fieldnames, data):
        filepath = os.path.join(output_dir, filename)
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    export_csv("applicants.csv", ["applicant_id", "entity_type", "credit_score",
               "loss_history_count_3yr", "annual_revenue", "jurisdiction", "created_at"], applicants)
    export_csv("insured_assets.csv", ["asset_id", "applicant_id", "asset_type",
               "declared_value", "construction_type_or_make", "asset_risk_score"], insured_assets)
    export_csv("products.csv", ["product_id", "product_name", "target_asset_type",
               "min_credit_score", "max_loss_count", "max_sum_insured", "base_rate"], PRODUCTS)
    export_csv("coverage_options.csv", [
               "coverage_id", "product_id", "coverage_name", "deductible", "coverage_limit"], COVERAGE_OPTIONS)
    export_csv("risk_factors.csv", [
               "risk_factor_id", "dimension", "bucket_min", "bucket_max", "multiplier"], RISK_FACTORS)
    export_csv("quotes.csv", ["quote_id", "applicant_id", "asset_id", "product_id",
               "sum_insured", "calculated_premium", "status", "created_at", "expires_at"], quotes)
    export_csv("underwriting_decisions.csv", [
               "decision_id", "quote_id", "authority_level", "decision", "reasons", "decided_by", "decided_at"], uw_decisions)
    export_csv("policies.csv", ["policy_id", "quote_id", "applicant_id", "asset_id", "product_id",
               "effective_date", "expiration_date", "total_premium", "payment_reference", "policy_status"], policies)
    export_csv("endorsements.csv", ["endorsement_id", "policy_id", "endorsement_type",
               "delta_sum_insured", "pro_rata_premium_adjustment", "effective_date", "approved_by"], endorsements)
    export_csv("renewals.csv", ["renewal_id", "prior_policy_id", "renewal_status",
               "renewal_premium", "offer_expiry_date", "new_policy_id"], renewals)
    export_csv("ground_truth.csv", [
               "record_id", "entity", "issue_type", "description"], ground_truth)

    print(f"[SUCCESS] Scale '{scale}' completed using Seed: {seed}.")
    print(f"Generated: {len(applicants)} applicants, {len(quotes)} quotes, {len(policies)} total policies, {len(renewals)} renewals.")
    print(f"Total Isolated Ground Truth Anomalies: {len(ground_truth)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synthetic Underwriting Dataset Generator")
    parser.add_argument("--scale", choices=["starter", "full"],
                        default="full", help="Scale of the dataset (starter vs full)")
    parser.add_argument("--seed", type=int, default=20261022,
                        help="Fixed random seed for deterministic generation")
    parser.add_argument("--output_dir", type=str,
                        default="./underwriting_data", help="Output directory path")
    args = parser.parse_args()

    generate_dataset(scale=args.scale, seed=args.seed,
                     output_dir=args.output_dir)
