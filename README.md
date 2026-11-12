YottaFlex AI — Intelligent Insurance Underwriting & Policy Management SystemAn end-to-end, deterministic insurance underwriting, actuarial pricing, policy lifecycle management, and anomaly detection platform.Built to demonstrate transparent business rule execution, relational data integrity, reproducible synthetic portfolio generation, and zero-leakage anomaly auditing across Motor (PRD-AUTO-01), Property (PRD-PROP-01), and Commercial/Cyber (PRD-CYBR-01) insurance lines.1. Key Capabilities10-Entity Relational Architecture: Normalized ANSI SQL schema (src/database/schema.sql) enforcing primary keys, foreign keys, and lifecycle state transitions across Applicant, InsuredAsset, Product, CoverageOption, RiskFactor, Quote, Policy, Endorsement, Renewal, and UnderwritingDecision.Deterministic Actuarial Pricing Engine: Fixed-point Decimal arithmetic ($0.00$ floating-point drift) computing premiums transparently from product rate tables and risk multipliers.3-Tier Underwriting Authority Matrix: Automated triage routing applications across STP_SYSTEM (straight-through auto-approval), UNDERWRITER_L1 (operations review), and SENIOR_VP (high-sum-insured escalations $> ₹2.5\text{ Cr}$).Strict Policy Binding & Lifecycle Gates: Enforces explicit customer acceptance and payment token verification (TXN-PAY-XXXXXXXX) before policy issuance, immutable mid-term endorsements, and validated annual renewals.Zero-Leakage Anomaly Benchmark: Deliberately injects and isolates $N = 58$ labeled operational, pricing, and lifecycle edge cases in data/ground_truth/ground_truth.csv, achieving 100% Precision, 100% Recall, and a 1.0000 F1-Score.Interactive Executive Cockpit: 11-module Streamlit & Plotly dashboard (src/analytics/app_streamlit.py) featuring portfolio KPIs, real-time premium simulation, anomaly diagnostics, data quality reports, and one-click CSV/JSON exports.2. Project StructureIntelligent-Insurance-Underwriting-and-Policy-Management-System/
├── config/
│   └── business_rules.json          # Configurable rate tables, multipliers, and authority thresholds
├── data/
│   ├── generated/                   # Reproducible CSV & JSON tables (seed: 20261022)
│   └── ground_truth/
│       └── ground_truth.csv         # Isolated defect labels (N=58) for zero-leakage benchmarking
├── docs/
│   ├── architecture.md              # System architecture and design decisions
│   ├── assumptions.md               # Domain assumptions, trade-offs, and known limitations
│   ├── business_rules.md            # Actuarial formulas, eligibility rules, and routing matrix
│   ├── data_dictionary.md           # Field-level types, keys, enums, and constraints for all 10 entities
│   └── testing_report.md            # Validation suite and unit test verification summary
├── outputs/
│   ├── evaluation_metrics.json      # Precision, Recall, F1-score, and triage distribution metrics
│   └── source_manifest.json         # SHA-256 provenance checksums for deterministic reproducibility
├── prompts/
│   └── prompt_history.md            # Transparent AI usage log and human-reviewed interventions
├── sql/
│   └── seed_data.sql                # Reproducible SQL insert statements for SQLite/RDBMS
├── src/
│   ├── analytics/
│   │   ├── app_streamlit.py         # 11-module Streamlit & Plotly executive dashboard
│   │   └── detect_anomalies.py      # Rule-based anomaly detection and ground-truth evaluator
│   ├── database/
│   │   └── schema.sql               # ANSI SQL DDL with PK, FK, and check constraints
│   ├── engines/
│   │   └── evaluator.py             # Actuarial rating, underwriting triage, and policy binding engine
│   ├── generators/
│   │   └── generate_data.py         # Parameterized synthetic portfolio & anomaly generator
│   └── validation/
│       └── validate_integrity.py    # 6-suite referential, chronological, and arithmetic auditor
├── tests/
│   ├── __init__.py
│   └── test_engines.py              # Unit tests for pricing, STP routing, declines, and binding gates
├── dashboard.py                     # Lightweight CLI executive summary dashboard
├── requirements.txt                 # Python dependencies
└── README.md
3. Quickstart: Installation & ExecutionPrerequisitesPython 3.11+pip package managerStep 1: Clone & Install Dependenciesgit clone https://github.com/Pnvsai888/Intelligent-Insurance-Underwriting-and-Policy-Management-System.git
cd Intelligent-Insurance-Underwriting-and-Policy-Management-System
pip install -r requirements.txt
Step 2: Generate Data & Build SQLite Database (Optional — Pre-generated artifacts included)# Generate full-scale portfolio (seed: 20261022)
python src/generators/generate_data.py --scale full --seed 20261022

# Build local SQLite database from schema and seed scripts
python -c "import sqlite3; conn = sqlite3.connect('data/insurance.db'); conn.executescript(open('src/database/schema.sql').read()); conn.executescript(open('sql/seed_data.sql').read()); conn.close(); print('SQLite DB built at data/insurance.db')"
Step 3: Run Integrity Audits, Anomaly Detection & Unit Tests# 1. Run 6-suite referential and arithmetic data integrity validation
python src/validation/validate_integrity.py

# 2. Run anomaly detection benchmark against ground truth
python src/analytics/detect_anomalies.py

# 3. Execute automated unit test suite
python -m unittest discover tests
Step 4: Launch the Interactive Dashboardstreamlit run src/analytics/app_streamlit.py
Open http://localhost:8501 in your browser to explore all 11 operational and analytical modules. (For a quick terminal summary instead, run python dashboard.py.)4. Core Business Logic & Actuarial FormulaReproducible Premium CalculationEvery quote is priced deterministically using Python Decimal arithmetic:$$P = \text{Sum Insured} \times \text{Base Rate} \times M_{\text{credit}} \times M_{\text{loss}} \times M_{\text{asset}}$$Base Rates: Property (0.0200), Motor (0.0350), Commercial/Cyber (0.0150).Multipliers: Credit tier ($0.850\text{--}1.250$, including a $1.250$ fallback penalty for missing risk data), 3-year claims history ($0.900\text{--}1.400$), and normalized asset hazard score ($0.800\text{--}1.300$).3-Tier Underwriting Authority MatrixAuthority LevelDecision OutcomeTrigger ConditionsSTP_SYSTEMAUTO_APPROVEClean eligibility, Sum Insured $\le ₹2.5\text{ Cr}$, Claims $\le 1$, Credit Score $\ge 680$, Asset Risk $\le 5.0$.UNDERWRITER_L1REFERMissing credit data penalty, borderline credit ($600\text{--}650$), or moderate loss history ($2$ claims).SENIOR_VPREFERHigh exposure ($> ₹2.5\text{ Cr}$ up to ₹5 Cr product ceiling) or high asset hazard score ($> 7.5$).Hard Decline RulesDECLINECredit score below product minimum, excessive claims ($\ge 3$), blacklisted applicant, or asset-product mismatch.5. Validation & Anomaly Benchmark ResultsThe system generates valid operational records first, then injects $N = 58$ labeled anomalies strictly isolated in data/ground_truth/ground_truth.csv:#Injected ScenarioExpected Detection RuleCount (N)PrecisionRecallF1-Score1Policy issued without acceptanceAcceptance & payment gate violation151.00001.00001.00002Premium outside formulaActuarial reconciliation failure101.00001.00001.00003Endorsement exceeds product limitMaximum coverage capacity violation101.00001.00001.00004Renewal generated for cancelled policyLifecycle state violation151.00001.00001.00005Overlapping policy periodsChronological term overlap violation81.00001.00001.0000—Total Audited BenchmarkAll 5 Exception Scenarios581.00001.00001.00006. Design Trade-offs, Limitations & AI TransparencyKey Design Decisions: Fixed-point Decimal math was selected over IEEE-754 floats to prevent penny-rounding drift across multi-factor endorsements. Separate history tables (Endorsement, Renewal) preserve immutable audit trails instead of mutating active policy rows.Known Limitations: Synthetic distributions model static annual terms (365 days) and single-currency (INR) rating without external credit bureau API calls or multi-currency FX conversion.Transparent AI Disclosure: Full prompt logs, areas accelerated by LLM scaffolding, and manual engineering interventions (such as fixing StopIteration edge-case lookups in validate_integrity.py and aligning Decimal type signatures in tests/test_engines.py) are documented in prompts/prompt_history.md.
