import streamlit as st
from scripts.file_parser import extract_shapefile
from scripts.map_renderer import render_map
from scripts.filters import apply_filters
from scripts.llm_mapper import suggest_column_mapping, EXPECTED_FIELDS
from scripts.llm_query import query_to_filter
import pandas as pd

st.set_page_config(page_title="Pavelength – Pavement Condition Explorer", layout="wide")
st.title("🛣️ Pavelength – Pavement Condition Explorer")

uploaded_zip = st.file_uploader("Upload zipped shapefile (.zip)", type=["zip"])

if uploaded_zip:
    try:
        gdf = extract_shapefile(uploaded_zip)
    except Exception as e:
        st.error(f"Error reading shapefile: {e}")
        st.stop()

    st.write(f"✅ Total rows loaded: {len(gdf)}")

    columns = gdf.columns.tolist()

    if "manual_mapping" not in st.session_state:
        st.session_state["manual_mapping"] = {}
    if "submitted_mapping" not in st.session_state:
        st.session_state["submitted_mapping"] = False
    if "filtered_gdf" not in st.session_state:
        st.session_state["filtered_gdf"] = None
    if "show_map" not in st.session_state:
        st.session_state["show_map"] = False
    if "show_data" not in st.session_state:
        st.session_state["show_data"] = False

    tab1, tab2, tab3 = st.tabs(["🧠 Column Mapping", "🗺️ Map View", "📋 Data Table"])

    with tab1:
        st.subheader("Column Mapping Setup")

        if st.button("🧠 Analyze Columns and Suggest Mapping"):
            with st.spinner("🔍 Analyzing your shapefile columns..."):
                st.session_state["auto_mapping"] = suggest_column_mapping(columns)
                st.success("Suggested mapping ready. Please review below.")

        auto_mapping = st.session_state.get("auto_mapping", {})

        if auto_mapping:
            st.subheader("LLM Suggested Mapping")
            st.json(auto_mapping)

            st.subheader("Manual Review and Mapping")
            st.markdown("Map each expected field to a column from your data. LLM-mapped values are pre-filled if available.")

            for field in EXPECTED_FIELDS:
                default_value = auto_mapping.get(field, "")
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.text_input("Expected Field", value=field, disabled=True, key=f"label_{field}")
                with col2:
                    selected = st.selectbox(f"Map for: {field}", options=[""] + columns, index=(columns.index(default_value) + 1) if default_value in columns else 0, key=field)
                    if selected:
                        st.session_state["manual_mapping"][field] = selected

            if "Segment_ID" not in st.session_state["manual_mapping"]:
                st.warning("Mapping for 'Segment_ID' is required to proceed.")
            else:
                if st.button("📌 Submit Column Mapping"):
                    st.session_state["submitted_mapping"] = True
                    st.success("Mappings saved. Go to the Map or Data tabs to continue.")

    if st.session_state["submitted_mapping"]:
        manual_mapping = st.session_state["manual_mapping"]
        pci_col = manual_mapping.get("PCI", "PCI")
        segment_col = manual_mapping.get("Segment_ID", "segment_id")

        gdf[pci_col] = pd.to_numeric(gdf[pci_col], errors='coerce')
        gdf = gdf.dropna(subset=[pci_col])
        gdf = gdf[gdf.geometry.notnull() & gdf.geometry.is_valid]

        if st.session_state["filtered_gdf"] is None:
            st.session_state["filtered_gdf"] = gdf

        with tab2:
            st.subheader("🗺️ Map View")

            user_query = st.text_input("💬 Ask a pavement query (e.g., PCI < 40 and `Segment area` > 1000)", key="map_query")

            if st.button("🔍 Apply Map Filter", key="map_filter") and user_query:
                with st.spinner("🧠 Applying query to map view..."):
                    try:
                        query_string = query_to_filter(user_query, manual_mapping)
                        st.write(f"🧠 Filter Applied: `{query_string}`")
                        filtered_gdf = gdf.query(query_string, engine="python")
                        st.session_state["filtered_gdf"] = filtered_gdf
                    except Exception as e:
                        st.error(f"Error applying query: {e}")

            if st.button("📍 Show Map"):
                st.session_state["show_map"] = True

            if st.session_state.get("show_map"):
                with st.spinner("🗺️ Loading map..."):
                    map_data = st.session_state["filtered_gdf"] if st.session_state["filtered_gdf"] is not None else gdf
                    m_html = render_map(map_data, pci_col, segment_col, manual_mapping)
                    if isinstance(m_html, str):
                        st.components.v1.html(m_html, height=600)

        with tab3:
            st.subheader("📋 Data Table")

            user_query_data = st.text_input("Ask a pavement-related data question (e.g., type AC and PCI > 50)", key="data_query")

            if st.button("🔍 Apply Data Filter", key="data_filter") and user_query_data:
                with st.spinner("📊 Applying filter to table..."):
                    try:
                        query_string = query_to_filter(user_query_data, manual_mapping)
                        st.write(f"🧠 Filter Applied: `{query_string}`")
                        filtered_gdf = gdf.query(query_string, engine="python")
                        st.session_state["filtered_gdf"] = filtered_gdf
                    except Exception as e:
                        st.error(f"Error applying query: {e}")

            if st.button("📊 Show Data Table"):
                st.session_state["show_data"] = True

            if st.session_state.get("show_data"):
                data = st.session_state["filtered_gdf"] if st.session_state["filtered_gdf"] is not None else gdf
                mapped_cols = {k: v for k, v in manual_mapping.items() if v in data.columns}
                renamed_df = data[list(mapped_cols.values())].rename(columns={v: k for k, v in mapped_cols.items()})
                st.dataframe(renamed_df)
                st.download_button("📥 Download CSV", data=renamed_df.to_csv(index=False), file_name="filtered_segments.csv")
