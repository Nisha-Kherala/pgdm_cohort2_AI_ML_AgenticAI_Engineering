# Kalpa Plus Groupby Practice

Use the existing Kalpa Plus CSV files. Answer each question independently using the original DataFrames.

- Use `groupby().agg()` for every grouped calculation.
- Use `.loc` whenever a question asks you to filter source rows or the aggregated result.
- Give calculated columns the names requested in the question.
- Work with one table at a time. No joins, merges, pivots, `apply` or loops are needed.
- All money values are in INR. A payment attempt is not necessarily a successful payment, and an event count is not a member count.

## Load the data

Run this setup once. Change `DATA_DIR` to the folder containing your three CSVs.

```python
from pathlib import Path
import pandas as pd

DATA_DIR = Path(".")

members = pd.read_csv(
    DATA_DIR / "members.csv",
    parse_dates=["join_date"]
)

renewals = pd.read_csv(
    DATA_DIR / "renewal_opportunities.csv",
    parse_dates=["expiry_date", "renewal_deadline"]
)

events = pd.read_csv(
    DATA_DIR / "member_events.csv",
    parse_dates=["event_time"]
)

# Date columns supplied for the exercises.
members["join_year"] = members["join_date"].dt.year
renewals["expiry_year"] = renewals["expiry_date"].dt.year
renewals["expiry_month"] = renewals["expiry_date"].dt.month
```

## Questions

### 1

Using `members`, group by `acquisition_channel`. Return:

- `member_count`: number of members.
- `average_annual_fee`: mean annual fee.
- `earliest_join`: earliest joining date.
- `latest_join`: latest joining date.

### 2

Using `.loc`, select members whose `status_2026_10_09` is `"PAID"`. Group them by `city` and return:

- `paid_members`: number of members.
- `average_annual_fee`: mean annual fee.
- `channels_present`: number of distinct acquisition channels.

### 3

Select members who were `"PAID"` on 9 October 2025 but `"EXPIRED"` on 9 October 2026. Group by `acquisition_channel` and return:

- `expired_members`: number of members.
- `average_annual_fee`: mean annual fee.

Use `.loc` on the aggregated result to display only channels with at least 300 such members.

### 4

Select members who joined in 2025 or 2026 and are `"PAID"` at the current snapshot. Group by both `join_year` and `acquisition_channel`. Return:

- `paid_members`: number of members.
- `cities_present`: number of distinct cities.
- `average_annual_fee`: mean annual fee.

### 5

Select currently paid members acquired through `"APP"` or `"WEB"`. Group by `city` and return:

- `paid_members`: number of members.
- `plans_present`: number of distinct plans.
- `average_annual_fee`: mean annual fee.

Using `.loc` on the summary, display only cities with at least 500 paid members and an average annual fee above 1,750. Show only `paid_members` and `average_annual_fee` in the final output.

### 6

Using `renewals`, group by `renewal_number` and return:

- `members_due`: number of renewal records.
- `average_fee`: mean renewal fee.
- `average_discount`: mean offered discount, including zero discounts.
- `maximum_discount`: largest offered discount.

These results describe offers and members due for renewal, not successful renewals.

### 7

Select renewal records with expiry month September and expiry year 2025 or 2026. Group by `expiry_year` and return:

- `members_due`: number of renewal records.
- `distinct_members`: number of distinct member IDs.
- `first_expiry`: earliest expiry date.
- `last_expiry`: latest expiry date.

Check whether `members_due` and `distinct_members` agree in each year. What would a disagreement mean?

### 8

Select September renewal records from 2025 and 2026. Group by both `expiry_year` and `renewal_number`. Return:

- `members_due`: number of renewal records.
- `average_fee`: mean renewal fee.
- `total_offered_discount`: sum of offered discounts.

The discount total is the sum of amounts offered across records; it is not proof that all those discounts were redeemed.

### 9

Select September 2026 renewal records with `offered_discount` greater than zero. Group by `renewal_number` and return:

- `discounted_offers`: number of records.
- `average_discount`: mean offered discount.
- `minimum_discount`: smallest offered discount.
- `maximum_discount`: largest offered discount.

Use `.loc` on the summary to keep only groups with at least 50 discounted offers.

### 10

Select records whose expiry year is 2026 and whose `renewal_deadline` is before 10 October 2026. Group by `renewal_number` and return:

- `members_due`: number of records.
- `earliest_deadline`: earliest deadline.
- `latest_deadline`: latest deadline.

Explain why this filter excludes renewal windows still open at the end of 9 October. Do not calculate renewal rates: this table alone does not contain successful payment outcomes.

### 11

Using `events`, group by `event_type` and return:

- `event_count`: number of events.
- `distinct_members`: number of distinct members.
- `distinct_renewals`: number of distinct renewal IDs.
- `total_event_cost`: sum of recorded event costs.

Why can `event_count` exceed `distinct_members`?

### 12

Select only `"PAYMENT_ATTEMPT"` events with outcome `"SUCCESS"`. Group by `channel` and return:

- `successful_payments`: number of successful payment events.
- `cash_collected`: sum of payment amounts.
- `average_payment`: mean payment amount.
- `total_payment_event_cost`: sum of recorded costs for these successful events.

The cost total here excludes failed payment attempts and other event types.

### 13

Select failed payment-attempt events. Group by both `channel` and `detail_code`. Return:

- `failed_attempts`: number of failed events.
- `affected_members`: number of distinct members.
- `affected_renewals`: number of distinct renewal IDs.
- `total_failure_cost`: sum of recorded costs for these failed events.

Using `.loc` on the aggregated result, keep only groups with at least 100 failed attempts and at least 40 affected members.

### 14

Select `"BENEFIT_USED"` events recorded through `"APP"` or `"WEB"`. Group by `detail_code` and return:

- `uses`: number of benefit-use events.
- `members_using`: number of distinct members.
- `total_cost`: sum of recorded event costs.
- `average_cost_per_use`: mean event cost.

Using `.loc` on the summary, display only benefits whose average cost per use exceeds 30. Show only `uses`, `members_using` and `average_cost_per_use`.

### 15

Select `"SUPPORT_CONTACT"` events whose detail code is either `"FREE_DELIVERY_UNAVAILABLE"` or `"RENEWAL_HELP"`. Group by `detail_code` and return:

- `contacts`: number of support contacts.
- `members_contacting`: number of distinct members.
- `renewals_involved`: number of distinct renewal IDs.
- `total_support_cost`: sum of recorded support costs.

Explain why the number of members contacting support cannot automatically be treated as the number of lost members.

## Submission

Submit one notebook with the code and output for all 15 questions. Answer the short interpretation questions in Markdown cells. Keep each question independent; do not modify the original source DataFrames while answering.
