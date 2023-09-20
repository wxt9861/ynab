"""YNAB Integration."""

import json
import logging
import os
from datetime import date, timedelta

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from ynab_sdk import YNAB

from .const import (
    CONF_NAME,
    CONF_BUDGET_KEY,
    CONF_CATEGORIES_KEY,
    CONF_ACCOUNTS_KEY,

    DEFAULT_API_ENDPOINT,
    DOMAIN,
    DOMAIN_DATA,
    ISSUE_URL,
    REQUIRED_FILES,
    STARTUP,
    VERSION,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up this integration using config flow."""
    # startup message
    startup = STARTUP.format(name=DOMAIN, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(startup)

    # check all required files
    file_check = await check_files(hass)
    if not file_check:
        return False

    url_check = await check_url()
    if not url_check:
        return False

    # create data dictionary
    hass.data[DOMAIN_DATA] = {}

    # get global config
    budget = entry.data[CONF_BUDGET_KEY]
    _LOGGER.debug("YAML configured budget - %s", budget)

    if CONF_CATEGORIES_KEY in entry.data:
        categories = entry.data[CONF_CATEGORIES_KEY]
        _LOGGER.debug("Monitoring categories - %s", categories)

    if CONF_ACCOUNTS_KEY in entry.data:
        accounts = entry.data[CONF_ACCOUNTS_KEY]
        _LOGGER.debug("Monitoring accounts - %s", accounts)

    hass.data[DOMAIN_DATA]["client"] = YnabData(hass, entry)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True


class YnabData:
    """This class handles communication and data for YNAB integration."""

    def __init__(self, hass, entry):
        """Initialize the class."""
        self.hass = hass
        self.api_key = entry.data[CONF_API_KEY]
        self.budget = entry.data[CONF_BUDGET_KEY]
        self.categories = entry.data[CONF_CATEGORIES_KEY]
        self.accounts = entry.data[CONF_ACCOUNTS_KEY]

        self.ynab = None
        self.all_budgets = None
        self.get_all_budgets = None
        self.raw_budget = None
        self.get_data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """Update data."""

        # setup YNAB API
        await self.request_import()

        self.ynab = YNAB(self.api_key)
        self.all_budgets = await self.hass.async_add_executor_job(
            self.ynab.budgets.get_budgets
        )
        self.raw_budget = await self.hass.async_add_executor_job(
            self.ynab.budgets.get_budget, self.budget
        )

        # get budget summary
        self.get_all_budgets = self.all_budgets.data.budgets
        if self.get_all_budgets:
            _LOGGER.debug("Found %s budgets", len(self.get_all_budgets))
            for budget in self.get_all_budgets:
                _LOGGER.debug("Budget name: %s - id: %s", budget.name, budget.id)
        else:
            _LOGGER.errors("Unable to retrieve budgets summary")

        self.get_data = self.raw_budget.data.budget
        _LOGGER.debug("Retrieving data from budget id: %s", self.get_data.id)

        # get to be budgeted data
        self.hass.data[DOMAIN_DATA]["to_be_budgeted"] = (
            self.get_data.months[0].to_be_budgeted / 1000
        )
        _LOGGER.debug(
            "Received data for: to be budgeted: %s",
            (self.get_data.months[0].to_be_budgeted / 1000),
        )

        # get unapproved transactions
        unapproved_transactions = len(
            [
                transaction.amount
                for transaction in self.get_data.transactions
                if transaction.approved is not True
            ]
        )
        self.hass.data[DOMAIN_DATA]["need_approval"] = unapproved_transactions
        _LOGGER.debug(
            "Received data for: unapproved transactions: %s",
            unapproved_transactions,
        )

        # get number of uncleared transactions
        uncleared_transactions = len(
            [
                transaction.amount
                for transaction in self.get_data.transactions
                if transaction.cleared == "uncleared"
            ]
        )
        self.hass.data[DOMAIN_DATA]["uncleared_transactions"] = uncleared_transactions
        _LOGGER.debug(
            "Received data for: uncleared transactions: %s", uncleared_transactions
        )

        total_balance = 0
        # get account data
        for account in self.get_data.accounts:
            if account.on_budget:
                total_balance += account.balance

        # get to be budgeted data
        self.hass.data[DOMAIN_DATA]["total_balance"] = total_balance / 1000
        _LOGGER.debug(
            "Received data for: total balance: %s",
            (self.hass.data[DOMAIN_DATA]["total_balance"]),
        )

        # get accounts
        for account in self.get_data.accounts:
            if account.name not in self.accounts:
                continue

            self.hass.data[DOMAIN_DATA].update([(account.name, account.balance / 1000)])
            _LOGGER.debug(
                "Received data for account: %s",
                [account.name, account.balance / 1000],
            )

        # get current month data
        for month in self.get_data.months:
            if month.month != date.today().strftime("%Y-%m-01"):
                continue

            # budgeted
            self.hass.data[DOMAIN_DATA]["budgeted_this_month"] = month.budgeted / 1000
            _LOGGER.debug(
                "Received data for: budgeted this month: %s",
                self.hass.data[DOMAIN_DATA]["budgeted_this_month"],
            )

            # activity
            self.hass.data[DOMAIN_DATA]["activity_this_month"] = month.activity / 1000
            _LOGGER.debug(
                "Received data for: activity this month: %s",
                self.hass.data[DOMAIN_DATA]["activity_this_month"],
            )

            # get age of money
            self.hass.data[DOMAIN_DATA]["age_of_money"] = month.age_of_money
            _LOGGER.debug(
                "Received data for: age of money: %s",
                self.hass.data[DOMAIN_DATA]["age_of_money"],
            )

            # get number of overspend categories
            overspent_categories = len(
                [
                    category.balance
                    for category in month.categories
                    if category.balance < 0
                ]
            )
            self.hass.data[DOMAIN_DATA]["overspent_categories"] = overspent_categories
            _LOGGER.debug(
                "Received data for: overspent categories: %s",
                overspent_categories,
            )

            # get remaining category balances
            for category in month.categories:
                if category.name not in self.categories:
                    continue

                self.hass.data[DOMAIN_DATA].update(
                    [(category.name, category.balance / 1000)]
                )
                self.hass.data[DOMAIN_DATA].update(
                    [(category.name + "_budgeted", category.budgeted / 1000)]
                )
                _LOGGER.debug(
                    "Received data for categories: %s",
                    [category.name, category.balance / 1000, category.budgeted / 1000],
                )

    async def request_import(self):
        """Force transaction import."""

        import_endpoint = (
            f"{DEFAULT_API_ENDPOINT}/budgets/{self.budget}/transactions/import"
        )
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url=import_endpoint) as response:
                    if response.status in [200, 201]:
                        response_data = json.loads(await response.text())

                        _LOGGER.debug(
                            "Imported transactions: %s",
                            len(response_data["data"]["transaction_ids"]),
                        )
                        _LOGGER.debug("API Stats: %s", response.headers["X-Rate-Limit"])

                        if len(response_data["data"]["transaction_ids"]) > 0:
                            _event_topic = DOMAIN + "_event"
                            _event_data = {
                                "transactions_imported": len(
                                    response_data["data"]["transaction_ids"]
                                )
                            }
                            self.hass.bus.async_fire(_event_topic, _event_data)

        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.debug("Error encounted during forced import - %s", error)


async def check_files(hass):
    """Return bool that indicates if all files are present."""
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = f"{base}{file}"
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def check_url():
    """Return bool that indicates YNAB URL is accessible."""

    url = DEFAULT_API_ENDPOINT

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    _LOGGER.debug("Connection with YNAB established")
                    result = True
                else:
                    _LOGGER.debug(
                        "Connection with YNAB established, "
                        "but wasnt able to communicate with API endpoint"
                    )
                    result = False
    except Exception as error:  # pylint: disable=broad-except
        _LOGGER.debug("Unable to establish connection with YNAB - %s", error)
        result = False

    return result
