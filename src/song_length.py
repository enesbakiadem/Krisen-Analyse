import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("recession_pop.db")

df = pd.read_sql("""
    SELECT "Hot100 Ranking Year" as year, 
           ROUND(AVG("Song Length(ms)") / 60000.0, 2) AS avg_minuten
    FROM billboard
    GROUP BY "Hot100 Ranking Year"
    ORDER BY year
""", conn)

plt.figure(figsize=(14, 6))
plt.plot(df["year"], df["avg_minuten"], color="steelblue", linewidth=2)
plt.title("Durchschnittliche Songlänge in den Billboard Hot 100 (1946–2022)")
plt.xlabel("Jahr")
plt.ylabel("Minuten")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("visuals/06_song_length.png")
plt.show()
print("Done!")