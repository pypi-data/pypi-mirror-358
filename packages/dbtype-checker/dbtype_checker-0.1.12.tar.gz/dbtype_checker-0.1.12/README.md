# 🧠 dbtype_checker

A simple and lightweight tool to **detect columns stored in the wrong data type** in your database.  
It connects to your SQL database, samples data, and infers the **true data types** using intelligent pandas-based logic.

---

## 🚀 Features

- ✅ Detects `int`, `float`, `bool`, `datetime`, and `str`
- ✅ Identifies type mismatches based on actual data values (not just schema)
- ✅ Supports **MySQL**, **PostgreSQL**, and (optionally) **Oracle**
- ✅ Can **auto-fix** mismatched columns (via `ALTER TABLE`)
- ✅ Safe conversions with pre-cleaning (e.g., "true"/"false" to boolean)
- ✅ No LLMs or external APIs — **pure pandas + regex logic**

## 📦 Installation

Install via pip:

```bash
pip install dbtype_checker " OR" pip install dbtype-checker==0.1.10


""" 
## EXAMPLE USAGE

For postgres:

from dbtype_checker.checker import run_type_check_and_fix

# Detection
run_type_check_and_fix("postgresql+pg8000://user:password@localhost/database_name"dry_run=True)
# Correction
run_type_check_and_fix("postgresql+pg8000://user:password@localhost/database_name"dry_run=False)

For MySQL:

from dbtype_checker.checker import run_type_check_and_fix

# Detection
run_type_check_and_fix("mysql+pymysql://user:password@localhost:port/database", dry_run=True)
# Correction
run_type_check_and_fix("mysql+pymysql://user:password@localhost:port/database", dry_run=False)

For Oracle:
from dbtype_checker.checker import run_type_check_and_fix

db_url = "oracle+cx_oracle://username:password@host:1521/?service_name=your_service_name"
# Detection
run_type_check_and_fix(db_url, dry_run=True)

#Correction
run_type_check_and_fix(db_url,dry_run=False)   

For CLI:

# Detection
python -m dbtype_checker.checker --db_url "postgresql+pg8000://user:password@localhost/dbname" --dry_run true

#Correction
python -m dbtype_checker.checker --db_url "mysql+pymysql://user:password@localhost/dbname" --dry_run false

"""
