# System Architecture
- Master Data Management (Applicants, Assets, Products, Coverages, Risk Factors)
- Quoting & Transparent Rating Engine: P = SI * Base * M_credit * M_loss * M_asset
- Underwriting & Escalation Authority: STP_SYSTEM, UNDERWRITER_L1, SENIOR_VP
- Policy Lifecycle Gate: Quote Eligibility, Underwriting Approval, Customer Acceptance, Payment Token
- Anomaly & Ground Truth Engine: 5 distinct negative scenarios isolated in ground_truth.csv
