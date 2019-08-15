"""Sensor platform for ynab."""
import logging
from homeassistant.helpers.entity import Entity

from .const import CATEGORY_ERROR, DOMAIN, DOMAIN_DATA, ICON

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([ynabSensor(hass, discovery_info)], True)


class ynabSensor(Entity):
    """YNAB Sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._state = None
        self._name = config["name"]
        self._measurement = config["currency"]
        self._categories = config["categories"]

    async def async_update(self):
        """Update the sensor."""
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        to_be_budgeted = self.hass.data[DOMAIN_DATA].get("to_be_budgeted")

        if to_be_budgeted is None:
            self._state = self._state
        else:
            self._state = to_be_budgeted

        # set attributes
        self.attr["budgeted_this_month"] = self.hass.data[DOMAIN_DATA].get(
            "budgeted_this_month"
        )

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
                else:
                    category_error = CATEGORY_ERROR.format(category=category)
                    _LOGGER.error(category_error)

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
        return self._measurement

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
