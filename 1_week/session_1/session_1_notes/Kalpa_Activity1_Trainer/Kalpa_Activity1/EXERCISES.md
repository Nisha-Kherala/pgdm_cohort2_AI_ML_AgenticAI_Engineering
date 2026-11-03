# Activity 1 — Outcome: revenue and the guardrail

## Your role
Kalpa Retail sells consumer goods through its app, website and stores. Last year, it made ₹100 crore in revenue. This year, it made ₹104 crore, against a plan of ₹115 crore.

Marketing says, “We need more customers. Give us ₹12 crore for acquisition.”

You are Kalpa Retail's new data team. Meera asks: “Revenue grew less than planned. Marketing wants ₹12 crore for acquisition. Before I commit, show me what changed and whether our recent growth protected profitability.”

The original plan was 15% growth. For the next annual reporting period, success means at least 15% growth in eligible net revenue while contribution margin reaches at least the agreed 20% floor. Today's task establishes historical evidence; no proposed future acquisition programme has been executed in these files.

Use the full dataset. Complete both exercises on the SAME financial years. All monetary amounts are whole INR. Read the dictionary before calculating.

## Before coding — 3 minutes
Write one sentence stating the problem, the primary business metric, the time window and the guardrail. Identify the decision Meera is considering. Do not adopt “insufficient acquisition” as a proven cause.

## Exercise 1: Check Marketing's explanation — 30 minutes
Meera: “Is customer acquisition the branch that is short, or is something else changing?”

### A. Python calculation
1. Decide which order statuses belong in revenue and purchase counts. State your rule.
2. Calculate eligible revenue from the raw monetary fields. Show the relationship between gross amount, discounts, refunds and recognised revenue.
3. For each financial year, calculate completed orders, distinct purchasing customers and revenue.
4. Calculate orders per purchasing customer and revenue per order. Keep the numerators and denominators alongside the ratios.
5. Calculate the percentage change in all five measures. Distinguish a difference in counts from a percentage change.
6. Check that customers × orders per customer × revenue per order returns each year's revenue. Check that the product of the three current-year / previous-year branch ratios returns the annual revenue ratio. Use full precision until display.

### B. SQL confirmation
Reproduce the base totals and ratios from the SAME data in `kalpa.sqlite`. Use `eligible_orders` if you want the eligibility/amount scaffold; inspect how it is defined. Sort results by period. Compare the Python and SQL totals before interpreting them.

### C. Response to Meera — maximum 100 words
State what changed, which branch deserves investigation and what these results do not establish. Address Marketing's explanation directly. Does a lower overall frequency mean every existing customer bought less often? Explain why you cannot assume that.

Deliver: one two-period results table, a Python/SQL reconciliation and the short response.

## Exercise 2: Was the growth profitable? — 20 minutes
Meera: “Before we celebrate revenue growth, did we protect the contribution-margin floor?”

1. Inspect the grain and join keys of order_costs and marketing_spend. Write how you will combine them without repeating money.
2. Sum product, fulfilment and payment costs for each financial year using the historical order-cost records.
3. Sum historical marketing expenditure by financial year. These are costs already incurred; they are NOT the proposed ₹12 crore budget.
4. Combine the annual cost components, then calculate contribution and contribution margin using the revenue from Exercise 1.
5. Calculate cost growth and contribution growth. State margin movement in percentage points.
6. Compare both years against the 20% floor. Was positive revenue growth sufficient to meet our desired business outcome?
7. Confirm your result with SQL. Aggregate each grain separately before joining the annual summaries; a query scaffold is provided.
8. Update your response to Meera in at most 100 words: what is now different about your assessment, what should be investigated, and what is still unknown?

Deliver: a cost bridge, contribution/margin table, guardrail verdict and updated response.

## Closing challenge — 5 minutes
Marketing suggests measuring acquisition success by account registrations. Give one way registrations could increase without helping our agreed outcome, and identify another measurement you would request.

## Hand-off to Deconstruction
Do not conclude that “unchanged average order value” means an unchanged customer experience. For the next session, bring two questions about what the averages could hide. We will examine customer-level frequency, order-level value, segments, channels, median, quartiles, spread and distributions.

## Ungraded review criteria
Your work is complete when your eligibility/metric definitions are explicit; counts are distinct where needed; both languages agree; totals reconcile; costs are not duplicated; the margin verdict follows the agreed floor; and observed changes are distinguished from causes or campaign effects. No model training, causal claim or future campaign forecast is required today.
