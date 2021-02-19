"""
Use to figure out if the issue with YNAB component is related to the
component itself or the package it uses to interact with YNAB

To run, you must have python3 and ynab-sdk installed on the machine
Install using pip3 install ynab-sdk

Replace API_KEY_HERE with your API key
Run the file using python3 apitest.py

If everything works, you should see a summary of your budgets
Otherwise you will see an error
"""

from ynab_sdk import YNAB

try:
    api_key = "API_KEY_HERE"
    apicheck = YNAB(api_key)
    print(apicheck.budgets.get_budgets())
except Exception:
    raise
