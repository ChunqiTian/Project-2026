# E-commerce Landing Page A/B Test

## Project Overview

This project analyzes an A/B test for an e-commerce landing page. The goal is to decide whether the company should ship the new landing page or keep the old page.

The analysis uses conversion data from a control group and a treatment group, then applies statistical testing, confidence intervals, bootstrap resampling, timing analysis, and visualization.

## Business Question

Should the company ship the new landing page?

## Dataset

The dataset is loaded directly from an online CSV URL:

```python
DATA_URL = "https://raw.githubusercontent.com/beery4010/Analyze-AB-Test-Results/master/ab_data.csv"
df = pd.read_csv(DATA_URL)
```

No local CSV download is required.

## Dataset Columns

| Column | Description |
| --- | --- |
| `user_id` | Unique user identifier |
| `timestamp` | Time when the user visited the page |
| `group` | Experiment group: `control` or `treatment` |
| `landing_page` | Page shown: `old_page` or `new_page` |
| `converted` | Binary conversion outcome: `1` converted, `0` did not convert |

## Analysis Steps

1. Load data directly from the online URL
2. Inspect dataset shape, columns, and data types
3. Check missing values and duplicate users
4. Validate experiment setup
5. Remove mismatched group/page rows
6. Remove duplicate users
7. Create timing features from timestamp
8. Compare sample sizes
9. Calculate conversion rates
10. Calculate absolute and relative lift
11. Run sample ratio check
12. Run two-proportion z-test
13. Run chi-square test of independence
14. Build a 95% confidence interval
15. Build a bootstrap confidence interval
16. Analyze conversion rate by day and hour
17. Run optional logistic regression adjustment
18. Create visualizations
19. Write a final business recommendation

## Statistical Methods

| Task | Method |
| --- | --- |
| Compare conversion rates | Two-proportion z-test |
| Check group/conversion relationship | Chi-square test |
| Estimate campaign impact | Absolute and relative lift |
| Build confidence interval | CI for difference in proportions |
| Use resampling | Bootstrap CI |
| Check sample split | Sample ratio check |
| Check best timing | Group by visit day/hour |
| Optional advanced method | Logistic regression adjustment |

## Visualizations

The analysis includes:

- Sample size by group
- Conversion rate by group
- Conversion rate with 95% confidence intervals
- Bootstrap distribution of conversion-rate difference
- Conversion rate by visit day
- Conversion rate by visit hour

## Requirements

```bash
pip install pandas numpy matplotlib
```

Optional, for logistic regression:

```bash
pip install statsmodels
```

## How to Run

You can run the analysis in a Jupyter Notebook or as a Python script using notebook-style cells.

If using Jupyter:

```bash
jupyter notebook
```

Then open the notebook and run the cells from top to bottom.

## Key Metrics

The main metrics used to make the business decision are:

- Treatment conversion rate
- Control conversion rate
- Absolute lift
- Relative lift
- Z-test p-value
- Chi-square p-value
- 95% confidence interval
- Bootstrap confidence interval

## Business Decision Framework

The new landing page should only be shipped if:

1. The treatment group has a higher conversion rate than the control group
2. The lift is statistically significant
3. The confidence intervals support a positive effect
4. The effect is practically meaningful for the business

If the statistical evidence is weak or the lift is negative, the recommendation is not to ship the new page yet.

## Final Recommendation

The final recommendation is based on both statistical significance and business impact. A statistically significant result is useful, but the company should also consider whether the observed lift is large enough to justify shipping the new landing page.
