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

    base = combined[["year", "Unemployment"]].copy()

    for lag in range(-2, 4):
        energy_shifted = combined[["year", "Energy"]].copy()

        # Lag +1 means:
        # Unemployment in year t is compared with Energy in year t+1
        energy_shifted["year"] = energy_shifted["year"] + lag

        temp = base.merge(
            energy_shifted,
            on="year",
            how="inner",
        )

        res = corr_with_ci(temp["Unemployment"], temp["Energy"])
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


def shorten_text(value: str, max_length: int = 45) -> str:
    value = str(value)

    if len(value) <= max_length:
        return value

    return value[: max_length - 3] + "..."


def export_crisis_song_comparison(billboard: pd.DataFrame) -> None:
    exclude_patterns = [
        "Acoustic",
        "Karaoke",
        "Originally Performed",
        "Instrumental",
        "Tribute",
        "Cover",
        "Future Hit Makers",
        "Made Famous by",
    ]

    clean = billboard.copy()
    clean["Energy"] = pd.to_numeric(clean["Energy"], errors="coerce")
    clean = clean.dropna(subset=["Energy", "Song", "Artist Names"])

    pattern = "|".join(exclude_patterns)

    clean = clean[
        ~clean["Song"].str.contains(pattern, case=False, na=False)
        & ~clean["Artist Names"].str.contains(pattern, case=False, na=False)
    ].copy()

    active_results = []
    mellow_results = []

    for crisis, years in CRISIS_YEARS.items():
        data = clean[clean["year"].isin(years)].copy()

        active = (
            data.sort_values("Energy", ascending=False)
            .drop_duplicates(subset=["Song", "Artist Names"])
            .head(10)[["year", "Song", "Artist Names", "Energy"]]
            .copy()
        )
        active["Crisis"] = crisis
        active["Type"] = "Active"

        mellow = (
            data.sort_values("Energy", ascending=True)
            .drop_duplicates(subset=["Song", "Artist Names"])
            .head(10)[["year", "Song", "Artist Names", "Energy"]]
            .copy()
        )
        mellow["Crisis"] = crisis
        mellow["Type"] = "Mellow"

        active_results.append(active)
        mellow_results.append(mellow)

    active_out = pd.concat(active_results).copy()
    mellow_out = pd.concat(mellow_results).copy()

    for df in [active_out, mellow_out]:
        df["Song_short"] = df["Song"].apply(shorten_text)
        df["Artist_short"] = df["Artist Names"].apply(shorten_text)
        df["Energy"] = df["Energy"].round(2)

    active_out.to_csv(
        BI / "active_songs.csv",
        index=False,
        decimal=",",
        sep=";",
        encoding="utf-8-sig",
    )

    mellow_out.to_csv(
        BI / "mellow_songs.csv",
        index=False,
        decimal=",",
        sep=";",
        encoding="utf-8-sig",
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