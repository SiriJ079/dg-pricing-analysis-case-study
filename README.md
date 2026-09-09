# D&G Pricing Analysis Case Study

Pricing strategy analysis using Python: conversion, price elasticity, claims
and revenue performance, completed as part of the Domestic & General Pricing
Analyst case study assessment.

## Objective

Domestic & General is using data science to lead pricing strategy on its new
business book. This project analyses a sample of appliance protection plan
offers to determine whether the current pricing strategy (ASIS) should be
maintained or replaced with a customer-level optimised alternative (@22% or
@23%).

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
```

Open any notebook in VS Code and select the `venv` interpreter as the kernel.

## Data Cleaning

The raw dataset (`pricing_analyst_dataset.csv`) contains contact-centre
offer data with three pricing strategies: **ASIS FEE** (unadjusted
appliance-level pricing) and two customer-level optimised strategies,
**@22%** and **@23%**.

Cleaning steps applied in `01_dataset_cleaning.ipynb`:

1. **Standardised column names and types** — lowercased column headers,
   converted date fields (`offerdate`, `purchase_date`) to datetime, and
   numeric fields (premiums, price difference, claims, plan counts) to
   numeric dtypes.
2. **Removed exact duplicate rows.**
3. **Dropped rows missing essential fields** (`pricing_point`, `sale_flag`,
   `base_rate`, `offered_premium`, `price_diff`) required for strategy
   comparison, while preserving rows with missing claims data, since claims
   are only needed for one specific question later.
4. **Flagged (not removed) price inconsistencies** — added
   `invalid_price_flag` for non-positive prices, and `price_diff_matches` to
   check that `offered_premium - base_rate ≈ price_diff`. No rows triggered
   the invalid price flag in the final dataset.
5. Saved the cleaned dataset to `data/processed/pricing_analyst_cleaned.csv`.

**Result:** [8,865] rows retained from [8,867] original rows.

## Task A: Exploratory Data Analysis

Full analysis in `02_task_a_EDA.ipynb`. Key findings:

- Offer volumes and appliance/customer profiles (purchase price, item age,
  plan ownership) were broadly comparable across all three strategies,
  supporting a fair comparison between them.
- `price_diff` is exactly zero for every ASIS FEE row (expected, since ASIS
  applies no optimisation), while @22% and @23% show a bimodal spread of
  price increases and decreases.
- `predictedconversionrate` is a constant placeholder value of 1.0 for all
  ASIS FEE rows, indicating no real conversion model was applied under that
  strategy. This field is excluded from model-calibration comparisons
  involving ASIS.

**Key figures:** `outputs/figures/price_variation_by_strategy.png`,
`outputs/figures/correlation_matrix.png`

## Task B: Pricing Strategy Performance

Full analysis in `03_task_b_summary_table.ipynb`.

| Strategy | Offers | Avg base rate | Avg offered premium | Avg sold premium | Avg price increase | Conversion |
|---|---|---|---|---|---|---|
| ASIS FEE | 1,115 | £48.97 | £48.97 | £49.57 | £0.00 | 23.3% |
| @22% | 3,923 | £49.20 | £55.21 | £55.75 | £0.12 | 22.0% |
| @23% | 3,827 | £49.01 | £51.98 | £51.48 | £0.06 | 22.7% |

**Statistical testing:**

- **Conversion** (binary outcome): chi-square test of independence,
  chi2 = [value], **p = 0.61 (not significant)** — no strong evidence
  conversion rate differs by strategy.
- **Offered premium / price increase** (continuous): Welch's t-tests between
  each pair of strategies. All pairwise comparisons were **highly
  significant (p < 0.001)**.

## Task C: Price Elasticity

Full analysis in `04_task_c_price_elasticity.ipynb`.

**Between-group elasticity** (versus ASIS baseline), following the formula
provided:

| Strategy | Elasticity |
|---|---|
| @22% vs ASIS | -0.44 |
| @23% vs ASIS | -0.46 |

Both show the expected negative relationship: conversion falls as premium
rises relative to ASIS.

**Within-group elasticity** (low vs high price buckets within one
strategy):

| Strategy | Elasticity |
|---|---|
| @22% (low vs high price) | +0.66 |
| @23% (low vs high price) | +0.17 |

Both show a **positive** sign, the opposite direction to the between-group
result. Investigation traced part of this to a weak positive correlation
between `price_diff` and `predictedconversionrate` for @22% (r = +0.11),
suggesting the optimisation model assigns slightly higher prices to
customers it already predicts are more likely to convert, a selection
effect rather than a genuine causal price response. For @23%, no tested
variable (plan status, claims, item age, plan count) fully explained the
positive within-group result.

## Task D: Strategy Ranking and Model Bias

Full analysis in `05_task_d_pricing_comparison.ipynb`.

| Criterion | Best strategy |
|---|---|
| Statistical: premium difference vs ASIS | @22% |
| Statistical: conversion difference vs ASIS | Not significant (p = 0.61) |
| Revenue: avg realised uplift per sale | @22% (£6.42 vs £2.92) |
| Revenue: total realised uplift | @22% (£5,545 vs £2,535) |

**Model bias:** @22% and @23% showed small predicted-vs-actual conversion
calibration gaps (0.008 and 0.004 respectively), suggesting reasonable
calibration between the two. However, the elasticity findings above indicate
@22%'s pricing decisions are mildly linked to its own conversion
predictions, a form of selection bias worth further investigation before
scaling the strategy.

## Task E: Claims and Conversion Relationship

Full analysis in `06_task_e_consversion&claims.ipynb`.

- Chi-square test confirmed a highly significant relationship between claim
  history and conversion (chi2 = 324.81, **p < 0.0001**).
- Customers with a claim on record converted at **48.1%**, versus **20.0%**
  for those without, roughly 2.4x higher.
- This relationship held consistently across all three strategies
  (ASIS: 50.5% vs 20.4%; @22%: 48.4% vs 19.5%; @23%: 47.0% vs 20.3%).
- Claims correlate strongly with plan ownership (84.8% of claim holders
  already hold a plan), but the effect survives controlling for plan
  status: claims still roughly double conversion among non-plan customers
  (16.3% to 33.3%) and add a smaller boost among plan holders (43.9% to
  50.7%).

**Key figure:** `outputs/figures/conversion_by_claims.png`

## Task F: Final Recommendation

See `reports/executive_summary.pdf` for the full write-up. In brief:
**adopt @22%** as the primary pricing strategy, given its clear revenue
advantage and lack of statistically proven conversion cost, while
addressing the model-bias and data-quality caveats identified above before
scaling further.

## Limitations

- Conversion differences between strategies were not statistically
  significant overall; the recommendation relies more heavily on revenue
  evidence than proven conversion advantage.
- `predictedconversionrate` for ASIS FEE is a placeholder constant, not a
  genuine model output, limiting fair three-way model-bias comparison.
- Within-group elasticity for @23% remains only partially explained by the
  variables available in this dataset.
