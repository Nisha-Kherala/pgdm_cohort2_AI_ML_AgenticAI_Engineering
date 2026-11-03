# Kalpa Plus data dictionary
Synthetic teaching data. Snapshot: 9 October 2026 at 23:59:59 IST. Timestamps are local India time without timezone suffixes. Currency is whole Indian rupees.

## Business definitions
Plus has two annual price tiers: PLUS_STANDARD (₹1,499) and PLUS_PREMIUM (₹2,499). Both last one calendar year, renewed on the original joining anniversary. This dataset uses annual plans to isolate first versus later renewal without monthly/annual duration differences.

A renewal opportunity arises when one paid term expires. Its observation window runs from seven days before expiry through seven days after expiry, inclusive. The deadline date is included in full. A successful payment in that window counts as renewed. Only one successful renewal payment is allowed per opportunity.

At the snapshot, an unrenewed opportunity with a deadline that has not finished is unresolved. Count renewal rates only for opportunities whose full window has closed. Members who have not reached their first expiry are not in the renewal denominator.

Renewal rate = successful renewals / mature renewal opportunities. 

This is a term-level rate: a member can contribute opportunities in different years. In a September comparison, each eligible member contributes one opportunity. Never count event rows as members or renewals.
The expiry date ends paid access. A member paying after expiry but within the grace window is counted as renewed but may have had a temporary access gap. Membership status and benefit-usage status are separate.
Annual renewal cash received is not accounting revenue recognition. Event costs are observed direct costs for recorded events, not a full annual contribution statement.

## members.csv
One row per member. Primary key: member_id. This is a new synthetic membership population, not an implicit join to the earlier retail customers.csv.
| Column | Type | Meaning |
| member_id | string | Unique Plus member ID |
| join_date | date | First paid membership start, YYYY-MM-DD |
| plan_code | string | PLUS_STANDARD or PLUS_PREMIUM; plan stays fixed in this case |
| annual_fee | integer | Full annual membership fee in INR |
| acquisition_channel | string | APP, WEB or STORE at joining; not necessarily a later payment channel |
| city | string | Member home city |
| status_2025_10_09 | string | Billing status at 9 October 2025 end of day: PAID, EXPIRED or NOT_JOINED |
| status_2026_10_09 | string | Billing status at 9 October 2026 end of day: PAID or EXPIRED |

## renewal_opportunities.csv
One row per paid term approaching expiry. Primary key: renewal_id. member_id is a foreign key to members. All generated opportunities observed by the snapshot are included, covering September 2024, September 2025, September 2026 and open October 2026 windows. Memberships not yet due have no opportunity row.
| Column | Type | Meaning |
| renewal_id | string | Unique renewal opportunity ID |
| member_id | string | Member facing this expiry |
| renewal_number | integer | 1 = first renewal; 2, 3 = later renewals; consecutive for a continuing member |
| expiry_date | date | Original anniversary on which this paid term expires |
| renewal_deadline | date | Last calendar day of the grace window: expiry_date + 7 days |
| renewal_fee | integer | Full annual fee offered for the new term, INR |
| offered_discount | integer | Offer reduction in INR; zero means no discount |
There is no renewal outcome column. Derive it from successful PAYMENT_ATTEMPT events and the window definition.

## member_events.csv
One row per recorded event. Primary key: event_id. renewal_id joins to renewal_opportunities; member_id is redundant for audit and must agree with that opportunity's member. Multiple events may belong to one opportunity.
| Column | Type | Meaning |
| event_id | string | Unique event ID |
| member_id | string | Member involved |
| renewal_id | string | Opportunity to which the event belongs |
| event_time | datetime | Observed local timestamp, YYYY-MM-DD HH:MM:SS |
| event_type | string | BENEFIT_USED, REMINDER_SENT, PAYMENT_ATTEMPT or SUPPORT_CONTACT |
| channel | string | Event channel: APP, WEB, EMAIL or SUPPORT |
| outcome | string | SUCCESS/FAILED for payments, SUCCESS for benefits, DELIVERED/UNDELIVERED for reminders, LOGGED for support |
| detail_code | string | Benefit, failure or contact category; blank on a successful payment |
| amount | integer | Attempted payment amount in INR; only successful payments represent cash received. Non-payment events use zero |
| event_cost | integer | Observed direct handling/service cost of that event in INR, including failed-attempt costs |
Benefit detail codes: FREE_DELIVERY, PRIORITY_SUPPORT, MEMBER_OFFER. Payment failure codes: PSP_TIMEOUT, AUTHENTICATION_FAILED, INSUFFICIENT_FUNDS. Support codes: FREE_DELIVERY_UNAVAILABLE, PRICE_QUERY, BENEFITS_QUERY, RENEWAL_HELP. Reminder code: RENEWAL_REMINDER.
Benefit events cover the 60 calendar days before each expiry: prior window = days 60 to 31 before expiry; recent window = days 30 to 1 before expiry. Include dates by normalising timestamps. Zero events means zero recorded use, not missing data, within these specified windows.
There is one reminder seven days before expiry. Payment attempts occur within the renewal window. Support contacts are recorded around the expiry. No event after the snapshot is included.
The event table is an extract of these defined renewal-centred windows, not a complete lifelong activity log. It cannot establish total company benefit usage between those windows.

## Join rules
members.member_id → renewal_opportunities.member_id: one to many. renewal_opportunities.renewal_id → member_events.renewal_id: one to many.
Aggregate events to one row per renewal_id before joining event summaries to opportunities. Preserve all opportunities with a left join, including those with no payment attempt. Preserve all members when asking who has not reached renewal.

Dates and blank detail codes need parsing; no deliberate corrupt IDs or duplicate rows have been planted. This exercise is about analytical definitions, cohorts and table grain.

## Limits
These tables describe patterns. They do not contain a randomly assigned recovery pilot, a causal campaign effect, a full annual cost ledger, a price-change history or survey-confirmed reasons for leaving. Payment failure codes support investigating the renewal process; they do not by themselves establish a particular software root cause. Acquisition channel and payment channel answer different questions.
