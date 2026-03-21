import pandas as pd
import math


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
        parts.append(f"{prime}" if power == 1 else f"{prime}^{power}")
    return " × ".join(parts)


def extract_decimal_part(x: float):
    if pd.isna(x):
        return pd.NA
    return int(round((float(x) - int(float(x))) * 1000))


def to_binary(series: pd.Series) -> pd.Series:
    mapping = {
        "true": 1, "false": 0,
        "yes": 1, "no": 0,
        "y": 1, "n": 0,
        "1": 1, "0": 0
    }

    def convert(x):
        if pd.isna(x):
            return 0
        if isinstance(x, bool):
            return int(x)
        s = str(x).strip().lower()
        if s in mapping:
            return mapping[s]
        try:
            return int(float(s))
        except ValueError:
            return 0

    return series.apply(convert).astype(float)


def compute_develle_mcharo_passing(row: pd.Series) -> float:
    v = row["mentality_vision"] / 100.0
    cr = row["attacking_crossing"] / 100.0
    fk = row["skill_fk_accuracy"] / 100.0
    sp = row["attacking_short_passing"] / 100.0
    lp = row["skill_long_passing"] / 100.0
    cv = row["skill_curve"] / 100.0

    s_star = 0.75 * sp + 0.25 * cr
    l_star = 0.625 * lp + 0.1875 * fk + 0.1875 * cr
    capacity = v + 0.809 * cv + s_star + l_star
    penalty = (1 - (s_star - l_star) ** 2) * (1 - v) ** 2

    ep = capacity - penalty
    return round(ep, 9)


def compute_mcharo_develle_ln_price(row: pd.Series, passing_col: str) -> float:
    return round(
        1.585332
        + 0.008219 * row["power_jumping"]
        + 0.047559 * row["pace"]
        + 0.012348 * row["attacking_heading_accuracy"]
        + 0.362187 * row[passing_col]
        + 0.015238 * row["dribbling"]
        + 0.189748 * row["weak_foot"]
        + 0.033917 * row["power_strength"]
        + 0.260190 * row["skill_moves"]
        + 0.808787 * row["Defender"]
        + 0.472467 * row["Midfielder"]
        + 0.081427 * row["Finesse_Shot"],
        9
    )


def add_develle_prime_and_ln_price(
    df: pd.DataFrame,
    passing_col: str = "develle_mcharo_passing",
    ln_price_col: str = "mcharo_develle_ln_price",
) -> pd.DataFrame:

    df = df.copy()
    df.columns = df.columns.str.strip()

    numeric_cols = [
        "mentality_vision",
        "attacking_crossing",
        "skill_fk_accuracy",
        "attacking_short_passing",
        "skill_long_passing",
        "skill_curve",
        "power_jumping",
        "pace",
        "attacking_heading_accuracy",
        "dribbling",
        "weak_foot",
        "power_strength",
        "skill_moves",
    ]

    required_cols = numeric_cols + ["Defender", "Midfielder", "Finesse_Shot"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Defender"] = to_binary(df["Defender"])
    df["Midfielder"] = to_binary(df["Midfielder"])
    df["Finesse_Shot"] = to_binary(df["Finesse_Shot"])

    fill_cols = numeric_cols + ["Defender", "Midfielder", "Finesse_Shot"]
    df[fill_cols] = df[fill_cols].fillna(0)

    # Step 1: create passing column first
    df[passing_col] = df.apply(compute_develle_mcharo_passing, axis=1)

    # Check that it really exists
    if passing_col not in df.columns:
        raise KeyError(f"{passing_col} was not created")

    # Step 2: ln price using the exact passing_col name
    df[ln_price_col] = df.apply(
        lambda row: compute_mcharo_develle_ln_price(row, passing_col),
        axis=1
    )

    # Step 3: integer + prime factorization
    df["Whole_Number_Used"] = df[passing_col].apply(extract_decimal_part)
    df["Prime_Factorization"] = df["Whole_Number_Used"].apply(
        lambda x: format_factors(prime_factors(int(x))) if pd.notna(x) else ""
    )

    # Optional: predicted euro value
    df["mcharo_develle_price_eur"] = df[ln_price_col].apply(
        lambda x: round(math.exp(x), 2) if pd.notna(x) else pd.NA
    )

    return df


input_file = "Book2.xlsx"
output_file = "Book2_with_develle.xlsx"

df = pd.read_excel(input_file)
df = add_develle_prime_and_ln_price(df)

df.to_excel(input_file, index=False)
df.to_excel(output_file, index=False)

print(
    df[
        [
            "short_name",
            "long_name",
            "develle_mcharo_passing",
            "mcharo_develle_ln_price",
            "mcharo_develle_price_eur",
            "Whole_Number_Used",
            "Prime_Factorization",
        ]
    ].head(10)
)
