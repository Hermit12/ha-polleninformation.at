from datetime import timedelta
from typing import Any, Dict, Optional
import html
import logging

import aiohttp
import async_timeout

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    UnitOfTemperature,
)

from .const import DOMAIN, CONF_API_URL, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

class PollenCoordinator(DataUpdateCoordinator):
    """Pollen data update coordinator."""

    def __init__(self, hass: HomeAssistant, api_url: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(hours=1),
        )
        self.api_url = api_url

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    _LOGGER.debug(f"Fetching data from API: {self.api_url}")
                    async with session.get(self.api_url) as response:
                        data = await response.json()
                        _LOGGER.debug(f"Received data from API: {data}")

            if data["success"] != 1:
                _LOGGER.error(f"Error fetching pollen data: {data}")
                raise UpdateFailed("Error fetching pollen data")

            result = data["result"]
            forecast_text = result.get("forecastText", {})
            
            processed_data = {
                "pollen_data": result.get("contamination", []),
                "forecast_text_title": forecast_text.get("title", ""),
                "forecast_text_description": html.unescape(forecast_text.get("description", "")),
                "forecast_text_date": result.get("contamination_date_1", ""),
                "additional_data": result.get("additionalForecastData", [{}])[0],
            }
            _LOGGER.debug(f"Processed data: {processed_data}")
            return processed_data
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    api_url = entry.data[CONF_API_URL]
    selected_sensors = entry.data["sensors"]

    coordinator = PollenCoordinator(hass, api_url)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    if "pollen" in selected_sensors:
        for pollen in coordinator.data["pollen_data"]:
            sensors.append(PollenSensor(coordinator, pollen["poll_title"]))

    if "air_quality" in selected_sensors:
        sensors.append(AirQualitySensor(coordinator, "air_quality", "Luftqualität", "mdi:air-filter"))
    if "nitrogen_dioxide" in selected_sensors:
        sensors.append(AirQualitySensor(coordinator, "nitrogen_dioxide", "Stickstoffdioxid", "mdi:molecule", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER))
    if "ozone" in selected_sensors:
        sensors.append(AirQualitySensor(coordinator, "ozone", "Ozon", "mdi:cloud", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER))
    if "particulate_matter" in selected_sensors:
        sensors.append(AirQualitySensor(coordinator, "particulate_matter", "Feinstaub", "mdi:grain", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER))
    if "sulphur_dioxide" in selected_sensors:
        sensors.append(AirQualitySensor(coordinator, "sulphur_dioxide", "Schwefeldioxid", "mdi:smog", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER))
    if "temperature" in selected_sensors:
        sensors.append(AirQualitySensor(coordinator, "temperature", "Temperatur", "mdi:thermometer", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT))
    if "allergy_risk" in selected_sensors:
        sensors.append(AllergyRiskSensor(coordinator))

    sensors.append(DailyMessageSensor(coordinator))

    async_add_entities(sensors)

class PollenSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Pollen Sensor."""

    def __init__(self, coordinator: PollenCoordinator, pollen_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._pollen_type = pollen_type
        self._attr_name = f"Pollen {pollen_type}"
        self._attr_unique_id = f"pollen_{pollen_type.lower().replace(' ', '_')}"
        self._attr_icon = "mdi:flower-pollen"

    @property
    def state(self):
        """Return the state of the sensor."""
        for pollen in self.coordinator.data["pollen_data"]:
            if pollen["poll_title"] == self._pollen_type:
                return get_contamination_level(pollen["contamination_1"])
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        for pollen in self.coordinator.data["pollen_data"]:
            if pollen["poll_title"] == self._pollen_type:
                contamination_level = get_contamination_level(pollen["contamination_1"])
                return {
                    "contamination_value": pollen["contamination_1"],
                    "poll_image": pollen["poll_image"],
                    "is_keine": contamination_level == "keine",
                    "is_massig": contamination_level == "mäßig",
                    "is_hoch": contamination_level == "hoch",
                    "is_sehr_hoch": contamination_level == "sehr hoch",
                }
        return {}

class AirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of an Air Quality Sensor."""

    def __init__(self, coordinator: PollenCoordinator, sensor_type: str, name: str, icon: str, unit: str | None = None, device_class: str | None = None, state_class: str | None = None) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"air_quality_{sensor_type}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data["additional_data"].get(self._sensor_type)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        state_value = self.state
        return {
            "is_keine": state_value == 0,
            "is_massig": 0 < state_value <= 1 if state_value is not None else False,
            "is_hoch": 1 < state_value <= 2 if state_value is not None else False,
            "is_sehr_hoch": state_value > 2 if state_value is not None else False,
        }

class AllergyRiskSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Allergy Risk Sensor."""

    def __init__(self, coordinator: PollenCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Allergierisiko"
        self._attr_unique_id = "allergy_risk"
        self._attr_icon = "mdi:alert"

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data["additional_data"]
        summe = sum(data.get(key, 0) for key in ["air_quality", "dayrisk", "asthma_weather", "nitrogen_dioxide", "ozone", "particulate_matter", "sulphur_dioxide"])
        return round(summe / 7)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {
            key: self.coordinator.data["additional_data"].get(key)
            for key in ["air_quality", "dayrisk", "asthma_weather", "nitrogen_dioxide", "ozone", "particulate_matter", "sulphur_dioxide", "temperature"]
        }
        state_value = self.state
        attributes.update({
            "is_keine": state_value == 0,
            "is_massig": 0 < state_value <= 1,
            "is_hoch": 1 < state_value <= 2,
            "is_sehr_hoch": state_value > 2,
        })
        return attributes

class DailyMessageSensor(CoordinatorEntity, SensorEntity):
    """Representation of the Daily Message Sensor."""

    def __init__(self, coordinator: PollenCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Tägliche Pollennachricht"
        self._attr_unique_id = "daily_pollen_message"
        self._attr_icon = "mdi:message-text"

    @property
    def state(self):
        """Return the state of the sensor."""
        return "Verfügbar" if self.coordinator.data.get("forecast_text_description") else "Nicht verfügbar"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "title": self.coordinator.data.get("forecast_text_title", ""),
            "date": self.coordinator.data.get("forecast_text_date", ""),
            "message": self.coordinator.data.get("forecast_text_description", "Keine Nachricht verfügbar"),
        }

def get_contamination_level(value):
    if value == 0:
        return "keine"
    elif value <= 1:
        return "mäßig"
    elif value <= 2:
        return "hoch"
    else:
        return "sehr hoch"