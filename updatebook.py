import pandas as pd
import math


# -----------------------------
# Prime factorization helpers
# -----------------------------
def prime_factors(n: int) -> dict:
    factors = {}

    if n < 2:
        return factors

    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def format_factors(factors: dict) -> str:
    if not factors:
        return ""
    parts = []
    for prime, power in factors.items():
        if power == 1:
            parts.append(f"{prime}")
        else:
            parts.append(f"{prime}^{power}")
    return " × ".join(parts)


def extract_decimal_part(x: float) -> int:
    """
    Ignore the ones place and convert the decimal portion to a whole number.
    Example:
        3.543 -> 543
        2.077 -> 77
        3.002 -> 2
    """
    if pd.isna(x):
        return pd.NA
    return int(round((float(x) - int(float(x))) * 1000))


# -----------------------------
# Develle-Mcharo Passing Index
# -----------------------------
def compute_develle_mcharo_passing(row: pd.Series) -> float:
    """
    Column mapping from your FIFA dataset:
      Vision          -> mentality_vision
      Crossing        -> attacking_crossing
      FK Accuracy     -> skill_fk_accuracy
      Short Passing   -> attacking_short_passing
      Long Passing    -> skill_long_passing
      Curve           -> skill_curve
    """
    try:
        v = row["mentality_vision"] / 100.0
        cr = row["attacking_crossing"] / 100.0
        fk = row["skill_fk_accuracy"] / 100.0
        sp = row["attacking_short_passing"] / 100.0
        lp = row["skill_long_passing"] / 100.0
        cv = row["skill_curve"] / 100.0

        # Short-circulation composite
        s_star = 0.75 * sp + 0.25 * cr

        # Long-delivery composite
        l_star = 0.625 * lp + 0.1875 * fk + 0.1875 * cr

        # Capacity
        capacity = v + 0.809 * cv + s_star + l_star

        # Penalty
        penalty = (1 - (s_star - l_star) ** 2) * (1 - v) ** 2

        ep = capacity - penalty
        return round(ep, 9)

    except Exception:
        return pd.NA


# -----------------------------
# Main transformation
# -----------------------------
def add_develle_and_prime_factorization(
    df: pd.DataFrame,
    output_col: str = "develle_mcharo_passing",
) -> pd.DataFrame:
    # 1) Compute Develle-Mcharo Passing
    df[output_col] = df.apply(compute_develle_mcharo_passing, axis=1)

    # 2) Decimal -> whole number used
    df["Whole_Number_Used"] = df[output_col].apply(extract_decimal_part)

    # 3) Prime factorization
    df["Prime_Factorization"] = df["Whole_Number_Used"].apply(
        lambda x: format_factors(prime_factors(int(x))) if pd.notna(x) else ""
    )

    return df


# -----------------------------
# Run
# -----------------------------
input_file = "Book2.xlsx"
output_file = "Book2_with_develle.xlsx"

df = pd.read_excel(input_file)

df = add_develle_and_prime_factorization(df)

df.to_excel(output_file, index=False)

print(
    df[
        [
            "short_name",
            "long_name",
            "mentality_vision",
            "attacking_crossing",
            "skill_fk_accuracy",
            "attacking_short_passing",
            "skill_long_passing",
            "skill_curve",
            "develle_mcharo_passing",
            "Whole_Number_Used",
            "Prime_Factorization",
        ]
    ].head(10)
)