"""Adds config flow for YNAB."""

import logging
from collections import OrderedDict

import voluptuous as vol

from homeassistant import config_entries
# from homeassistant.helpers import aiohttp_client

from .const import DOMAIN
from ynab_sdk import YNAB

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class YNABlowHandler(config_entries.ConfigFlow):
    """Config flow for YNAB."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input={}):
        """Handle a flow initialized by the user."""
        self._errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_communication(user_input["api_key"])
            if valid:
                return self.async_create_entry(title="ynab", data=user_input)
            else:
                self._errors["base"] = "communication"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        # Defaults
        api_key = ""
        budget = "last-used"
        currency = "$"
        categories = ""

        if user_input is not None:
            if "api_key" in user_input:
                api_key = user_input["api_key"]
            if "budget" in user_input:
                budget = user_input["budget"]
            if "currency" in user_input:
                currency = user_input["currency"]
            if "categories" in user_input:
                categories = user_input["categories"]

        data_schema = OrderedDict()
        data_schema[vol.Required("api_key", default=api_key)] = str
        data_schema[vol.Optional("budget", default=budget)] = str
        data_schema[vol.Optional("currency", default=currency)] = str
        data_schema[vol.Optional("categories", default=categories)] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):
        """Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def _test_communication(self, api_key):
        """Return true if the communication is ok."""
        try:
            conn = YNAB(api_key)
            _LOGGER.debug(conn)

            return True
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(exception)
            return False
