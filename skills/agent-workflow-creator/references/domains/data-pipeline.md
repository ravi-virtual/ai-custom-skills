# Data Processing & ETL Workflows

Domain guidance for workflows that ingest, transform, validate, and output structured data.

## Common Data Workflow Goals
- Transform raw data into a usable format
- Extract data from multiple sources and join it
- Clean and validate a dataset
- Run analysis and produce a report or dashboard
- Move data between systems (ETL)

## Recommended Patterns
- **Sequential Chain** for simple ETL
- **Map-Reduce** for large batch processing
- **Fan-Out/Fan-In** for multi-source ingestion

## Always-Present Steps
1. **Ingest** — load raw data from source (file, API, DB)
2. **Validate schema** — check expected fields and types
3. **Clean** — handle nulls, duplicates, encoding issues
4. **Transform** — reshape, join, aggregate
5. **Quality check** — assertions on output data
6. **Output** — write to destination

## Quality Assertions (build into every data workflow)
- Row count before vs. after (flag >5% loss)
- Null rate per column (flag if critical field >1% null)
- Type validation on all columns
- Range checks on numeric fields
- Uniqueness check on key columns
- Referential integrity for joins

## Prompt Templates

### Schema Validation Prompt
```
Given this data sample: {{data_sample}}
Expected schema: {{schema}}
Identify any schema violations, missing fields, or type mismatches.
Return JSON: { violations: [...], warnings: [...], passed: bool }
```

### Data Cleaning Prompt
```
Clean this dataset according to these rules:
- Remove exact duplicates
- Standardize date formats to ISO 8601
- Trim whitespace from string fields
- Replace empty strings with null
Data: {{raw_data}}
Return cleaned data in the same format.
```
