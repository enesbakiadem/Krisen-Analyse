from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
BI = PROCESSED / "bi"

BILLBOARD_PATH = RAW / "Billboard_Hot100_Songs_Spotify_1946-2022.csv"
MASTER_PATH = PROCESSED / "master.csv"

START_YEAR = 2000
END_YEAR = 2022

CRISIS_YEARS = {
    "Financial Crisis": [2008, 2009, 2010],
    "COVID": [2020, 2021],
}