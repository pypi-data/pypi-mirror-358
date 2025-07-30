from datetime import date
from enum import Enum
from pathlib import Path
from typing import List

from vito.sas.air import logger


class Pollutant(str, Enum):
    """Enum for pollutant types with string values"""
    NO2 = "NO2"
    PM10 = "PM10"
    PM25 = "PM25"
    O3 = "O3"

    @classmethod
    def all(cls) -> List[str]:
        """Return all available pollutant types"""
        return [member.value for member in cls]


# Map pollutant names to CAMS variable names
POLLUTANT_MAP = {
    Pollutant.NO2: "nitrogen_dioxide",
    Pollutant.PM10: "particulate_matter_10um",
    Pollutant.PM25: "particulate_matter_2.5um",
    Pollutant.O3: "ozone"
}

def to_cams_conc_var(pollutant: str) -> str:
    """
    Get the CAMS variable name for a given pollutant.
    """
    cams_var_mapping = {
        "pm10": "pm10_conc",
        "pm25": "pm2p5_conc",
        "no2": "no2_conc",
        "o3": "o3_conc",
        # Add more mappings as needed
    }
    return cams_var_mapping.get(pollutant.lower(), pollutant.lower() + "_conc")


def to_cams_variable(pollutant: str) -> str:
    """
    Convert pollutant name to CAMS variable name

    Args:
        pollutant (str): Pollutant name (case-insensitive)

    Returns:
        str: CAMS variable name

    Raises:
        ValueError: If pollutant is not supported
    """
    try:
        # Handle case where pollutant is passed as Enum or string
        if isinstance(pollutant, Pollutant):
            return POLLUTANT_MAP[pollutant]
        return POLLUTANT_MAP[Pollutant(pollutant.upper())]
    except (KeyError, ValueError):
        valid_pollutants = ", ".join(Pollutant.all())
        raise ValueError(f"Unsupported pollutant: {pollutant}. Valid options are: {valid_pollutants}")


def crop_to_extent(cams_nc_file_in: Path, cams_nc_file_out: Path,
                   lon_min: float, lon_max: float, lat_min: float, lat_max: float, engine="netcdf4"):
    """
    Crop a CAMS netCDF file to a specified extent.
    Args:
        cams_nc_file_in (Path): Input netCDF file path
        cams_nc_file_out (Path): Output (cropped) netCDF file path (Overwrites if exists)
        lon_min (float): Minimum longitude
        lon_max (float): Maximum longitude
        lat_min (float): Minimum latitude
        lat_max (float): Maximum latitude

    Returns:
        None
    """
    import xarray as xr
    with xr.open_dataset(str(cams_nc_file_in), engine=engine, decode_timedelta=False) as xr_ds:
        xr_ds = xr_ds.assign_coords({"longitude": (((xr_ds.longitude + 180) % 360) - 180)})

        # find the closest lat/lon values in the dataset
        min_lon = xr_ds.longitude.sel(longitude=lon_min, method='bfill').values
        max_lon = xr_ds.longitude.sel(longitude=lon_max, method='ffill').values

        min_lat = xr_ds.latitude.sel(latitude=lat_min, method='ffill').values
        max_lat = xr_ds.latitude.sel(latitude=lat_max, method='bfill').values

        cropped_dataset = xr_ds.sel(
            latitude=slice(max_lat, min_lat),
            longitude=slice(min_lon, max_lon)
        )

        # write the cropped dataset to a new nc file
        # output_file = cams_file.parent / f"{cams_file.stem}_cropped.nc"
        cams_nc_file_out.parent.mkdir(parents=True, exist_ok=True)
        if cams_nc_file_out.exists():
            logger.warning(f"File {cams_nc_file_out.name} already exists. Overwriting...")

        cropped_dataset.to_netcdf(str(cams_nc_file_out))


def _load_dataset(nc_file: Path) :
    """
    Load a netCDF file into an xarray Dataset.

    Args:
        nc_file (Path): Path to the netCDF file

    Returns:
        xarray.Dataset: Loaded dataset
    """
    import xarray as xr
    try:
        return xr.load_dataset(nc_file, engine='h5netcdf', decode_timedelta=False)
    except Exception as e:
        logger.warning(f"Failed to load netCDF file {nc_file} with 'h5netcdf engine': {e}")
        logger.info("Trying to load with 'netcdf4 engine' instead.")
        return xr.load_dataset(nc_file, engine='netcdf4', decode_timedelta=False)

def cams_data_complete(cams_nc_file: Path, date_start: date, date_end: date) -> bool:
    """
    Check if the netcdf file is complete (all data variables are present)

    Arguments:
        cams_nc_file (Path): Path to the netcdf file
        date_start (date): Start date of the data
        date_end (date): End date of the data

    Returns:
        True if the file is complete (data for the last 96 hours is available), False otherwise

    Raises:
        Exception: If the date range is invalid (less than 1 day)

    """
    import numpy as np

    delta_days = (date_end - date_start).days
    if delta_days < 1:
        raise Exception(f"Invalid date range: {date_start} -> {date_end}")

    expected_range_hours = delta_days * 24

    ds = _load_dataset(cams_nc_file)

    # ds = ds.assign_coords({"longitude": (((ds.longitude + 180) % 360) - 180)})

    time_arr = ds.time.values
    if len(time_arr) < expected_range_hours:
        return False
    try:
        var_name = list(ds.data_vars)[0]
        # Compute the mean over time, latitude and longitude
        avg = ds.isel(time=slice(-24, None))[var_name].mean(dim=["time", "latitude", "longitude"]).values
        # return true if avg is a real number
        is_real: List[bool] = list(np.isreal(avg))
        return is_real[0]
    except Exception:
        return False

