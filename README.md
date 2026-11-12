# Automated Underwriting & Renewal Lifecycle Engine

An end-to-end, deterministic policy lifecycle and underwriting evaluation system. This solution evaluates quote submissions and renewals against product eligibility guidelines, actuarial factor matrices, capacity ceilings, and multi-tier approval authority structures.

---

## 1. System Architecture & Entity Relationships

The relational data model consists of 10 primary entities plus an isolated anomaly supervision dataset:

- **Master / Reference Entities**:
  - `Product`: Underwriting limits, target asset classes, hurdle rates, and base pricing rates ($N = 3$).
  - `CoverageOption`: Deductible and sub-limit configurations ($N = 9$).
  - `RiskFactor`: Actuarial pricing multipliers across credit scores, claim history, and asset hazard scores ($N = 14$).
  - `Applicant`: Legal entities (Individual, SME, Enterprise) with loss histories and credit data ($N = 3,000$).
  - `InsuredAsset`: Assets mapped to applicants with declared values and risk ratings ($N = 3,606$).
- **Transaction & Event Entities**:
  - `Quote`: Actuarially rated submissions ($N = 4,000$).
  - `UnderwritingDecision`: Traceable approvals, multi-tier referrals (L1 Underwriter, Senior VP), and declines ($N = 4,000$).
  - `Policy`: Bound contracts with payment tokens and lifecycle state tracking ($N = 2,316$).
  - `Endorsement`: Mid-term sum insured modifications and pro-rata adjustments ($N = 600$).
  - `Renewal`: Expiring contract evaluations, adjusted rates, and subsequent binding ($N = 1,200$).
- **Supervision / Ground Truth**:
  - `ground_truth.csv`: Isolated audit table cataloging injected negative edge cases ($N = 58$).

---

## 2. Underwriting Authority & Actuarial Rating Logic

### Actuarial Pricing Formula
$$\text{Calculated Premium} = \text{Sum Insured} \times \text{Base Rate} \times M_{\text{credit}} \times M_{\text{loss}} \times M_{\text{asset}}$$

### Decision Matrix
- **Straight-Through Processing (STP) Auto-Approve**: Credit Score $\ge$ Product Minimum, Loss History $\le 1$, Sum Insured $\le$ ₹10,000,000, Asset Risk Score $\le 6.0$.
- **Underwriter Level 1 Referral**: Credit Score in $[550, \text{Product Min}]$, Loss History $= 2$, or Missing Credit Data.
- **Senior VP Referral**: Loss History $> 2$ or Sum Insured between ₹10,000,000 and ₹25,000,000.
- **Hard Decline**: Credit Score $< 500$ or Sum Insured exceeding product capacity limit.

---

## 3. Ground Truth Anomalies & Edge Cases ($N = 58$)

To train and benchmark anomaly detection models, five negative scenarios were deliberately injected into the dataset and strictly isolated in `ground_truth.csv` without leaking into feature rows:

1. **`ISSUED_WITHOUT_APPROVAL`** ($N = 15$): Policies bound against unapproved (referred or declined) quotes.
2. **`PREMIUM_FORMULA_MISMATCH`** ($N = 10$): Bound premium modified outside standard actuarial formula tables.
3. **`ENDORSEMENT_EXCEEDS_CAPACITY`** ($N = 10$): Mid-term endorsements exceeding product underwriting ceilings.
4. **`RENEWAL_GENERATED_ON_CANCELLED_POLICY`** ($N = 15$): Renewal offers generated for terminated/cancelled policies.
5. **`OVERLAPPING_POLICY_PERIOD`** ($N = 8$): Renewal effective date starts prior to prior policy expiration without justification.

---

## 4. Setup, Reproduction & Verification Commands

### Environment Setup
```bash
# Clone or open directory in terminal
cd underwriting_project
