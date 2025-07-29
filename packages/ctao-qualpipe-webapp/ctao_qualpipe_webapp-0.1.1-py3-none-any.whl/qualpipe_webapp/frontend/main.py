"""
Main application module for the QualPipe frontend.

This module sets up the FastAPI application, mounts static files, and defines
routes for rendering HTML templates using Jinja2.
"""

from pathlib import Path

import sass
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for demo/demo testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

project_root = Path(__file__).resolve().parents[0]
static_path = project_root / "static"
view_path = project_root / "view"

# Compile SCSS file to CSS
sass.compile(dirname=(str(static_path / "css"), str(static_path / "css")))

app.mount("/static", StaticFiles(directory=static_path), name="static")
view = Jinja2Templates(directory=view_path)
template_404 = "templates/404.html"


@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    """Create homepage."""
    return view.TemplateResponse(
        request=request, name="pages/home.html", context={"array_element": "home"}
    )


@app.get("/LSTs", response_class=HTMLResponse)
async def read_lst(request: Request):  # noqa: N802
    """Create LSTs placeholder."""
    return view.TemplateResponse(
        request=request,
        name="pages/array_element_type/LSTs-summary.html",
        context={"array_element": "LSTs"},
    )


@app.get("/MSTs", response_class=HTMLResponse)
async def read_mst(request: Request):  # noqa: N802
    """Create MSTs placeholder."""
    return view.TemplateResponse(
        request=request,
        name="pages/array_element_type/MSTs-summary.html",
        context={"array_element": "MSTs"},
    )


@app.get("/SSTs", response_class=HTMLResponse)
async def read_sst(request: Request):  # noqa: N802
    """Create SSTs placeholder."""
    return view.TemplateResponse(
        request=request,
        name="pages/array_element_type/SSTs-summary.html",
        context={"array_element": "SSTs"},
    )


@app.get("/Auxiliary", response_class=HTMLResponse)
async def read_auxiliary(request: Request):  # noqa: N802
    """Create Auxiliary placeholder."""
    return view.TemplateResponse(
        request=request,
        name="templates/501.html",
        context={"array_element": "Auxiliary"},
        status_code=501,
    )


@app.get("/{array_element_type}/{subitem}", response_class=HTMLResponse)
async def read_array_element_type_subitem(
    array_element_type: str, subitem: str, request: Request
):
    """Create ArrayElementType subitem pages."""
    # Check if the ArrayElementType is valid
    valid_array_element_types = [
        "LSTs",
        "MSTs",
        "SSTs",
        "Auxiliary",
    ]
    if array_element_type not in valid_array_element_types:
        return view.TemplateResponse(
            request=request,
            name=template_404,
            status_code=404,
        )
    if array_element_type in ["Auxiliary"]:
        # Check if the subitem is valid
        valid_subitems = [
            "Lidar",
            "FRAM",
            "Weather Station",
        ]
        if subitem not in valid_subitems:
            return view.TemplateResponse(
                request=request,
                name=template_404,
                status_code=404,
            )
        return view.TemplateResponse(
            request=request,
            name="templates/501.html",
            context={
                "array_element": array_element_type,
                "active_subitem": subitem,
                "subitem": subitem.replace("_", " "),
            },
            status_code=501,
        )
    else:
        # Check if the subitem is valid
        valid_subitems = [
            "event_rates",
            "trigger_tags",
            "pointings",
            "interleaved_pedestals",
            "interleaved_flat_field_charge",
            "interleaved_flat_field_time",
            "cosmics",
            "pixel_problems",
            "muons",
            "interleaved_pedestals_averages",
            "interleaved_FF_averages",
            "cosmics_averages",
        ]
        if subitem not in valid_subitems:
            return view.TemplateResponse(
                request=request,
                name=template_404,
                status_code=404,
            )

        # Render the appropriate template based on the subitem
        return view.TemplateResponse(
            request=request,
            name=f"pages/array_element_type/{subitem}.html",
            context={
                "array_element": array_element_type,
                "active_subitem": subitem,
                "subitem": subitem.replace("_", " "),
            },
        )


@app.exception_handler(404)
async def not_found(request: Request, exc):
    """Handle 404 errors."""
    return view.TemplateResponse(
        request=request,
        name=template_404,
        status_code=404,
    )
