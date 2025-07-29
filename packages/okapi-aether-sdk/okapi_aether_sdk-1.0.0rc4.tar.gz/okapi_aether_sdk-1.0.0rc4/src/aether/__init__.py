import logging

from aether.aether_api import AetherApi
from aether.aether_satellites_api import AetherSatellitesApi
from aether.aether_sensors_api import AetherSensorsApi
from aether.aether_services_api import AetherServicesApi

__all__ = [
    "AetherApi",
    "AetherSatellitesApi",
    "AetherSensorsApi",
    "AetherServicesApi"
]
# Add a default null handler
logging.getLogger(__name__).addHandler(logging.NullHandler())