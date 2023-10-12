"""Constants for YNAB integration."""
DOMAIN = "ynab"
DOMAIN_DATA = f"{DOMAIN}_data"

REQUIRED_FILES = ["const.py", "manifest.json", "sensor.py"]
VERSION = "0.3.0"
ISSUE_URL = "https://github.com/wxt9861/ynab/issues"

STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""

CATEGORY_ERROR = """Unable to create attribute for category \
'{category}'. Make sure it exists in YNAB and the case is correct"""
ACCOUNT_ERROR = """Unable to create attribute for account \
'{account}'. Make sure it exists in YNAB and the case is correct"""

DEFAULT_NAME = "ynab"
DEFAULT_BUDGET = "last-used"
DEFAULT_CURRENCY = "$"
DEFAULT_API_ENDPOINT = "https://api.ynab.com/v1"

ICON = "mdi:finance"

CONF_NAME = "name"
CONF_ENABLED = "enabled"
CONF_SENSOR = "sensor"

CONF_BUDGET_KEY = "budget"
CONF_BUDGET_NAME_KEY = "budget_name"
CONF_CATEGORIES_KEY = "categories"
CONF_ACCOUNTS_KEY = "accounts"
CONF_CURRENCY_KEY = "currency"