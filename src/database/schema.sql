CREATE TABLE products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_name VARCHAR(128) NOT NULL,
    target_asset_type VARCHAR(64) NOT NULL,
    min_credit_score INT NOT NULL,
    max_loss_count INT NOT NULL,
    max_sum_insured NUMERIC(14,2) NOT NULL,
    base_rate NUMERIC(6,4) NOT NULL
);

CREATE TABLE applicants (
    applicant_id VARCHAR(32) PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL,
    credit_score INT,
    loss_history_count_3yr INT NOT NULL,
    annual_revenue NUMERIC(14,2),
    jurisdiction VARCHAR(8) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE insured_assets (
    asset_id VARCHAR(32) PRIMARY KEY,
    applicant_id VARCHAR(32) REFERENCES applicants(applicant_id),
    asset_type VARCHAR(64) NOT NULL,
    declared_value NUMERIC(14,2) NOT NULL,
    construction_type_or_make VARCHAR(64) NOT NULL,
    asset_risk_score NUMERIC(4,2) NOT NULL
);

CREATE TABLE quotes (
    quote_id VARCHAR(32) PRIMARY KEY,
    applicant_id VARCHAR(32) REFERENCES applicants(applicant_id),
    asset_id VARCHAR(32) REFERENCES insured_assets(asset_id),
    product_id VARCHAR(32) REFERENCES products(product_id),
    sum_insured NUMERIC(14,2) NOT NULL,
    calculated_premium NUMERIC(12,2) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE underwriting_decisions (
    decision_id VARCHAR(32) PRIMARY KEY,
    quote_id VARCHAR(32) REFERENCES quotes(quote_id),
    authority_level VARCHAR(32) NOT NULL,
    decision VARCHAR(32) NOT NULL,
    reasons TEXT NOT NULL,
    decided_by VARCHAR(64) NOT NULL,
    decided_at TIMESTAMP NOT NULL
);

CREATE TABLE policies (
    policy_id VARCHAR(32) PRIMARY KEY,
    quote_id VARCHAR(32) REFERENCES quotes(quote_id),
    applicant_id VARCHAR(32) REFERENCES applicants(applicant_id),
    asset_id VARCHAR(32) REFERENCES insured_assets(asset_id),
    product_id VARCHAR(32) REFERENCES products(product_id),
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL,
    total_premium NUMERIC(12,2) NOT NULL,
    payment_reference VARCHAR(64) NOT NULL,
    policy_status VARCHAR(32) NOT NULL
);

CREATE TABLE endorsements (
    endorsement_id VARCHAR(64) PRIMARY KEY,
    policy_id VARCHAR(32) REFERENCES policies(policy_id),
    endorsement_type VARCHAR(64) NOT NULL,
    delta_sum_insured NUMERIC(14,2) NOT NULL,
    pro_rata_premium_adjustment NUMERIC(12,2) NOT NULL,
    effective_date DATE NOT NULL,
    approved_by VARCHAR(64) NOT NULL
);

CREATE TABLE renewals (
    renewal_id VARCHAR(64) PRIMARY KEY,
    prior_policy_id VARCHAR(32) REFERENCES policies(policy_id),
    renewal_status VARCHAR(32) NOT NULL,
    renewal_premium NUMERIC(12,2) NOT NULL,
    offer_expiry_date DATE NOT NULL,
    new_policy_id VARCHAR(32)
);