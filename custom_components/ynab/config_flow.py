from homeassistant import config_entries
import logging
import voluptuous as vol
from .const import (
    CONF_ACCOUNTS_KEY,
    CONF_BUDGET_KEY,
    CONF_CATEGORIES_KEY,
    CONF_CURRENCY_KEY,
    DOMAIN
)
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.selector import selector
from ynab_sdk import YNAB

_LOGGER = logging.getLogger(__name__)

async def init_ynab_and_validate_api_key(hass, api_key: str) -> None:
    ynab = YNAB(api_key)

    await hass.async_add_executor_job(ynab.budgets.get_budgets)

    return ynab

class YnabConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    ynab: YNAB

    def __init__(self) -> None:
        super().__init__()
        self.ynab = None

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            _LOGGER.debug("Validating API Key")
            try:
                self.ynab = await init_ynab_and_validate_api_key(self.hass, user_input[CONF_API_KEY])
                self.data = {CONF_API_KEY: user_input[CONF_API_KEY]}
                return await self.async_step_budgets()
            except AssertionError:
                errors["base"] = "auth"

        data_schema = {
            vol.Required(CONF_API_KEY): str
        }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema), errors=errors)

    async def async_step_budgets(self, user_input=None):

        if user_input is not None:
            budget_id = user_input[CONF_BUDGET_KEY]
            self.data[CONF_BUDGET_KEY] = budget_id

            await self.async_set_unique_id(budget_id)
            self._abort_if_unique_id_configured()

            budget = (await self.hass.async_add_executor_job(self.ynab.budgets.get_budget, budget_id)).data.budget

            self.data["budget_name"] = budget.name
            self.data[CONF_CURRENCY_KEY] = budget.currency_format.currency_symbol
            return await self.async_step_categories()

        budgets_response = await self.hass.async_add_executor_job(self.ynab.budgets.get_budgets)

        data_schema = {
            vol.Required(CONF_BUDGET_KEY): selector({
                "select": {
                    "options": [{"label": budget.name, "value": budget.id} for budget in budgets_response.data.budgets],
                    "multiple": False
                }
            })
        }

        return self.async_show_form(step_id="budgets", data_schema=vol.Schema(data_schema))

    async def async_step_categories(self, user_input=None):
        if user_input is not None:
            if CONF_CATEGORIES_KEY in user_input:
                self.data[CONF_CATEGORIES_KEY] = user_input[CONF_CATEGORIES_KEY]
            else:
                self.data[CONF_CATEGORIES_KEY] = []

            return await self.async_step_accounts()

        categories_by_name = await self.fetch_categories()

        data_schema = {
            vol.Optional(CONF_CATEGORIES_KEY): selector({
                "select": {
                    "options": [{"label": name, "value": category.name} for name, category in categories_by_name.items()],
                    "multiple": True
                }
            })
        }

        return self.async_show_form(step_id="categories", data_schema=vol.Schema(data_schema))

    async def fetch_categories(self):
        categories_response = await self.hass.async_add_executor_job(self.ynab.categories.get_categories, self.data["budget"])
        categories_by_name = {}
        for category_group in categories_response.data.category_groups:
            if category_group.deleted is False and category_group.hidden is False and category_group.name != "Internal Master Category":
                for category in category_group.categories:
                    if category.deleted is False and category.hidden is False:
                        categories_by_name[category_group.name + " - " + category.name] = category

        return categories_by_name


    async def async_step_accounts(self, user_input=None):
        if user_input is not None:
            if CONF_ACCOUNTS_KEY in user_input:
                self.data[CONF_ACCOUNTS_KEY] = user_input[CONF_ACCOUNTS_KEY]
            else:
                self.data[CONF_ACCOUNTS_KEY] = []

            return self.async_create_entry(
                title=self.data["budget_name"],
                data=self.data
            )

        accounts_response = await self.hass.async_add_executor_job(self.ynab.accounts.get_accounts, self.data["budget"])

        data_schema = {
            vol.Optional(CONF_ACCOUNTS_KEY): selector({
                "select": {
                    "options": [{"label": account.name, "value": account.name} for account in accounts_response.data.accounts],
                    "multiple": True
                }
            })
        }

        return self.async_show_form(step_id="accounts", data_schema=vol.Schema(data_schema))