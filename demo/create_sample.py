"""
ModelAuditAI — Demo Asset Generator
Creates a sample sklearn classifier and dataset for testing.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os


def create_sample_data():
    """Create a synthetic dataset with bias-prone features."""
    np.random.seed(42)
    n_samples = 1000

    data = {
        "age": np.random.randint(18, 70, n_samples),
        "gender": np.random.choice(["male", "female"], n_samples, p=[0.6, 0.4]),
        "income": np.random.normal(50000, 15000, n_samples).astype(int),
        "education_years": np.random.randint(8, 22, n_samples),
        "experience_years": np.random.randint(0, 40, n_samples),
        "region": np.random.choice(["north", "south", "east", "west"], n_samples),
        "credit_score": np.random.randint(300, 850, n_samples),
        "debt_ratio": np.random.uniform(0, 1, n_samples).round(3),
        "num_accounts": np.random.randint(1, 15, n_samples),
        "previous_defaults": np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
    }

    df = pd.DataFrame(data)

    # Create target with some bias
    score = (
        0.3 * (df["income"] / 50000) +
        0.2 * (df["credit_score"] / 850) +
        0.15 * (df["education_years"] / 22) +
        0.1 * (1 - df["debt_ratio"]) +
        0.1 * (df["experience_years"] / 40) -
        0.3 * df["previous_defaults"] +
        np.random.normal(0, 0.1, n_samples)
    )

    # Add slight gender bias (for demo purposes)
    score[df["gender"] == "female"] -= 0.05

    df["approved"] = (score > 0.45).astype(int)

    return df


def create_sample_model(df: pd.DataFrame):
    """Train a RandomForest classifier on the dataset."""
    # Encode categorical
    df_encoded = pd.get_dummies(df, columns=["gender", "region"], drop_first=True)

    X = df_encoded.drop(columns=["approved"])
    y = df_encoded["approved"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    print(f"Train accuracy: {train_acc:.4f}")
    print(f"Test accuracy:  {test_acc:.4f}")

    return model, df_encoded


if __name__ == "__main__":
    output_dir = os.path.dirname(__file__)

    print("Creating sample dataset...")
    df = create_sample_data()
    csv_path = os.path.join(output_dir, "sample_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path} ({len(df)} rows)")

    print("\nTraining sample model...")
    # For the model, we need the encoded dataset
    df_encoded = pd.get_dummies(df, columns=["gender", "region"], drop_first=True)
    X = df_encoded.drop(columns=["approved"])
    y = df_encoded["approved"]

    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X, y)

    model_path = os.path.join(output_dir, "sample_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    # Also save the encoded dataset (this is what the model expects)
    encoded_csv_path = os.path.join(output_dir, "sample_dataset_encoded.csv")
    df_encoded.to_csv(encoded_csv_path, index=False)
    print(f"Encoded dataset saved to {encoded_csv_path}")

    print("\nDone! Use these files to test the audit system.")
