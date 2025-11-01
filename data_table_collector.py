"""Utilities for downloading Seoul open API table data and exporting as CSV and image.

This module provides a command line interface for downloading tabular data from the
Seoul open API (https://data.seoul.go.kr/).  It supports exporting the retrieved data
into CSV files and rendering the resulting table into an image for documentation or
reporting purposes.
"""
from __future__ import annotations

import argparse
import pathlib
from typing import Any, Dict, List

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pandas as pd
import requests
if any("Malgun Gothic" in f.name for f in font_manager.fontManager.ttflist):
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    # Fall back to a generic sans-serif font while warning users that
    # Malgun Gothic improves readability for Korean text.
    rc("font", family="sans-serif")

# Prevent minus signs from rendering as boxes when using Korean fonts.
plt.rcParams["axes.unicode_minus"] = False

DEFAULT_SERVICE = "ListAirQualityByDistrictService"
DEFAULT_START_INDEX = 1
DEFAULT_END_INDEX = 5


class SeoulOpenAPIError(RuntimeError):
    """Raised when the Seoul Open API returns an error payload."""


def build_request_url(
    api_key: str,
    service: str = DEFAULT_SERVICE,
    start_index: int = DEFAULT_START_INDEX,
    end_index: int = DEFAULT_END_INDEX,
    payload_format: str = "json",
) -> str:
    """Build the request URL for the Seoul open API.

    Parameters
    ----------
    api_key:
        Issued Open API key from https://data.seoul.go.kr/.
    service:
        Dataset service identifier. The default retrieves the air quality
        dataset (`ListAirQualityByDistrictService`).
    start_index, end_index:
        Record indices for pagination. The API is inclusive, so the default
        of 1 and 5 will request the first five rows.
    payload_format:
        Either ``"json"`` or ``"xml"``. JSON is used by default because it is
        easier to parse into :class:`pandas.DataFrame` objects.
    """
    return (
        f"http://openAPI.seoul.go.kr:8088/{api_key}/{payload_format}/"
        f"{service}/{start_index}/{end_index}/"
    )


def _extract_rows(service: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract the row data list from a JSON payload returned by the API."""
    service_payload = payload.get(service)
    if not service_payload:
        raise SeoulOpenAPIError(
            "Unexpected API response: could not find service payload. "
            "Check the service name or API key."
        )

    if service_payload.get("RESULT", {}).get("CODE") != "INFO-000":
        result = service_payload.get("RESULT", {})
        raise SeoulOpenAPIError(
            f"API returned error {result.get('CODE')}: {result.get('MESSAGE')}"
        )

    rows = service_payload.get("row")
    if rows is None:
        raise SeoulOpenAPIError("API response does not include a 'row' field.")

    if not isinstance(rows, list):
        raise SeoulOpenAPIError("API response 'row' field is not a list.")

    return rows


def fetch_table(
    api_key: str,
    service: str = DEFAULT_SERVICE,
    start_index: int = DEFAULT_START_INDEX,
    end_index: int = DEFAULT_END_INDEX,
) -> pd.DataFrame:
    """Download dataset rows from the Seoul open API as a DataFrame."""
    url = build_request_url(api_key, service, start_index, end_index)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    payload = response.json()
    rows = _extract_rows(service, payload)

    return pd.DataFrame(rows)


def save_csv(df: pd.DataFrame, output_path: pathlib.Path) -> None:
    """Save the DataFrame into a CSV file with UTF-8 encoding."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")


def render_table_image(
    df: pd.DataFrame,
    output_path: pathlib.Path,
    *,
    title: str | None = None,
    max_rows: int = 15,
) -> None:
    """Render the DataFrame as an image using matplotlib.

    Parameters
    ----------
    df:
        Data to render. The DataFrame is automatically truncated to ``max_rows``
        to avoid generating very large images.
    output_path:
        Destination path for the image. The file type is inferred from the
        suffix (for example ``.png`` or ``.jpg``).
    title:
        Optional title text displayed above the table.
    max_rows:
        Limit the number of rows displayed in the image. Set this to ``None``
        to disable truncation.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if max_rows is not None and len(df) > max_rows:
        display_df = df.head(max_rows).copy()
    else:
        display_df = df.copy()

    fig, ax = plt.subplots(figsize=(max(6, len(display_df.columns) * 1.2), 0.5 * len(display_df) + 2))
    ax.axis("off")

    table = ax.table(cellText=display_df.values, colLabels=display_df.columns, loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.2)

    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download tabular data from the Seoul open API and export it to CSV "
            "and a rendered image."
        )
    )
    parser.add_argument("api_key", help="Seoul open API key")
    parser.add_argument(
        "--service",
        default=DEFAULT_SERVICE,
        help="Dataset service identifier (default: %(default)s)",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=DEFAULT_START_INDEX,
        help="Start index for pagination (default: %(default)s)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=DEFAULT_END_INDEX,
        help="End index for pagination (default: %(default)s)",
    )
    parser.add_argument(
        "--csv",
        type=pathlib.Path,
        default=pathlib.Path("output/data.csv"),
        help="Path to save the CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--image",
        type=pathlib.Path,
        default=pathlib.Path("output/data.png"),
        help="Path to save the rendered table image (default: %(default)s)",
    )
    parser.add_argument(
        "--title",
        help="Optional title to display on the rendered image",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=15,
        help="Maximum number of rows to display in the image (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = fetch_table(args.api_key, args.service, args.start, args.end)
    save_csv(df, args.csv)
    render_table_image(df, args.image, title=args.title, max_rows=args.max_rows)
    print(f"Saved CSV to {args.csv.resolve()}")
    print(f"Saved image to {args.image.resolve()}")


if __name__ == "__main__":
    main()
