# Kalpa Plus membership investigation
Meera asks: “We added more members, but fewer seem to renew. Should we offer everyone a discount?”
Use the three CSV files and DATA_DICTIONARY.md. All data is synthetic. Analyse as of 9 October 2026, end of day. Compare September 2025 with September 2026 using identical renewal definitions. October 2026 contains windows that are still open. The two plans are annual price tiers.

1. Inspect row counts, unique keys and date coverage. Draw the connections between tables before merging.
2. Define renewal eligibility, success and the observation window. Separate not-yet-due, mature and unresolved opportunities.
3. Compare paid member snapshots, renewal counts and rates. Is the same headline telling the same story?
4. Split first and later renewals. Group first renewals by joining cohort and compare complete opportunities.
5. Create one row per opportunity with prior-30-day and last-30-day benefit usage. Define Active = at least 4 uses, Occasional = 1–3, Inactive = 0. These are exercise rules, not universal business definitions. Build a transition table.
6. Among mature first-renewal non-renewals, distinguish no recorded payment attempt from attempted payment without success. Compare usage patterns and support contacts.
7. Challenge the discount proposal. Recommend different actions where justified and identify missing evidence before promising results.
8. Define success and stop signals for a future pilot. Do not label historical associations as effects of an intervention.

Starter notebook: Kalpa_Plus_Student.ipynb. Keep IDs as strings and money as numbers. Read the dictionary before assigning business meaning to any field.
