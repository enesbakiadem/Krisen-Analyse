# Recession Pop: Music in Times of Economic Crisis

## Project Snapshot

- **Type:** exploratory data analysis  
- **Tools:** Python · pandas · SciPy · Power BI  
- **Data:** Billboard Hot 100 · Spotify audio features · World Bank macro indicators  
- **Focus:** music audio features · unemployment · economic crises  
- **Output:** correlation analysis, lag analysis, interactive Power BI dashboard

Do economic crises change the sound of popular music?

> A data analysis project combining music data with macroeconomic indicators to explore how culture reacts to economic pressure.

I first came across the idea of “Recession Pop”, the claim that music became more energetic during the financial crisis. 

This made me question whether the relationship between economic conditions and music actually holds in a measurable way, and led to this analysis.

## 📸 Key Visuals

### Energy vs Unemployment, including the COVID anomaly
![Energy vs Unemployment](./visuals/01_energy_vs_unemployment.png)

### Lag Analysis
![Lag Analysis](./visuals/03_lag_analysis.png)

## 🎯 Research Question

Do economic conditions in the United States influence musical characteristics, and if so, how?

## 🧠 Background

“Recession Pop” describes a wave of energetic, dance-oriented music that emerged during the late 2000s financial crisis.

This project explores whether this phenomenon can be observed statistically using Billboard Hot 100 data and Spotify audio features, and whether a similar pattern appeared during COVID-19.

## 📊 Data Sources

Detailed source documentation is available in:

`DATA_SOURCES.md`

Main datasets:

- Billboard Hot 100 + Spotify audio features
- World Bank macroeconomic indicators

### Audio Features

- **Valence** – how positive or happy a song sounds  
- **Energy** – intensity and activity level  
- **Danceability** – how suitable a song is for dancing  

> Spotify audio features are proprietary algorithmic estimates and should be interpreted cautiously.  
> A related validity reference is documented in `DATA_SOURCES.md`.

## ⚙️ Methodology

- Aggregation of Billboard data by year  
- Merging with US economic indicators  
- Pearson correlation analysis  
- Spearman correlation as a robustness check  
- Lag analysis (-2 to +3 years) to test delayed relationships  
- Statistical significance testing (p-values)  
- Data visualization using Power BI  

## 📈 Key Results

The analysis reveals a consistent pattern:

During economic downturns, music becomes more energetic while losing danceability.

At the same time, the data indicates that music does not lead economic changes, it follows them.

| Feature       | r     | p-value | Interpretation              |
|---------------|-------|---------|-----------------------------|
| Energy        | +0.57 | 0.0047  | Rises with unemployment     |
| Danceability  | -0.68 | 0.0004  | Falls with unemployment     |
| Valence       | +0.06 | 0.79    | No meaningful relationship  |

**Lag Analysis (Energy)**  
The strongest correlation appears one year after the economic shock *(r = 0.63, lag +1)*, suggesting that music reacts to economic conditions with a short delay rather than immediately.

**Robustness**  
To check whether this result is stable, I also used Spearman correlation.

The result remains similar (ρ = 0.53), which suggests that the relationship is not driven by outliers or strict linear assumptions.

### COVID-19

No clear “Recession Pop” effect was observed during COVID-19, suggesting that structural changes in music consumption may have altered the relationship.

Possible explanations:
- Increased digital media consumption  
- Social isolation reducing collective escapism  
- A shift toward more introspective or “negative escapism”, where listeners turn to slower or emotionally heavier music instead of energetic, dance-oriented tracks

## 🔬 Statistical Note

The sample consists of 23 yearly observations (2000–2022).  
Given the relatively small sample size, the analysis should be interpreted as exploratory rather than conclusive.

The starting point (year 2000) was chosen pragmatically to focus on recent developments and ensure consistent data availability.  
To assess whether this choice influenced the results, the analysis was repeated starting from 1991 (earliest available macroeconomic data).  
The overall pattern remains similar, suggesting that the findings are not driven by the selected time window.

To reduce the risk of confirmation bias, multiple features (Energy, Danceability, Valence) were analyzed.  
Since not all variables show the same relationship, the results are less likely to reflect a single predefined narrative.

Spotify audio features are based on proprietary algorithms and should be interpreted with caution.  
External research suggests that “Energy” correlates relatively well with perceived intensity, while “Danceability” appears less consistent.  
For this reason, the interpretation focuses primarily on Energy, while Danceability is treated more cautiously.

Pearson correlation is used as a measure of linear association, while Spearman correlation serves as a robustness check.  
The similarity between both measures suggests that the results are not driven by outliers or strict linear assumptions.

## ⚠️ Limitations

- Billboard reflects chart success, not actual listening behavior  
- Spotify audio features for older songs are retroactively calculated  
- Limited sample size (23 data points)  
- Correlation does not imply causation  

## 🧹 Data Cleaning

- 172 karaoke entries removed (incorrect audio features)  
- Artist name formatting standardized  

## 🛠️ Tools

- Python (Pandas, SciPy)  
- Power BI  

## 💡 Key Insight

Music does not exist in isolation.

The results suggest that economic pressure shapes music, but not immediately.

Instead, cultural responses seem to build up over time, reflecting shared experiences.

## 🤖 Use of AI (Transparency)

AI tools were used to support wording, structuring, and parts of the code.

The core analysis, interpretation, and all decisions were developed independently.