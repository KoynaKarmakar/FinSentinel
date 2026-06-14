import json
import os


DEMO_CASES = {
    "Structuring": {
        "account_id": "C1001",
        "amount_inr": 985000,
        "velocity_24h": 1,
        "account_age_days": 420,
        "is_cross_border": False,
        "description": "Amount just below ₹10L RBI reporting threshold — classic structuring signal",
        "expected_tier": "HIGH",
    },
    "Fan-out smurfing": {
        "account_id": "C1002",
        "amount_inr": 4500000,
        "velocity_24h": 7,
        "account_age_days": 12,
        "is_cross_border": False,
        "description": "One source to 7 destinations, new account, large amount — fan-out pattern",
        "expected_tier": "CRITICAL",
    },
    "Cross-border layering": {
        "account_id": "C1003",
        "amount_inr": 2200000,
        "velocity_24h": 3,
        "account_age_days": 8,
        "is_cross_border": True,
        "description": "Cross-border transfer from a new account with large amount — layering pattern",
        "expected_tier": "HIGH",
    },
    "Legitimate transfer": {
        "account_id": "C1004",
        "amount_inr": 1800000,
        "velocity_24h": 1,
        "account_age_days": 847,
        "is_cross_border": False,
        "description": "Established account, single domestic transaction — salary disbursement pattern",
        "expected_tier": "LOW",
    },
}


def write_demo_cases() -> None:
    os.makedirs("data/transactions", exist_ok=True)
    output_path = "data/transactions/demo_cases.json"
    with open(output_path, "w") as f:
        json.dump(DEMO_CASES, f, indent=2)
    print(f"Wrote {len(DEMO_CASES)} demo cases to {output_path}")


if __name__ == "__main__":
    write_demo_cases()
