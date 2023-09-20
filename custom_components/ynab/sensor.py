"""Sensor platform for ynab."""
import logging
from homeassistant.helpers.entity import Entity

from .const import ACCOUNT_ERROR, CATEGORY_ERROR, DOMAIN_DATA, ICON, CONF_ACCOUNTS_KEY, CONF_BUDGET_KEY, CONF_CATEGORIES_KEY, CONF_CURRENCY_KEY, CONF_BUDGET_NAME_KEY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, config_entry, async_add_entities
):
    """Set up sensor platform."""
    async_add_entities([ynabSensor(hass, config_entry.data)], True)


class ynabSensor(Entity):
    """YNAB Sensor class."""

    def __init__(self, hass, config):
        """Init."""
        self.hass = hass
        self.attr = {}
        self._state = None
        self._attr_unique_id = config[CONF_BUDGET_KEY]
        self._name = config[CONF_BUDGET_NAME_KEY]
        self._measurement = config[CONF_CURRENCY_KEY]
        self._categories = config[CONF_CATEGORIES_KEY]
        self._accounts = config[CONF_ACCOUNTS_KEY]

    async def async_update(self):
        """Update the sensor."""
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        to_be_budgeted = self.hass.data[DOMAIN_DATA].get("to_be_budgeted")

        if to_be_budgeted is not None:
            self._state = to_be_budgeted

        # set attributes
        self.attr["budgeted_this_month"] = self.hass.data[DOMAIN_DATA].get(
            "budgeted_this_month"
        )

        self.attr["activity_this_month"] = self.hass.data[DOMAIN_DATA].get(
            "activity_this_month"
        )
        self.attr["age_of_money"] = self.hass.data[DOMAIN_DATA].get("age_of_money")

        self.attr["total_balance"] = self.hass.data[DOMAIN_DATA].get("total_balance")

        self.attr["need_approval"] = self.hass.data[DOMAIN_DATA].get("need_approval")

        self.attr["uncleared_transactions"] = self.hass.data[DOMAIN_DATA].get(
            "uncleared_transactions"
        )

        self.attr["overspent_categories"] = self.hass.data[DOMAIN_DATA].get(
            "overspent_categories"
        )

        # category attributes
        if self._categories is not None:
            for category in self._categories:
                if self.hass.data[DOMAIN_DATA].get(category) is not None:
                    self.attr[category.replace(" ", "_").lower()] = self.hass.data[
                        DOMAIN_DATA
                    ].get(category)
                    self.attr[
                        (category + "_budgeted").replace(" ", "_").lower()
                    ] = self.hass.data[DOMAIN_DATA].get(category + "_budgeted")
                else:
                    category_error = CATEGORY_ERROR.format(category=category)
                    _LOGGER.error(category_error)

        if self._accounts is not None:
            for account in self._accounts:
                if self.hass.data[DOMAIN_DATA].get(account) is not None:
                    self.attr[account.replace(" ", "_").lower()] = self.hass.data[
                        DOMAIN_DATA
                    ].get(account)
                else:
                    account_error = ACCOUNT_ERROR.format(account=account)
                    _LOGGER.error(account_error)

    @property
    def should_poll(self):
        """Return the name of the sensor."""
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return self._measurement

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.attr
