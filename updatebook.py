import pandas as pd
import math

# --- Prime factorization function ---
def prime_factors(n):
    factors = {}
    
    # handle 2 separately
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2
    
    # odd numbers
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i
    
    # remaining prime
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    
    return factors


# --- Format factors nicely ---
def format_factors(factors):
    parts = []
    for prime, power in factors.items():
        if power == 1:
            parts.append(f"{prime}")
        else:
            parts.append(f"{prime}^{power}")
    return " × ".join(parts)


# --- Convert decimal to integer (ignore ones place) ---
def extract_decimal_part(x):
    return int(round((x - int(x)) * 1000))


# --- Main function to apply ---
def add_prime_factorization(df, col="develle_mcharo_passing"):
    
    # Step 1: Whole number from decimal
    df["Whole_Number_Used"] = df[col].apply(extract_decimal_part)
    
    # Step 2: Factorization
    df["Prime_Factors_Dict"] = df["Whole_Number_Used"].apply(prime_factors)
    
    # Step 3: String format
    df["Prime_Factorization"] = df["Prime_Factors_Dict"].apply(format_factors)
    
    # Optional: drop dict column
    df = df.drop(columns=["Prime_Factors_Dict"])
    
    return df


# --- Example usage ---
df = pd.read_excel("SerieABook.xlsx")
df = add_prime_factorization(df)

df.to_excel("SerieABook.xlsx", index=False)
print(df.head())