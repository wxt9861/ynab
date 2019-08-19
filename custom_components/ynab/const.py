DOMAIN = "ynab"
DOMAIN_DATA = "{}_data".format(DOMAIN)

PLATFORMS = ["sensor"]
REQUIRED_FILES = ["const.py", "manifest.json", "sensor.py"]
VERSION = "0.1.3"
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

DEFAULT_NAME = "ynab"
DEFAULT_BUDGET = "last-used"
DEFAULT_CURRENCY = "$"

ICON = "mdi:finance"

CONF_NAME = "name"
CONF_ENABLED = "enabled"
CONF_SENSOR = "sensor"
