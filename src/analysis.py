from pathlib import Path

import pandas as pd
from scipy.stats import pearsonr, spearmanr

# ── Paths ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = DATA_DIR / "results"

BILLBOARD_PATH = RAW_DIR / "Billboard_Hot100_Songs_Spotify_1946-2022.csv"
MASTER_PATH = PROCESSED_DIR / "master.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Parameters ───────────────────────────────────────────────
START_YEAR = 2000
END_YEAR = 2022

CRISIS_YEARS = {
    "Financial Crisis": [2008, 2009, 2010],
    "COVID": [2020, 2021],
}

# ── Load data ────────────────────────────────────────────────
billboard = pd.read_csv(BILLBOARD_PATH, encoding="latin-1")
billboard["year"] = billboard["Hot100 Ranking Year"]

master = pd.read_csv(MASTER_PATH)

# ── Data cleaning ────────────────────────────────────────────
billboard = billboard[
    ~billboard["Song"].str.contains("Karaoke", case=False, na=False)
]
billboard = billboard[
    ~billboard["Artist Names"].str.contains("Karaoke", case=False, na=False)
]

print(f"Songs after cleaning: {len(billboard)}")

billboard["Artist Names"] = (
    billboard["Artist Names"]
    .str.strip("[]")
    .str.replace("'", "", regex=False)
)

# ── Aggregate music features by year ────────────────────────
music = (
    billboard.groupby("year")[["Valence", "Energy", "Danceability"]]
    .mean()
    .reset_index()
)

usa = master.loc[master["Country Code"] == "USA", ["Jahr", "GDP", "Unemployment", "Inflation"]].copy()
usa = usa.rename(columns={"Jahr": "year"})

# ── Merge ────────────────────────────────────────────────────
combined_all = music.merge(usa, on="year", how="inner")
combined_all = combined_all.sort_values("year").reset_index(drop=True)

# ── Filter to main analysis window ───────────────────────────
combined = combined_all[combined_all["year"].between(START_YEAR, END_YEAR)].copy()

# ── Correlation matrix for export ───────────────────────────
correlation = combined[
    ["Valence", "Energy", "Danceability", "Unemployment"]
].corr()

target = correlation["Unemployment"].drop("Unemployment").reset_index()
target.columns = ["Feature", "Correlation"]

target.to_csv(
    RESULTS_DIR / "correlation_clean.csv",
    index=False,
    sep=";",
    decimal=","
)

# ── Helper function ──────────────────────────────────────────
def corr_with_ci(x, y):
    tmp = pd.concat([x, y], axis=1).dropna()

    pearson = pearsonr(tmp.iloc[:, 0], tmp.iloc[:, 1])
    ci = pearson.confidence_interval(0.95)
    spearman_rho, spearman_p = spearmanr(tmp.iloc[:, 0], tmp.iloc[:, 1])

    return {
        "n": len(tmp),
        "pearson_r": pearson.statistic,
        "pearson_p": pearson.pvalue,
        "ci_low": ci.low,
        "ci_high": ci.high,
        "spearman_rho": spearman_rho,
        "spearman_p": spearman_p,
    }

# ── Main result: Energy vs Unemployment ─────────────────────
main_res = corr_with_ci(combined["Unemployment"], combined["Energy"])
print(f"\nMain result (N={main_res['n']}, {START_YEAR}-{END_YEAR}):")
print(f"Pearson r  = {main_res['pearson_r']:.3f}, p={main_res['pearson_p']:.4f}")
print(f"95% CI: [{main_res['ci_low']:.3f}, {main_res['ci_high']:.3f}]")
print(f"Spearman ρ = {main_res['spearman_rho']:.3f}, p={main_res['spearman_p']:.4f}")

# ── Additional feature correlations ─────────────────────────
print("\nAll features:")
for feature in ["Energy", "Danceability", "Valence"]:
    res = corr_with_ci(combined["Unemployment"], combined[feature])
    print(f"{feature}: r={res['pearson_r']:.3f}, p={res['pearson_p']:.4f}")

# ── Energy vs macro indicators ──────────────────────────────
print("\nMacro indicators:")
for indicator in ["Unemployment", "GDP", "Inflation"]:
    res = corr_with_ci(combined[indicator], combined["Energy"])
    print(f"Energy ↔ {indicator}: r={res['pearson_r']:.3f}, p={res['pearson_p']:.4f}")

# ── Lag analysis ────────────────────────────────────────────
print("\nLag analysis:")
lag_rows = []

for lag in range(-2, 4):
    # Interpretation:
    # lag +1 = Unemployment(t) vs Energy(t+1)
    # lag -1 = Unemployment(t) vs Energy(t-1)
    shifted_energy = combined["Energy"].shift(-lag)

    res = corr_with_ci(combined["Unemployment"], shifted_energy)
    res["Lag"] = lag

    if lag > 0:
        res["Description"] = f"Unemployment(t) vs Energy(t+{lag}) — music follows"
    elif lag < 0:
        res["Description"] = f"Unemployment(t) vs Energy(t{lag}) — music leads"
    else:
        res["Description"] = "Unemployment(t) vs Energy(t) — same year"

    lag_rows.append(res)

lag_df = pd.DataFrame(lag_rows)

print(
    lag_df[
        ["Lag", "n", "pearson_r", "pearson_p", "spearman_rho", "spearman_p", "Description"]
    ].to_string(index=False)
)

# ── Robustness check ─────────────────────────────────────────
print("\nRobustness check:")
print(f"Pearson r  = {main_res['pearson_r']:.3f}, p={main_res['pearson_p']:.4f}")
print(f"Spearman ρ = {main_res['spearman_rho']:.3f}, p={main_res['spearman_p']:.4f}")
print(f"Consistent: {abs(main_res['pearson_r'] - main_res['spearman_rho']) < 0.1}")

# ── Sensitivity test ─────────────────────────────────────────
print("\nSensitivity test – time window robustness:")
for start, label in [(1991, "earliest available"), (1997, "25 years"), (2000, "main analysis")]:
    test = combined_all[combined_all["year"].between(start, END_YEAR)].copy()
    res = corr_with_ci(test["Unemployment"], test["Energy"])
    print(f"{start} ({label}): N={res['n']}, r={res['pearson_r']:.3f}, p={res['pearson_p']:.4f}")

# ── Song comparison lists ───────────────────────────────────
results = []

for crisis, years in CRISIS_YEARS.items():
    data = billboard[billboard["year"].isin(years)].copy()

    top_energy = (
        data.nlargest(20, "Energy")[["year", "Song", "Artist Names", "Energy"]]
        .drop_duplicates(subset=["Song", "Artist Names"])
        .head(10)
        .copy()
    )
    top_energy["Crisis"] = crisis
    top_energy["Type"] = "Energetic"

    top_mellow = (
        data.nsmallest(20, "Energy")[["year", "Song", "Artist Names", "Energy"]]
        .drop_duplicates(subset=["Song", "Artist Names"])
        .head(10)
        .copy()
    )
    top_mellow["Crisis"] = crisis
    top_mellow["Type"] = "Low Energy"

    results.append(top_energy)
    results.append(top_mellow)

# ── Save outputs ────────────────────────────────────────────
combined.to_csv(
    PROCESSED_DIR / "musik_wirtschaft_final.csv",
    index=False,
    decimal=",",
    sep=";",
)

correlation.to_csv(
    RESULTS_DIR / "korrelation.csv",
    decimal=",",
    sep=";",
)

lag_df.to_csv(
    RESULTS_DIR / "lag_analyse.csv",
    index=False,
    decimal=",",
    sep=";",
)

pd.concat(results).to_csv(
    RESULTS_DIR / "songs_vergleich.csv",
    index=False,
    decimal=",",
    sep=";",
)

print("\nAll files saved successfully.")