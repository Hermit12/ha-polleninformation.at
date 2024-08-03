"""Constants for the Polleninformation.at integration."""

DOMAIN = "polleninformation_at"
CONF_API_URL = "api_url"
DEFAULT_API_URL = "https://www.polleninformation.at/index.php?eID=appinterface&pure_json=1&lang_code=de&lang_id=0&action=getFullContaminationData&type=gps&value[latitude]=48.223249&value[longitude]=16.335907&country_id=1&personal_contamination=false&sensitivity=0&country=AT&sessionid="

SENSOR_TYPES = {
    "pollen": "Pollen",
    "air_quality": "Luftqualität",
    "nitrogen_dioxide": "Stickstoffdioxid",
    "ozone": "Ozon",
    "particulate_matter": "Feinstaub",
    "sulphur_dioxide": "Schwefeldioxid",
    "temperature": "Temperatur",
    "allergy_risk": "Allergierisiko",
}