import folium
from streamlit_folium import st_folium
from scripts.llm_mapper import EXPECTED_FIELDS

def render_map(gdf, pci_col, segment_col, mapping=None):
    if gdf.empty:
        return st_folium(folium.Map(location=[0, 0], zoom_start=2), width=1200, height=700)

    # Simplify geometries slightly for better performance
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.0001, preserve_topology=True)

    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, width="100%")

    for _, row in gdf.iterrows():
        pci = row.get(pci_col, 0)
        seg_id = row.get(segment_col, "N/A")
        color = "green" if pci > 70 else "orange" if pci > 40 else "red"

        popup_lines = [f"<b>{field}:</b> {row.get(mapping[field], '')}" for field in EXPECTED_FIELDS if mapping and field in mapping and mapping[field] in row]
        popup_html = "<br>".join(popup_lines)

        folium.GeoJson(
            row.geometry,
            popup=folium.Popup(popup_html, max_width=400),
            style_function=lambda x, color=color: {"color": color, "weight": 3}
        ).add_to(m)

    return st_folium(m, width=1400, height=700)
