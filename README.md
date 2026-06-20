# Pairs Trade v1.0

This is my first attempt at a pairs trading implementation built around a simple mean reversion strategy, using **Coke (KO)** and **Pepsi (PEP)** as the test pair. My main process sets out to answer whether a volatility-of-volatility approach outperform the standard Bollinger Band method?

---

## Overview

This project compares two mean reversion strategies across 2024 and 2025 out-of-sample data:

- **Deviation Strategy**: signals trades using the standard deviation *of* the standard deviation (volatility of volatility)
- **Bollinger Band Strategy**: the traditional approach, signaling trades when the spread exceeds `mean ± (σ × k)`

---

## Project Structure

| File | Description |
|---|---|
| `pairstrade.py` | Core project file. Contains some deprecated code left in from before data was saved locally (no need to hit the API every run) |
| `oos_pairstrade_202X.py` | Out-of-sample test scripts for 2024 and 2025 |
| `*.csv` | Datasets labeled by year |
| `SAVE*.py` | Scripts used to save data locally (kept for documentation clarity) |
| `202X OOS graph.png` | These are the graphs that I use to visualize the total PnL for each OOS test.

---
## Setup & Bloomberg API

Getting the Bloomberg API running was a project in itself. BBG's documentation is notoriously sparse, and the initial setup requires a real time investment before you see any return (no pun intended).

Fortunately, there exists a BBG **Polars** dataframe library, which is broadly compatible with the Python ecosystem. Key nuances worth knowing:
- Data comes in a vertical format and needs to be pivoted to horizontal (wide) format for this use case
- Mutation functions are clearly named (`rolling_mean` does exactly what it says) which made the learning curve more manageable
---

## Strategy Functions

Two functions live in `pairstrade.py`:

**`run_strategy_deviation`**
Uses the deviation of the deviation to determine when to enter a trade. Requires an initial burn-in period to calculate the second-order deviation, which pushes the trading start date to approximately mid-year.

**`run_strategy_bollinger`**
Standard Bollinger Band implementation. Signals a trade when the spread relationship between KO and PEP exceeds a k-value multiple of the rolling standard deviation.

---

## Results

### 2024
Both strategies had a rough year. The KO/PEP relationship broke down in June 2024, and neither strategy recovered particularly well. Both ended the year around **+2–3% total PnL**.

### 2025
A completely different story. The deviation strategy finished at approximately **+12% total return**. The Bollinger approach failed to capture the relationship and returned roughly **-2% PnL**. Notably, the deviation strategy outperformed *despite* starting later in the year due to its burn-in requirement.

---

## Known Constraints

**Fixed start/end windows**: Both out-of-sample tests don't begin trading until approximately June of each respective year, cutting the opportunity set roughly in half. Despite this limitation, the deviation strategy still outperformed the Bollinger approach in 2025.

**No cointegration testing**: Ideally, trades should only be entered when the two stocks are actually moving together. Adding a cointegration check before entering positions would likely have protected both strategies from the significant drawdown in June 2024.

---

## Roadmap — PairsTradeV2

The next iteration will aim to address both constraints above:
- Rolling or expanding window approach to eliminate the hard start-date limitation (I'm not exactly sure how to integrate this).
- Pre-trade cointegration testing to filter out periods where the pair relationship has broken down

---

## Notes

This is a first pass. The goal was to validate whether a second-order volatility signal could add value over a baseline Bollinger approach, and in 2025 at least, the answer was yes.
