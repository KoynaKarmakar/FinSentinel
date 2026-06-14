import json
import os
import random


def generate_synthetic_transactions(n_fraud: int = 50, n_normal: int = 450) -> list:
    random.seed(42)
    transactions = []

    for i in range(n_fraud):
        transactions.append(
            {
                "account_id": f"FRAUD{i:04d}",
                "amount_inr": random.uniform(900000, 5000000),
                "velocity_24h": random.randint(4, 12),
                "account_age_days": random.randint(1, 29),
                "is_cross_border": random.random() < 0.7,
                "is_fraud": True,
            }
        )

    for i in range(n_normal):
        transactions.append(
            {
                "account_id": f"LEGIT{i:04d}",
                "amount_inr": random.uniform(10000, 2000000),
                "velocity_24h": random.randint(1, 4),
                "account_age_days": random.randint(180, 1000),
                "is_cross_border": False,
                "is_fraud": False,
            }
        )

    return transactions


def write_synthetic_data() -> None:
    os.makedirs("data/transactions", exist_ok=True)
    transactions = generate_synthetic_transactions()
    output_path = "data/transactions/synthetic_transactions.json"
    with open(output_path, "w") as f:
        json.dump(transactions, f, indent=2)
    print(f"Generated {len(transactions)} synthetic transactions → {output_path}")


if __name__ == "__main__":
    write_synthetic_data()
