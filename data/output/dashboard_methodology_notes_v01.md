# Auditor Switch Event Study — Methodology Notes

## Research Objective

The project examines preliminary market reaction around auditor-switch events among Israeli public companies, with particular attention to transitions involving Big-4 and non-Big-4 auditors.

## Event Definition

The baseline event date is the auditor-switch date preserved in the event dataset. The project also preserves publication-date fields where available for later robustness checks.

## Event Window Definition

The event window is `t-5_to_t+5` using trading days. If the event calendar date is not a trading day, the event trading date is the nearest available trading day on or after the event date.

## Benchmark Definition

TA-125 is used as the broad market benchmark for market-adjusted return calculations.

## Return Formulas

stock_return = stock_price_t_plus_5 / stock_price_t_minus_5 - 1

ta125_return = ta125_price_t_plus_5 / ta125_price_t_minus_5 - 1

## Market-Adjusted Return Formula

market_adjusted_return = stock_return - ta125_return

## Inclusion Criteria

Rows are included in return calculations only when stock and TA-125 event-window prices are available, positive, and associated with OK price-status flags.

## Exclusion Reasons

Rows may be excluded due to missing tickers, ticker validation failures, future event dates, missing stock prices, missing market prices, non-positive prices, or insufficient trading days before or after the event.

## Outlier and Robustness Treatment

Extreme returns are retained in the main results. The dashboard also reports sensitivity metrics excluding events with absolute market-adjusted return above 20%.

These robustness metrics are descriptive and do not replace formal econometric testing. Extreme observations may reflect genuine market reactions, ticker issues, corporate actions, low liquidity, or event-date problems.

## Limitations

The dashboard provides preliminary descriptive evidence. The results should not be interpreted as causal evidence. Additional controls and robustness checks are required for formal inference.

Important limitations include possible mapping uncertainty, missing or unavailable market data, firm-specific confounders, sector effects, liquidity differences, concurrent corporate news, earnings announcements, and market microstructure effects.

## Interpretation Guidance for the Dashboard

Market-adjusted returns should be read as descriptive event-window reactions relative to TA-125. They do not prove that the auditor switch caused the observed price movement. Dashboard users should review exclusion counts, ticker validation status, event eligibility, and outlier flags before interpreting the results.
