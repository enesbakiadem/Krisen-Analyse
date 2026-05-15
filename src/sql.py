import pandas as pd
import sqlite3

df = pd.read_csv("data/raw/Billboard_Hot100_Songs_Spotify_1946-2022.csv")
conn = sqlite3.connect("recession_pop.db")
df.to_sql("billboard", conn, if_exists="replace", index=False)
conn.close()
print(f"Done! {len(df)} Songs geladen.")