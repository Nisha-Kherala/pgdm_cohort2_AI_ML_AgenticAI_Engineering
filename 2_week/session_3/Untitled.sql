# Using member_events, find the channels where members made at least 500 failed payment attempts.
# For each channel, show:
# - Number of failed payment attempts.
# - Number of distinct members who made those attempts.
# - Total event cost of those failed attempts.
# Include only events where event_type = 'PAYMENT_ATTEMPT' and outcome = 'FAILED'.
# Sort the result by failed payment attempts, highest first.

-- select channel,count(event_id) as number_events,count(distinct member_id) as total_member
-- from member_events
-- where event_type = 'PAYMENT_ATTEMPT' and outcome = 'FAILED'
-- group by channel
-- having count(event_id)>=500
-- order by count(outcome) DESC


# Using renewal_opportunities, examine renewals due in September 2026.
# For each renewal_number, show:
# - Number of renewal opportunities.
# - Total renewal fees.
# - Average renewal fee.
# Show only groups with at least 1,000 renewal opportunities, sorted by total renewal fees, highest first.
# Use expiry_date to identify the month.
# Think: Do these fees represent money actually collected, or amounts members were due to pay?


-- select renewal_number,count(renewal_id) as number_renewals, sum(renewal_fee) as total_renewal_fees, avg(renewal_fee) as Avg_renewal_fee
-- from renewal_opportunities
-- where month(expiry_date) = 9 and year(expiry_date) = 2026
-- group by renewal_number
-- having count(renewal_id)>1000
-- order by sum(renewal_fee) desc


# Kalpa’s team says: “Payment failures are the main reason members are not renewing. We should fix payments before offering discounts.”
# Using member_events, investigate whether the data supports this claim.

# Decide which comparisons matter, present evidence, and recommend what Kalpa should investigate first.

# What can this table establish—and what would you still need to know before accepting the claim?

-- select event_type,outcome,count(renewal_id)/(select count(*) from member_events) *100
-- from member_events
-- group by event_type,outcome


-- from renewal_oppurtunities
-- groupby outcome,detail_code



-- select member_id,join_date,count(*)
-- from members
-- group by member_id,join_date
-- having count(*)>1




-- select year(expiry_date),renewal_number,count(distinct member_id) as member_count
-- from renewal_opportunities
-- group by year(expiry_date),renewal_number


# “First-time renewals deserve more attention than later renewals. We should offer a discount whenever a member reaches their first renewal.”

# Using renewal_opportunities, investigate whether first renewals represent a large enough share of upcoming renewals—and membership fees—to justify prioritising them.
# Choose the comparisons you think matter, present evidence, and recommend what the team should examine next.

-- select renewal_number,year(expiry_date), count(distinct member_id)
-- from renewal_opportunities
-- where expiry_date < '2026-09-01'
-- group by renewal_number,year(expiry_date)


-- select *,CASE WHEN renewal_deadline > expiry_date+7 THEN
-- from renewal_opportunities
-- where renewal_deadline > expiry_date+7

-- select CASE WHEN annual_fee>1500 THEN 'High'
--             ELSE 'Low'
--             END as fee_status,count(*) as stat_count
-- from members
-- group by (CASE WHEN annual_fee>1500 THEN 'High'
--             ELSE 'LOW'
--             END)


-- Using renewal_opportunities, compare renewal opportunities due in September 2026.
-- Use CASE to classify them as:
-- FIRST_RENEWAL: renewal_number = 1
-- LATER_RENEWAL: renewal_number > 1
-- For each category, show the number of opportunities, total renewal fees, and average renewal fee.
-- Which category accounts for more money due? Does that tell us which category is more likely to renew?

-- select CASE WHEN renewal_number=1 THEN 'FIRST_RENEWAL' 
--             WHEN renewal_number>1 THEN 'LATER_RENEWAL' END As renewal_type,count(renewal_id) as no_oppurtunities, sum(renewal_fee) as total, avg(renewal_fee) as AvgRenFee
-- from renewal_opportunities
-- where expiry_date > '2026-09-01' and expiry_date < '2026-10-01'
-- group by (CASE WHEN renewal_number=1 THEN 'FIRST_RENEWAL' 
--             WHEN renewal_number>1 THEN 'LATER_RENEWAL' END)

-- Using member_events, examine payment attempts made during September 2026.
-- For each channel, show:
-- - Total payment attempts.
-- - Successful payment attempts.
-- - Failed payment attempts.


-- select channel,outcome,count(renewal_id)
-- from member_events
-- where dateformat(expiry_date,%Y-%M) = '2026-09' 
-- group by channel,outcome


-- Using member_events, investigate failed payment attempts during September 2026. Use CASE in GROUP BY to combine failure reasons into:
-- Technical: PSP_TIMEOUT
-- Authentication: AUTHENTICATION_FAILED
-- Funds: INSUFFICIENT_FUNDS
-- Other: Any remaining failure reason Group by channel and failure category. For each combination, calculate:
-- Number of failed attempts.
-- Number of distinct members affected.
-- Failed attempts per affected member.
-- Total event cost. Keep only groups affecting at least 30 members, and sort by attempts per affected member, highest first. Which group shows the most repeated failures per member? Is that also the group affecting the most people—and which would you investigate first?

-- select channel,case when detail_code = 'PSP_TIMEOUT' then 'Technical'
--                     when detail_code = 'AUTHENTICATION_FAILED' then 'Authentication'
--                     when detail_code = 'INSUFFICIANT_FUNDS' then 'Funds'
--                     else 'Others' end as type_failure,count(*) as no_of_failed_attempts,count(distinct member_id) as members_affected, 
-- from member_events
-- where (event_type = 'PAYMENT_ATTEMPT' and outcome = 'FAILED' ) and (event_time > '2026-09-01' and event_time < '2026-10-01')
-- group by channel,case when detail_code = 'PSP_TIMEOUT' then 'Technical'
--                     when detail_code = 'AUTHENTICATION_FAILED' then 'Authentication'
--                     when detail_code = 'INSUFFICIANT_FUNDS' then 'Funds'
--                     else 'Others' end

-- select * from member_events

-- Using members and renewal_opportunities, calculate for each city:
-- - Number of renewal opportunities.
-- - Number of distinct members with an opportunity.
-- - Total renewal fees due.

-- select m.city,count(renewal_id) as renewal,count(distinct m.member_id) as member_distinct,sum(ro.renewal_fee) as tot_renewal_fees
-- from members m
-- join renewal_opportunities ro
-- on m.member_id = ro.member_id
-- group by m.city

-- Using renewal_opportunities and member_events, investigate how many events are recorded against each renewal number.
-- Number of distinct renewal opportunities.
-- Number of recorded events.
-- Total event cost, showing 0 when no costs are recorded.

-- select ro.renewal_id, count(event_id) as recorded_events,count(distinct ro.renewal_id) as dist_renewal_opp,COALESCE(sum(me.event_cost),0) as tot_eve_cost
-- from renewal_opportunities ro
-- join member_events me
-- on ro.renewal_id=me.renewal_id
-- group by ro.renewal_id

-- 1. Which cities have the most renewals coming due?
-- For opportunities expiring in September 2026, show each city’s:
-- - Number of distinct members due for renewal.
-- - Number of renewal opportunities.
-- - Total renewal fees due.

-- select m.city,count(distinct m.member_id) as members_due,count(ro.renewal_id) as renewal_opp,sum(ro.renewal_fee) as tot_ren_fees
-- from members m
-- join renewal_opportunities ro
-- on m.member_id=ro.member_id and (ro.expiry_date>'2026-09-01' and ro.expiry_date < '2026-10-01')
-- group by m.city

-- Include members who were not due
-- Show every member from Delhi or Mumbai, along with any renewal opportunities expiring in September 2026.
-- Include members who had no opportunity that month. Return member ID, city, renewal ID and expiry date.
-- Think: Which condition belongs in ON, and which belongs in WHERE?

-- Who had no payment attempt recorded?
-- For September 2026 renewal opportunities, find those with no PAYMENT_ATTEMPT event.
-- Return renewal ID, member ID, renewal number and expiry date.
-- Use a LEFT JOIN. An opportunity with benefit or reminder events—but no payment attempt—must still appear.

-- Using renewal_opportunities, display every opportunity and add the total renewal fees due across all opportunities belonging to that member.


-- select *,sum(renewal_fee) over(partition by member_id)
-- from renewal_opportunities

-- *Using* members, display every member and add the number of members from the same city.

-- select *,count(member_id) over(partition by city) as mem_per_city
-- from members 

##
-- Members in each city Using members, display every member and add the number of members from the same city.

-- Events per renewal opportunity Using member_events, display every event and add the total number of events recorded against the same renewal_id.

-- Cost of serving each member Using member_events, display every event and add the total recorded event cost for that member.

-- Successful collections by channel Using member_events, select only successful payment attempts. Display every selected event and add the total successful payment amount collected through that event’s channel.
##
# for each member find its latest payment attempt

-- with temp as (select * 

### Question 1: Highest service costs in each city

-- Kalpa wants to identify members with the highest recorded service costs in each city.

-- Using `members` and `member_events`:

-- 1. Calculate each member’s total `event_cost` during September 2026.
-- 2. Include members with no events during the month, showing their cost as zero.
-- 3. Use a CTE to calculate the member totals.
-- 4. Use a window function to rank members within each city, highest cost first.
-- 5. Return members in the top three distinct cost levels in each city. Equal costs should receive the same rank, with no gaps between ranks.

-- **Required columns:** member ID, city, total event cost and rank.

-- **Explain:** Where should the September date condition go to preserve members with no events?

select *,sum(event_cost) over(partition by city order by event_cost desc)
from member_events
group by city



-- -

-- ### Question 2: Daily renewal collections

-- Kalpa wants to understand how renewal collections accumulated during September 2026.

-- Using `member_events`:

-- 1. Select successful payment attempts made during September 2026.
-- 2. Use a CTE to calculate total collections for each channel and payment date.
-- 3. Use window functions to calculate:
--    - Cumulative collections within each channel, ordered by date.
--    - Average daily collections for each channel across dates with successful payments.
--    - The difference between each day’s collections and that channel’s average.

-- **Required columns:** channel, payment date, daily collections, cumulative collections, average daily collections and difference from average.

-- **Explain:** Why is the average of daily collection totals different from the average amount per successful payment?






