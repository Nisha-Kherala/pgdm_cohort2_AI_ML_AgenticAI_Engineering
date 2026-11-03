# Verification report

Status: **PASS**. Both Python and SQLite calculations agree with the teaching targets.

95 checks passed.

Checks cover every primary key, required field, foreign key and compound spend grain; exact CSV/database row equality; date boundaries and signup timing; monetary identities; one-to-one cost coverage; cancelled-order scope; exact target totals; revenue-tree identities; segment reconciliation; independent Python/SQL results; database integrity; and deliberate wrong-query probes.

| Measure | Previous | Current |
|---|---:|---:|
| Completed orders | 50,000 | 52,000 |
| Purchasing customers | 10,000 | 13,000 |
| Revenue (INR) | 1,000,000,000 | 1,040,000,000 |
| Total specified cost (INR) | 800,000,000 | 884,000,000 |
| Contribution (INR) | 200,000,000 | 156,000,000 |
| Contribution margin | 20% | 15% |

Amounts are whole rupees and reconcile exactly. Ratios are compared at full precision; rounding is for display. Monetary values, cost coverage and entity IDs are compared exactly. Detailed results and SHA-256 CSV hashes are in verification_report.json.

Limitations: synthetic case calibration, stable customer segments, simplified within-period recognition/refunds, no line items or inventory, no pre-period purchase history, contribution rather than net profit, and no causal intervention results. The data includes 106,400 order records, of which 102,000 are completed and 4,400 are cancelled before dispatch.

Delivery checks: rebuilding the SQLite database from the six CSV files reproduced every original table row. All five student notebook code cells executed from a clean copied folder. Regenerating with the same seed reproduced identical CSV SHA-256 hashes. Both Excel workbooks were rendered and visually checked.
