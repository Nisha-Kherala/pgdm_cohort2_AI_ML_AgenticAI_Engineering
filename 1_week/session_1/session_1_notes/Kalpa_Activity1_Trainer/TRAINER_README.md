# Kalpa Activity 1 — trainer pack

Distribute only the separate Student Pack ZIP to learners. This archive includes that full pack plus answers and generation/verification code.

- `Kalpa_Activity1/EXERCISES.md`: student instructions for the two historical exercises.
- `Kalpa_Activity1/DATA_DICTIONARY.md` and `Data_Dictionary.xlsx`: field meanings, table grain, keys, relationships and revenue/cost definitions.
- `trainer/TRAINER_GUIDE.md`: opening story, facilitation, exact answers and transition to descriptive statistics.
- `trainer/Activity1_SOLUTIONS_EXECUTED.ipynb`: worked Python/SQL solutions with recorded outputs.
- `trainer/Trainer_Results.xlsx`: verified inputs and calculated metrics, with adjustable future growth target and margin floor.
- `trainer/VERIFICATION_REPORT.md`: checks and case limitations.

## Reproduce and validate
From this archive's root folder:

```bash
python validate_pack.py
python build_pack.py
python validate_pack.py
python make_materials.py
```

Generation requires NumPy; the included requirements.txt records the version used. Validation, solutions and the learner calculations use Python's standard library. Keep the seed unchanged to regenerate the original CSV files. The two Excel files are finished companion artifacts; the generation scripts rebuild data, SQLite, Markdown and notebooks.

The reporting snapshot is 31 March 2026. This is Activity 1 (revenue); churn and repeat-purchase activity definitions need their own windows and history decisions before being taught using these records.
