# Data Sources

| File                                         | Source                                      | URL                                                                            | License                  | Accessed |
| -------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------ | -------- |
| Billboard_Hot100_Songs_Spotify_1946-2022.csv | Kaggle / Billboard + Spotify Audio Features | https://www.kaggle.com/datasets/thedevastator/billboard-hot-100-audio-features | Dataset license (Kaggle) | 2026     |
| GDP.csv                                      | World Bank WDI                              | https://data.worldbank.org/indicator/NY.GDP.MKTP.CD                            | CC BY 4.0                | 2026     |
| GDP per capita.csv                           | World Bank WDI                              | https://data.worldbank.org/indicator/NY.GDP.PCAP.CD                            | CC BY 4.0                | 2026     |
| Inflation.csv                                | World Bank WDI                              | https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG                            | CC BY 4.0                | 2026     |
| Population.csv                               | World Bank WDI                              | https://data.worldbank.org/indicator/SP.POP.TOTL                               | CC BY 4.0                | 2026     |
| Unemployment.csv                             | World Bank WDI / ILO                        | https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS                            | CC BY 4.0                | 2026     |

## Notes

* The analysis focuses on the United States, although the macroeconomic preparation pipeline includes G20 countries.
* Spotify audio features (Energy, Danceability, Valence) are proprietary algorithmic estimates and should be interpreted cautiously.
* Older songs receive retroactively calculated Spotify audio features.
* Karaoke entries were removed during data cleaning.

### Audio Feature Validity Reference

Vidas et al. (2025)
*Validating Spotify's "Valence", "Energy" and "Danceability" Audio Features for Music Psychology Research*

https://www.researchgate.net/publication/395985412_Validating_Spotify's_'Valence'_'Energy'_and_'Danceability'_Audio_Features_for_Music_Psychology_Research
