import pandas as pd

from config import RAW, PROCESSED

PROCESSED.mkdir(parents=True, exist_ok=True)

G20_COUNTRIES = [
    "ARG", "AUS", "BRA", "CAN", "CHN", "DEU", "FRA", "GBR",
    "IDN", "IND", "ITA", "JPN", "KOR", "MEX", "RUS", "SAU",
    "ZAF", "TUR", "USA",
]


def clean_worldbank(filename: str, value_name: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / filename)

    year_columns = [
        col for col in df.columns
        if col.startswith(("196", "197", "198", "199", "200", "201", "202"))
    ]

    df = df[df["Country Code"].isin(G20_COUNTRIES)]
    df = df[["Country Name", "Country Code", *year_columns]]

    df = df.melt(
        id_vars=["Country Name", "Country Code"],
        var_name="year",
        value_name=value_name,
    )

    df["year"] = df["year"].str[:4].astype(int)
    df[value_name] = pd.to_numeric(df[value_name], errors="coerce")

    return df


def main() -> None:
    gdp = clean_worldbank("GDP.csv", "GDP")
    gdp_pc = clean_worldbank("GDP per capita.csv", "GDP_per_Capita")
    inflation = clean_worldbank("Inflation.csv", "Inflation")
    population = clean_worldbank("Population.csv", "Population")
    unemployment = clean_worldbank("Unemployment.csv", "Unemployment")

    master = gdp.merge(gdp_pc, on=["Country Name", "Country Code", "year"])
    master = master.merge(inflation, on=["Country Name", "Country Code", "year"])
    master = master.merge(population, on=["Country Name", "Country Code", "year"])
    master = master.merge(unemployment, on=["Country Name", "Country Code", "year"])

    master = master.rename(columns={"year": "Jahr"})

    out_path = PROCESSED / "master.csv"
    master.to_csv(out_path, index=False)

    print(f"master.csv saved: {master.shape[0]} rows, {master.shape[1]} columns")


if __name__ == "__main__":
    main()