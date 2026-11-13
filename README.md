# NVIDIA CEO price forecaster

`main.py` (Python 3.13, standard library only, deterministic) forecasts the minute-by-minute Yes prices of the
24 markets of Polymarket's "Next CEO of NVIDIA?" event, 240 minutes ahead, as five quantiles (5/25/50/75/95%).
It uses recency-weighted empirical distributions of h-minute price changes per market, blended with a pooled,
volatility-normalised distribution, then clamps to [0, 1]. MIT licensed.
