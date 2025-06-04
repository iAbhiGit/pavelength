import pandas as pd

def apply_filters(
    gdf,
    pci_range=None,
    selected_zone=None,
    aadt_range=None,
    pavement_types=None,
    rehab_year_range=None,
    pavement_age_range=None,
    segment_area_range=None,
    width_range=None,
    thickness_range=None,
    length_range=None
):
    """
    Filters the GeoDataFrame based on standardized expected fields.

    Parameters:
    - gdf: GeoDataFrame with standardized column names.
    - pci_range: (min, max) PCI values.
    - selected_zone: string to filter 'Zone'.
    - aadt_range: (min, max) AADT values.
    - pavement_types: list of types (e.g., ["Asphalt", "Concrete"])
    - rehab_year_range: (min, max) for 'Last rehab year'.
    - pavement_age_range: (min, max) for 'Pavement age'.
    - segment_area_range: (min, max) for 'Segment area'.
    - width_range: (min, max) for 'Width'.
    - thickness_range: (min, max) for 'Thickness'.
    - length_range: (min, max) for 'Length'.

    Returns:
    - Filtered GeoDataFrame
    """
    def safe_numeric_filter(df, col, value_range):
        if col in df.columns and value_range:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=[col])
            df = df[(df[col] >= value_range[0]) & (df[col] <= value_range[1])]
        return df

    # Ensure gdf is valid before filtering
    if not isinstance(gdf, pd.DataFrame) or gdf.empty:
        return pd.DataFrame(columns=gdf.columns if hasattr(gdf, 'columns') else [])

    # PCI
    gdf = safe_numeric_filter(gdf, "PCI", pci_range)

    # Zone
    if "Zone" in gdf.columns and selected_zone:
        gdf = gdf[gdf["Zone"] == selected_zone]

    # AADT
    gdf = safe_numeric_filter(gdf, "AADT", aadt_range)

    # Pavement type
    if "Pavement type" in gdf.columns and pavement_types:
        gdf = gdf[gdf["Pavement type"].isin(pavement_types)]

    # Last rehab year
    gdf = safe_numeric_filter(gdf, "Last rehab year", rehab_year_range)

    # Pavement age
    gdf = safe_numeric_filter(gdf, "Pavement age", pavement_age_range)

    # Segment area
    gdf = safe_numeric_filter(gdf, "Segment area", segment_area_range)

    # Width
    gdf = safe_numeric_filter(gdf, "Width", width_range)

    # Thickness
    gdf = safe_numeric_filter(gdf, "Thickness", thickness_range)

    # Length
    gdf = safe_numeric_filter(gdf, "Length", length_range)

    return gdf
