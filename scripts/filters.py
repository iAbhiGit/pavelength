# scripts/filters.py
import pandas as pd

def apply_filters(gdf, pci_col, pci_range=None, zone_col=None, selected_zone=None):
    """
    Filters the GeoDataFrame based on PCI range and optional zone.

    Parameters:
    - gdf: GeoDataFrame containing segment data
    - pci_col: str, name of the PCI column
    - pci_range: tuple (min, max) PCI filter
    - zone_col: str or None, column name for zone
    - selected_zone: str or None, specific zone to filter

    Returns:
    - Filtered GeoDataFrame
    """
    # Ensure PCI column is numeric
    gdf[pci_col] = pd.to_numeric(gdf[pci_col], errors='coerce')
    gdf = gdf.dropna(subset=[pci_col])

    if pci_range:
        gdf = gdf[(gdf[pci_col] >= pci_range[0]) & (gdf[pci_col] <= pci_range[1])]
    if zone_col and selected_zone:
        gdf = gdf[gdf[zone_col] == selected_zone]
    return gdf
