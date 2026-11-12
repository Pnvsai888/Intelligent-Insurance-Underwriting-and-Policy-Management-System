import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "generated")
GROUND_TRUTH_DIR = os.path.join(BASE_DIR, "data", "ground_truth")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SQL_DIR = os.path.join(BASE_DIR, "sql")

DEFAULT_SEED = 20261022
SCALE_FULL = {
    "applicants": 3000,
    "quotes": 4000,
    "base_policies": 2000,
    "endorsements": 600,
    "renewals": 1200
}
SCALE_STARTER = {
    "applicants": 300,
    "quotes": 400,
    "base_policies": 200,
    "endorsements": 60,
    "renewals": 120
}
