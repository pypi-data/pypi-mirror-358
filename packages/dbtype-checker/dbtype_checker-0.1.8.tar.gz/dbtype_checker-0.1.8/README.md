# 🧠 dbtype_checker

A simple and lightweight tool to **detect columns stored in the wrong data type** in your database.  
It connects to your SQL database, samples data, and infers the **true data types** using intelligent pandas-based logic.

---

## 🚀 Features

- Detects `int`, `float`, `bool`, `datetime`, `str`
- Identifies type mismatches based on actual values
- Works with PostgreSQL, MySQL, Oracle (via SQLAlchemy)
- Easy to integrate into data pipelines 
- No heavy dependencies — pure pandas + regex logic

---

## 📦 Installation

Install via pip:

```bash
pip install dbtype_checker " OR" pip install dbtype-checker==0.1.8


""" 
## EXAMPLE USAGE

For postgres:

from dbtype_checker.checker import run_type_check_and_fix

run_type_check_and_fix("postgresql+pg8000://user:password@localhost/database_name"dry_run=True)
run_type_check_and_fix("postgresql+pg8000://user:password@localhost/database_name"dry_run=False)
print_mismatches(db_url)

For MySQL:

from dbtype_checker.checker import run_type_check_and_fix

# DRY RUN
run_type_check_and_fix("mysql+pymysql://user:password@localhost:port/database", dry_run=True)
run_type_check_and_fix("mysql+pymysql://user:password@localhost:port/database", dry_run=False)

For Oracle:
from dbtype_checker.checker import print_mismatches

db_url = (
    "oracle+cx_oracle://username:password@host:1521/"
    "?service_name=your_service_name"
)
print_mismatches(db_url)    
"""
