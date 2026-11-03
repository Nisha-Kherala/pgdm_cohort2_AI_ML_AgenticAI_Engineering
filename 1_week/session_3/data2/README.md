# Verified source evidence — release after the initial audit

These are synthetic re-exports from the system of record for this lab, not values guessed from distributions.
- approved_reporting_calendar.csv: Finance-approved year boundaries; use in place of the questionable calendar export.
- verified_order_fields.csv: Specific corrected order attributes from the order system, keyed by order_id. Blank cells mean no correction supplied for that field, not a source value of zero or blank.
- verified_customer_segments.csv: Missing segment values recovered from the stable customer master.

Only apply supplied nonblank fields. Log replacements. In a real investigation, establish provenance and obtain these extracts from the data owner; if unavailable, preserve unknowns, quantify coverage, and limit conclusions.
