"""YNAB Integration."""

import logging
import os
from datetime import timedelta, datetime, date
from ynab_sdk import YNAB

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import discovery
from homeassistant.util import Throttle

import voluptuous as vol

from .const import (
    CONF_NAME,
    DEFAULT_NAME,
    DEFAULT_BUDGET,
    DEFAULT_CURRENCY,
    DOMAIN,
    DOMAIN_DATA,
    ISSUE_URL,
    PLATFORMS,
    REQUIRED_FILES,
    STARTUP,
    VERSION,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional("budget", default=DEFAULT_BUDGET): cv.string,
                vol.Optional("currency", default=DEFAULT_CURRENCY): cv.string,
                vol.Optional("categories", default=None): vol.All(cv.ensure_list),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    # startup message
    startup = STARTUP.format(name=DOMAIN, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(startup)

    # check all required files
    file_check = await check_files(hass)
    if not file_check:
        return False

    # create data dictionary
    hass.data[DOMAIN_DATA] = {}

    # get global config
    budget = config[DOMAIN].get("budget")
    _LOGGER.debug("Using budget - %s", budget)

    if config[DOMAIN].get("categories") is not None:
        categories = config[DOMAIN].get("categories")
        _LOGGER.debug("Monitoring categories - %s", categories)

    hass.data[DOMAIN_DATA]["client"] = ynabData(hass, config)

    # load platforms
    for platform in PLATFORMS:
        # get platform specific configuration
        platform_config = config[DOMAIN]

        hass.async_create_task(
            discovery.async_load_platform(
                hass, platform, DOMAIN, platform_config, config
            )
        )

    return True


class ynabData:
    def __init__(self, hass, config):
        """Initialize the class."""
        self.hass = hass
        self.api_key = config[DOMAIN].get(CONF_API_KEY)
        self.budget = config[DOMAIN].get("budget")
        self.categories = config[DOMAIN].get("categories")

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """Update data."""
        try:
            # setup YNAB API
            self.ynab = YNAB(self.api_key)
            self.get_data = self.ynab.budgets.get_budget(self.budget).data.budget

            # get to be budgeted data
            self.hass.data[DOMAIN_DATA]["to_be_budgeted"] = (
                self.get_data.months[0].to_be_budgeted / 1000
            )
            _LOGGER.debug(
                "Recieved data for: to be budgeted: %s",
                (self.get_data.months[0].to_be_budgeted / 1000),
            )

            # get unapproved transactions
            unapproved_transactions = len(
                [t.amount for t in self.get_data.transactions if t.approved != True]
            )
            self.hass.data[DOMAIN_DATA]["need_approval"] = unapproved_transactions
            _LOGGER.debug(
                "Recieved data for: unapproved transactions: %s",
                unapproved_transactions,
            )

            # get number of uncleared transactions
            uncleared_transactions = len(
                [
                    t.amount
                    for t in self.get_data.transactions
                    if t.cleared == "uncleared"
                ]
            )
            self.hass.data[DOMAIN_DATA][
                "uncleared_transactions"
            ] = uncleared_transactions
            _LOGGER.debug(
                "Recieved data for: uncleared transactions: %s", uncleared_transactions
            )

            # get current month data
            for m in self.get_data.months:
                if m.month != date.today().strftime("%Y-%m-01"):
                    continue
                else:
                    self.hass.data[DOMAIN_DATA]["budgeted_this_month"] = (
                        m.budgeted / 1000
                    )
                    _LOGGER.debug(
                        "Recieved data for: budgeted this month: %s",
                        self.hass.data[DOMAIN_DATA]["budgeted_this_month"],
                    )

                    # get number of overspend categories
                    overspent_categories = len(
                        [c.balance for c in m.categories if c.balance < 0]
                    )
                    self.hass.data[DOMAIN_DATA][
                        "overspent_categories"
                    ] = overspent_categories
                    _LOGGER.debug(
                        "Recieved data for: overspent categories: %s",
                        overspent_categories,
                    )

                    # get remaining category balances
                    for c in m.categories:
                        if c.name not in self.categories:
                            continue
                        else:
                            self.hass.data[DOMAIN_DATA].update(
                                [(c.name, c.balance / 1000)]
                            )
                            _LOGGER.debug(
                                "Recieved data for categories: %s",
                                [c.name, c.balance / 1000],
                            )

            # print(self.hass.data[DOMAIN_DATA])
        except Exception as error:
            _LOGGER.error("Could not retrieve data - verify API key %s", error)


async def check_files(hass):
    """Return bool that indicates if all files are present."""
    base = "{}/custom_components/{}/".format(hass.config.path(), DOMAIN)
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue
