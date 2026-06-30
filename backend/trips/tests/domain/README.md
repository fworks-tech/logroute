# Domain Layer Tests

Pure unit tests. No Django ORM, no database, no HTTP. Run in milliseconds.
Test the HOS engine simulation against FMCSA rule requirements.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `test_hos_engine.py` | 14+ test functions validating all HOS rules: 11-hr drive limit, 14-hr window, 30-min break, 10-hr reset, 70/60-hr cycle, fuel stops, multi-day logbook, 15-min grid snapping, edge cases. |
