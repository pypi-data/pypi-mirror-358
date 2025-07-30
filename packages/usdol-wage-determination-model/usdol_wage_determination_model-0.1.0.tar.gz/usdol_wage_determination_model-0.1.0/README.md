# USDOL Wage Determination Model

Pydantic model for USDOL prevailing wage determination records


## Scripts

```bash
uv run safety scan
uv run ruff check
uv run -m pytest -vv --cov=src --cov-report=term --cov-report=xml
```


## References

* [Wage Determintion Search on SAM.gov](https://sam.gov/search/?index=dbra)
* [Davis-Bacon and Related Acts (DBRA)](https://www.dol.gov/agencies/whd/government-contracts/construction)


## To-Do

* Model adjustments
  * Job: add ID and perhaps an enumeration / taxonomy (US-wide or state specific?)
  * Wage: taxonomy for pay types (regular, overtime, double-time, hazard), validations, more flexible fringe
  * Determination: validation for rate identifier
  * Location: Validation of state (and maybe county?), also add county identifier
  * All: descriptions
* Tests to add
  * happy path for all fields in WD
  * bad effective range in WD
  * independent tests for job / location models
  * in wage model: fractions of penny, too big a rate, invalid currency, valid non-us currency
* Generate test data and test cases
* Add docstrings and then enable "D" checks in ruff
