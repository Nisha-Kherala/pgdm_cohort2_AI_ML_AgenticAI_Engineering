# Trainer guide — Activity 1

## Timing and sequence
Introduction 25 min; Exercise 1 30 min; Exercise 2 20 min; closing challenge 5 min. Reveal costs after the revenue discussion. Use the prepared environment so installation does not consume teaching time.

## Opening conversation — 25 minutes
1. Read the story aloud and ask everyone to write their first proposed solution (3 min). Expect advertising, dashboards or prediction models.
2. Ask: “What is the problem, and what decision does Meera need to make?” Collect answers. Separate the observed growth shortfall from the assumed acquisition explanation (5 min).
3. Ask: “If registrations doubled but revenue did not move, would we have succeeded?” Agree that registrations are an intermediate measure; the business outcome is eligible net revenue (4 min).
4. Put the next annual agreement on the board: grow net revenue at least 15% from the ₹104 crore baseline, with contribution margin at least 20%. Ask: “Could a discount help the first number and hurt the second?” Define contribution using the costs supplied in this case (5 min).
5. Build the tree together: revenue = purchasing customers × orders per purchasing customer × revenue per order. Ask learners to name each numerator, denominator and time window. The branches explain where to look; they do not identify a cause (5 min).
6. Introduce the two tasks: first check the revenue explanation, then check the historical margin. Ask learners to write their outcome sentence before coding (3 min).

## Story consistency
The financial years in the data reproduce ₹100 crore → ₹104 crore. The missed current-year plan was ₹115 crore. A new 15% target on the ₹104 crore baseline is ₹119.6 crore. The 20% margin floor is the PREVIOUS year's reference level. Do not tell students the current margin is 20%; it is 15%, discovered in Exercise 2. To meet the future agreement Kalpa must restore that floor. The proposed ₹12 crore acquisition request is not an expense row. Actual historical marketing costs are ₹7 crore and ₹9.52 crore.

## Exact answer key
| Metric | FY 2024-25 | FY 2025-26 | Change |
|---|---:|---:|---:|
| Recognised revenue | ₹100 crore | ₹104 crore | +4% |
| Completed orders | 50,000 | 52,000 | +4% |
| Purchasing customers | 10,000 | 13,000 | +30% |
| Orders per purchasing customer | 5 | 4 | −20% |
| Revenue per order | ₹20,000 | ₹20,000 | 0% |
| Product cost | ₹68 crore | ₹71.6 crore | |
| Fulfilment cost | ₹4 crore | ₹5.72 crore | |
| Payment cost | ₹1 crore | ₹1.56 crore | |
| Marketing cost | ₹7 crore | ₹9.52 crore | |
| Total specified cost | ₹80 crore | ₹88.4 crore | +10.5% |
| Contribution | ₹20 crore | ₹15.6 crore | −22% |
| Contribution margin | 20% | 15% | −5 percentage points |
| 20% margin floor | MET | BREACHED | |

## Suggested responses
Exercise 1: Buyers grew 30%, but overall orders per buyer fell 20%; average revenue per order was flat. Frequency deserves investigation before adopting acquisition as the main explanation. This does not show every returning customer reduced their purchases or that acquisition is unprofitable.

Exercise 2: Costs grew faster than revenue, contribution declined and the margin floor was breached. Investigate cost categories and order economics alongside frequency. Contribution is not net profit and no future campaign has been tested.

## Misconceptions to surface
- All registered customers are not this year's purchasing customers.
- COUNT(*) counts orders even if the column is named customers.
- Cancelled pre-dispatch orders do not recognise sales.
- Discount and refund amounts are already deducted in net revenue.
- Marketing expenses are incurred at month/channel/purpose grain; do not attach their full amount to every order.
- A mean order value of ₹20,000 does not imply most orders are near ₹20,000.
- A −5 percentage-point margin move is different from a −25% relative margin move.
- Customer changes and average changes are descriptions, not causes.

## Next session: Deconstruction and descriptive statistics
Use orders as the unit for order-value distribution; use customer-period as the unit for purchase-frequency distribution. Attach customer segment and order channel only when needed. Customers can buy in several channels, so unique customers do not generally add across channels.

| Distribution | Previous | Current |
|---|---:|---:|
| Mean order value (INR) | 20,000.00 | 20,000.00 |
| Median order value (INR) | 7,978.00 | 7,394.00 |
| IQR, inclusive linear quartiles (INR) | 13,450.25 | 13,183.50 |
| Population standard deviation (INR) | 37,314.56 | 38,108.84 |
| Median orders per purchasing customer | 4.00 | 3.00 |

The aggregate mean order value is unchanged while median and spread differ. Retail-Plus is the segment with a substantial frequency and revenue deterioration. Keep these facts in the trainer pack; learners discover them next session. Small synthetic populations are not evidence of market-wide effects.

## Data design
There are 7,000 buyers in both annual periods, 3,000 previous-only and 6,000 current-only. Two thousand registered customers never make a completed purchase. These support later cohort work but are not the previously discussed 10,000/12,000 quarterly churn illustration. That quarterly story must be recalibrated before reuse: this dataset compares complete financial years, and current buyers total 13,000. There is no pre-April-2024 purchase history, so “current-only” does not prove lifetime first purchase. Do not use signup as a substitute for first purchase. Churn and lifetime first-to-second-purchase activities need their own defined windows/history extension.

The record variability is intentional, while headline totals are constrained. There are no duplicate primary keys, orphan references, missing costs or malformed amounts. Do not tell learners the generator's targets or planted distribution patterns before they compute.

## Reproducibility
`build_pack.py` generates the six related raw files and database using seed 20261005 (requires NumPy). Student calculations, loader and solutions use only Python's standard library. `validate_pack.py` independently reads the CSVs and runs both SQL solutions. The trainer notebook contains captured outputs from executing its Python cells against the delivered dataset. SQL was executed in SQLite; no claim of a PostgreSQL runtime test is made.
