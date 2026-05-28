import pandas as pd
from scipy.stats import pearsonr, spearmanr

from config import (
    BILLBOARD_PATH,
    MASTER_PATH,
    PROCESSED,
    BI,
    START_YEAR,
    END_YEAR,
    CRISIS_YEARS,
)

PROCESSED.mkdir(parents=True, exist_ok=True)
BI.mkdir(parents=True, exist_ok=True)


def corr_with_ci(x: pd.Series, y: pd.Series) -> dict:
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


def load_and_prepare_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    billboard = pd.read_csv(BILLBOARD_PATH, encoding="latin-1")
    billboard["year"] = billboard["Hot100 Ranking Year"]

    billboard = billboard[
        ~billboard["Song"].str.contains("Karaoke", case=False, na=False)
    ]
    billboard = billboard[
        ~billboard["Artist Names"].str.contains("Karaoke", case=False, na=False)
    ]

    billboard["Artist Names"] = (
        billboard["Artist Names"]
        .str.strip("[]")
        .str.replace("'", "", regex=False)
    )

    print(f"Songs after cleaning: {len(billboard)}")

    music = (
        billboard.groupby("year")[["Valence", "Energy", "Danceability"]]
        .mean()
        .reset_index()
    )

    master = pd.read_csv(MASTER_PATH)

    usa = master.loc[
        master["Country Code"] == "USA",
        ["Jahr", "GDP", "Unemployment", "Inflation"],
    ].copy()

    usa = usa.rename(columns={"Jahr": "year"})

    combined_all = music.merge(usa, on="year", how="inner")
    combined_all = combined_all.sort_values("year").reset_index(drop=True)

    combined = combined_all[
        combined_all["year"].between(START_YEAR, END_YEAR)
    ].copy()

    return billboard, combined_all, combined


def export_correlation_outputs(combined: pd.DataFrame) -> pd.DataFrame:
    correlation = combined[
        ["Valence", "Energy", "Danceability", "Unemployment"]
    ].corr()

    target = correlation["Unemployment"].drop("Unemployment").reset_index()
    target.columns = ["Feature", "Correlation"]

    target.to_csv(
        BI / "correlation_clean.csv",
        index=False,
        sep=";",
        decimal=",",
    )

    correlation.to_csv(
        BI / "correlation_matrix.csv",
        decimal=",",
        sep=";",
    )

    return correlation


def print_main_results(combined: pd.DataFrame) -> dict:
    main_res = corr_with_ci(combined["Unemployment"], combined["Energy"])

    print(f"\nMain result (N={main_res['n']}, {START_YEAR}-{END_YEAR}):")
    print(f"Pearson r  = {main_res['pearson_r']:.3f}, p={main_res['pearson_p']:.4f}")
    print(f"95% CI: [{main_res['ci_low']:.3f}, {main_res['ci_high']:.3f}]")
    print(f"Spearman ρ = {main_res['spearman_rho']:.3f}, p={main_res['spearman_p']:.4f}")

    print("\nAll features:")
    for feature in ["Energy", "Danceability", "Valence"]:
        res = corr_with_ci(combined["Unemployment"], combined[feature])
        print(f"{feature}: r={res['pearson_r']:.3f}, p={res['pearson_p']:.4f}")

    print("\nMacro indicators:")
    for indicator in ["Unemployment", "GDP", "Inflation"]:
        res = corr_with_ci(combined[indicator], combined["Energy"])
        print(f"Energy ↔ {indicator}: r={res['pearson_r']:.3f}, p={res['pearson_p']:.4f}")

    return main_res


def run_lag_analysis(combined: pd.DataFrame) -> pd.DataFrame:
    print("\nLag analysis:")

    lag_rows = []

    for lag in range(-2, 4):
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
            [
                "Lag",
                "n",
                "pearson_r",
                "pearson_p",
                "spearman_rho",
                "spearman_p",
                "Description",
            ]
        ].to_string(index=False)
    )

    lag_df.to_csv(
        BI / "lag_analysis.csv",
        index=False,
        decimal=",",
        sep=";",
    )

    return lag_df


def print_robustness_checks(
    combined_all: pd.DataFrame,
    combined: pd.DataFrame,
    main_res: dict,
) -> None:
    print("\nRobustness check:")
    print(f"Pearson r  = {main_res['pearson_r']:.3f}, p={main_res['pearson_p']:.4f}")
    print(f"Spearman ρ = {main_res['spearman_rho']:.3f}, p={main_res['spearman_p']:.4f}")
    print(f"Consistent: {abs(main_res['pearson_r'] - main_res['spearman_rho']) < 0.1}")

    print("\nSensitivity test – time window robustness:")
    for start, label in [
        (1991, "earliest available"),
        (1997, "25 years"),
        (2000, "main analysis"),
    ]:
        test = combined_all[combined_all["year"].between(start, END_YEAR)].copy()
        res = corr_with_ci(test["Unemployment"], test["Energy"])
        print(f"{start} ({label}): N={res['n']}, r={res['pearson_r']:.3f}, p={res['pearson_p']:.4f}")


def export_crisis_song_comparison(billboard: pd.DataFrame) -> None:
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

    pd.concat(results).to_csv(
        BI / "songs_comparison.csv",
        index=False,
        decimal=",",
        sep=";",
    )


def export_analysis_dataset(combined: pd.DataFrame) -> None:
    combined.to_csv(
        BI / "music_economy_final.csv",
        index=False,
        decimal=",",
        sep=";",
    )


def main() -> None:
    billboard, combined_all, combined = load_and_prepare_data()

    export_analysis_dataset(combined)
    export_correlation_outputs(combined)

    main_res = print_main_results(combined)

    run_lag_analysis(combined)

    print_robustness_checks(combined_all, combined, main_res)

    export_crisis_song_comparison(billboard)

    print("\nAll files saved successfully.")


if __name__ == "__main__":
    main()