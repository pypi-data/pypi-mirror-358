"""
FastAPI application to serve data for a specific observation.

This application provides endpoints to retrieve data for a specific observation
based on site, date, observation number, telescope type, and telescope ID.
"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_OB_DATE_MAP_PATH = "data/v1/ob_date_map.json"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_ob_date_map(file_path=None):
    """
    Load a mapping of observation dates from a JSON file.

    Parameters
    ----------
    file_path : str || None
        The path to the JSON file containing the observation date map (for test
        purposing). If None, uses the default path specified by
        DEFAULT_OB_DATE_MAP_PATH.

    Returns
    -------
    dict
        The loaded dictionary mapping observation dates to their associated
        Observation Blocks, if successful. An error dictionary with an "error"
        key if the file is not found or an exception occurs.
    """
    file_path = file_path or DEFAULT_OB_DATE_MAP_PATH
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": str(e)}


@app.get("/v1/ob_date_map")
def get_ob_date_map():
    """Get the observation date map.

    Returns
    -------
    dict
        A dictionary mapping observation dates to their associated Observation
        Blocks, as returned by `load_ob_data_map()`.
    """
    return load_ob_date_map()


@app.get("/v1/data")
def get_data(
    site: str,
    date: str,
    ob: int,
    telescope_type: str,
    telescope_id: int,
):
    """
    Retrieve data for a specific observation and telescope.

    Parameters
    ----------
    site : str
        The site identifier (e.g., 'North', 'South').
    date : str
        The observation date in 'YYYYMMDD' format.
    ob : int
        The observation block number.
    telescope_type : str
        The type of telescope ('LST', 'MST', or 'SST').
    telescope_id : int
        The unique identifier for the telescope.

    Returns
    -------
    dict
        The data loaded from the corresponding JSON file for the specified observation.

    Raises
    ------
    HTTPException
        If the telescope type is invalid, the data file does not exist, or an
        error occurs while reading the file.
    """
    # Validate telescope type
    if telescope_type not in {"LST", "MST", "SST"}:
        raise HTTPException(status_code=400, detail="Invalid telescope type")

    file_path = f"data/v1/{site}/{date}_OB{ob}_{telescope_type}_{telescope_id}.json"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, detail=f"Data file '{file_path}' not found"
        )
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
