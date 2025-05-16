# -*- coding: utf-8 -*-
"""
Created on Sat May 17 00:38:14 2025

@author:Erqian Chen
"""

#need "pip install pandas openpyxl"
import sqlite3
import pandas as pd

# Connect to the SQLite database file (make sure the path to app.db is correct)
conn = sqlite3.connect('app.db')

# Query the top 10 training plans
plans_df = pd.read_sql_query("SELECT * FROM workout_plans LIMIT 10", conn)

# Query the first 10 training records
records_df = pd.read_sql_query("SELECT * FROM workout_records LIMIT 10", conn)

# Export to Excel file
plans_df.to_excel("migration_1_plans.xlsx", index=False)
records_df.to_excel("migration_2_records.xlsx", index=False)

# Close the connection
conn.close()

print("✅ Data export is complete! The generated files are as follows:")
print(" - migration_1_plans.xlsx")
print(" - migration_2_records.xlsx")

