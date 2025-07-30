from datetime import datetime, date, timezone
from http import HTTPStatus
from typing import List, Type, TypeVar, Dict, Callable
from typing import Optional

import requests
import urllib3
from pydantic import BaseModel, Field, ConfigDict
from pydantic import model_validator

from vito.sas.air import logger
from vito.sas.air.api_client import RESTclient

T = TypeVar('T')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IssepLocation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    id_reseau: int = Field(alias="idReseau")
    id_configuration: int = Field(alias="idConfiguration")
    user_id: Optional[int] = Field(alias="userId")

    nom: str  # Name of the station

    attrib_start: Optional[datetime] = Field(alias="attribStart")
    attrib_end: Optional[datetime] = Field(alias="attribEnd")

    x: float  # X coordinate in EPSG:31370
    y: float  # Y coordinate in EPSG:31370

    longitude: Optional[float] = Field(alias="lon")
    latitude: Optional[float] = Field(alias="lat")
    altitude: Optional[float] = None  # Altitude in meters
    h: Optional[float] = None  # Height in meters (if applicable)

    @model_validator(mode="after")
    def validate_after(self) -> 'IssepLocation':
        if isinstance(self.attrib_start, datetime) and self.attrib_start.tzinfo is None:
            self.attrib_start = self.attrib_start.replace(tzinfo=timezone.utc)
        if isinstance(self.attrib_end, datetime) and self.attrib_end.tzinfo is None:
            self.attrib_end = self.attrib_end.replace(tzinfo=timezone.utc)
        # TODO compute latitude and longitude from x and y if not provided
        if self.longitude is None or self.latitude is None:
            if self.x is not None and self.y is not None:
                # Convert EPSG:31370 to EPSG:4326
                from pyproj import Transformer
                transformer = Transformer.from_crs("EPSG:31370", "EPSG:4326", always_xy=True)
                self.longitude, self.latitude = transformer.transform(self.x, self.y)
        return self

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"IssepLocation (Id: {self.id}, IdReseau: {self.id_reseau}, IdConfiguration: {self.id_configuration},  Nom: {self.nom}, Lat: {self.latitude}, Lon: {self.longitude})"


class IssepMeasurement(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    moment: datetime
    id_configuration: int = Field(alias="idConfiguration")

    id_reseau: Optional[int] = Field(alias="idReseau", default=None)
    user_id: Optional[int] = Field(alias="userId", default=None)

    # Gas measurements
    co: Optional[float] = None
    no: Optional[float] = None
    no2: Optional[float] = None
    o3no2: Optional[float] = None

    # PPB measurements
    ppb_no: Optional[float] = Field(alias="ppbno", default=None)
    ppb_no_statut: Optional[int] = Field(alias="ppbnoStatut", default=None)
    ppb_no2: Optional[float] = Field(alias="ppbno2", default=None)
    ppb_no2_statut: Optional[int] = Field(alias="ppbno2Statut", default=None)
    ppb_o3: Optional[float] = Field(alias="ppbo3", default=None)
    ppb_o3_statut: Optional[int] = Field(alias="ppbo3Statut", default=None)

    # µg/m³ measurements
    ugpcm_no: Optional[float] = Field(alias="ugpcmno", default=None)
    ugpcm_no_statut: Optional[int] = Field(alias="ugpcmnoStatut", default=None)
    ugpcm_no2: Optional[float] = Field(alias="ugpcmno2", default=None)
    ugpcm_no2_statut: Optional[int] = Field(alias="ugpcmno2Statut", default=None)
    ugpcm_o3: Optional[float] = Field(alias="ugpcmo3", default=None)
    ugpcm_o3_statut: Optional[int] = Field(alias="ugpcmo3Statut", default=None)

    # BME sensor measurements (Temperature, Pressure, Humidity)
    bme_temperature: Optional[float] = Field(alias="bmeT", default=None)
    bme_temperature_statut: Optional[int] = Field(alias="bmeTStatut", default=None)
    bme_pressure: Optional[float] = Field(alias="bmePres", default=None)
    bme_pressure_statut: Optional[int] = Field(alias="bmePresStatut", default=None)
    bme_humidity: Optional[float] = Field(alias="bmeRh", default=None)
    bme_humidity_statut: Optional[int] = Field(alias="bmeRhStatut", default=None)

    # Particulate matter measurements
    pm1: Optional[float] = None
    pm1_statut: Optional[int] = Field(alias="pm1Statut", default=None)
    pm25: Optional[float] = None
    pm25_statut: Optional[int] = Field(alias="pm25Statut", default=None)
    pm4: Optional[float] = None
    pm4_statut: Optional[int] = Field(alias="pm4Statut", default=None)
    pm10: Optional[float] = None
    pm10_statut: Optional[int] = Field(alias="pm10Statut", default=None)

    # Battery and power measurements
    vbat: Optional[float] = None
    vbat_statut: Optional[int] = Field(alias="vbatStatut", default=None)
    mwh_bat: Optional[float] = Field(alias="mwhBat", default=None)
    mwh_pv: Optional[float] = Field(alias="mwhPv", default=None)

    # RF measurements
    co_rf: Optional[float] = Field(alias="coRf", default=None)
    no_rf: Optional[float] = Field(alias="noRf", default=None)
    no2_rf: Optional[float] = Field(alias="no2Rf", default=None)
    o3no2_rf: Optional[float] = Field(alias="o3no2Rf", default=None)
    o3_rf: Optional[float] = Field(alias="o3Rf", default=None)
    pm10_rf: Optional[float] = Field(alias="pm10Rf", default=None)

    @model_validator(mode="after")
    def validate_after(self) -> 'IssepMeasurement':
        if isinstance(self.moment, datetime) and self.moment.tzinfo is None:
            self.moment = self.moment.replace(tzinfo=timezone.utc)
        return self

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"IssepMeasurement (IdConfiguration: {self.id_configuration}, Moment: {self.moment}, IdReseau: {self.id_reseau}, UserId: {self.user_id})"


class IssepAirClient(RESTclient):
    """
    Client for the ISSEP AIR API:   https://opendata.issep.be/env/air/api
    """

    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None, token: Optional[str | Callable] = None):
        """
        Initialize the client.

        Args:
            base_url: The base URL of the SOS API. Defaults to "https://opendata.issep.be/env/air/api"
            session: The requests session to use. If None, a new session will be created.
        """
        super().__init__(base_url or "https://opendata.issep.be/env/air/api", session)
        self.token = token
        logger.info(f"Initialized IssepAirClient with base URL: {self.base_url}")


    def parse_list_response(self, response: requests.Response, model: Type[T]) -> List[T]:
        """
        Parses a list response into a List of the specified model.
        """
        try:
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.exception(response.text)
            response.raise_for_status()
            return [model(**item) for item in response.json()]
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e} | URL: {response.url}")
            raise
        except Exception as e:
            logger.error(f"List response parsing failed: {e} | Response: {response.text}")
            raise


    def parse_typed_response(self, response: requests.Response, model: Type[T]) -> T:
        """
        Parses a single response into the specified model.
        """
        try:
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.exception(response.text)
            response.raise_for_status()
            response_object = response.json()

            if isinstance(response_object, model):
                return response_object
            return model(**response_object)
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e} | URL: {response.url}")
            raise
        except Exception as e:
            logger.error(f"Response parsing failed: {e} | Response: {response.text}")
            raise

    # https://opendata.issep.be/env/air/api/microsensor/camsncpbe/locations
    def get_locations(self) -> List[IssepLocation]:
        logger.info("Getting available stations")
        full_url = self._build_url( "microsensor", "camsncpbe", "locations")
        response = self._exec_get(full_url)
        return self.parse_list_response(response, model=IssepLocation)

    # https://opendata.issep.be/env/air/api/microsensor/camsncpbe/lastdata
    def get_last_measurements(self) -> List[IssepMeasurement]:
        logger.info("Getting available stations")
        full_url = self._build_url( "microsensor", "camsncpbe", "lastdata")
        response = self._exec_get(full_url)
        return self.parse_list_response(response, model=IssepMeasurement)

    # https://opendata.issep.be/env/air/api/microsensor/config/10324/start/2025-06-23/end/2025-06-27
    def get_measurements(self, id_configuration: int, start_date: date, end_date: date) -> List[IssepMeasurement]:
        logger.info("Getting available stations")
        start_date_str: str = start_date.isoformat()
        end_date_str: str = end_date.isoformat()
        full_url = self._build_url( "microsensor", "config", str(id_configuration), "start", start_date_str, "end", end_date_str)
        response = self._exec_get(full_url)
        return self.parse_list_response(response, model=IssepMeasurement)

    def _base_headers(self) -> Dict[str, str]:
        """Get base headers for API requests"""
        token_str = None
        if isinstance(self.token, Callable):
            token_str = self.token()
        elif isinstance(self.token, str):
            token_str = self.token
        if token_str is not None:
            return {
                "Accept": "application/json",
                "Authorization": f"Bearer {token_str}"
            }
        else:
            return {
                "Accept": "application/json"
            }
