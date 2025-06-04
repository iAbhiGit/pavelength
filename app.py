# app.py
import streamlit as st
import pandas as pd
from scripts.file_parser import extract_shapefile
from scripts.map_renderer import render_map
from scripts.llm_mapper import suggest_column_mapping, EXPECTED_FIELDS
from scripts.llm_query import query_to_filter
from scripts.ui_styles import inject_custom_styles

st.set_page_config(page_title="Pavelength – Pavement Condition Explorer", layout="wide")

inject_custom_styles()

header = st.columns([5, 1])
with header[0]:
    st.markdown("""<h1>🚣️ Pavelength – Pavement Condition Explorer</h1>""", unsafe_allow_html=True)
with header[1]:
    uploaded_zip = st.file_uploader("", label_visibility="collapsed", type=["zip"])

@st.cache_data(show_spinner=False)
def load_data(uploaded_file):
    return extract_shapefile(uploaded_file)

if uploaded_zip:
    try:
        gdf = load_data(uploaded_zip)
    except Exception as e:
        st.error(f"❌ Error reading shapefile: {e}")
        st.stop()

    st.success(f"✅ Total rows loaded: {len(gdf)}")
    columns = gdf.columns.tolist()

    tab1, tab2, tab3 = st.tabs(["🧩 Column Mapping", "🗺️ Map View", "📊 Data Table"])

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
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "🧩 Column Mapping"

    with tab1:
        st.session_state["active_tab"] = "🧩 Column Mapping"
        st.subheader("📊 Shapefile Summary")
        if st.checkbox("Show 20 sample rows"):
            st.dataframe(gdf.head(20))
        st.write(f"**Total rows:** {len(gdf)}")
        st.write(f"**Duplicate rows:** {gdf.duplicated().sum()}")
        st.write(f"**Projection:** {gdf.crs}")

        st.markdown("---")
        st.subheader("🔍 AI-Suggested Column Mapping")
        if st.button("🧐 Analyze Columns and Suggest Mapping") and "auto_mapping" not in st.session_state:
            with st.spinner("Analyzing columns with AI..."):
                st.session_state["auto_mapping"] = suggest_column_mapping(columns)

        if "auto_mapping" in st.session_state:
            auto_mapping = st.session_state["auto_mapping"]
            with st.expander("View Suggested Mapping", expanded=True):
                st.json(auto_mapping)

            st.subheader("🛠️ Manual Mapping")
            st.markdown("Map each expected field to a column from your data. AI-mapped values are pre-filled if available.")

            for field in EXPECTED_FIELDS:
                default_value = auto_mapping.get(field, "")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.text_input("Expected Field", value=field, disabled=True, key=f"label_{field}")
                with col2:
                    selected = st.selectbox(f"Map for: {field}", options=[""] + columns,
                                            index=(columns.index(default_value) + 1) if default_value in columns else 0,
                                            key=field)
                    if selected:
                        st.session_state["manual_mapping"][field] = selected

            if "Segment_ID" not in st.session_state["manual_mapping"]:
                st.warning("⚠️ Mapping for 'Segment_ID' is required to proceed.")
            else:
                if st.button("📌 Submit Column Mapping"):
                    st.session_state["submitted_mapping"] = True
                    st.success("✅ Mappings saved. You can now explore Map or Data tabs.")

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
            st.session_state["active_tab"] = "🗺️ Map View"
            if st.session_state["active_tab"] == "🗺️ Map View":
                st.subheader("🗺️ Map View")

                user_query = st.text_input("💬 Ask a pavement query (e.g., PCI < 40 and `Segment area` > 1000)", key="map_query")

                if st.button("🔍 Apply Map Filter", key="map_filter") and user_query:
                    try:
                        query_string = query_to_filter(user_query, manual_mapping)
                        st.info(f"🤠 Filter Applied: `{query_string}`")
                        filtered_gdf = gdf.query(query_string, engine="python")
                        st.session_state["filtered_gdf"] = filtered_gdf
                    except Exception as e:
                        st.error(f"❌ Error applying query: {e}")

                if st.button("📍 Show Map"):
                    st.session_state["show_map"] = True

                if st.session_state.get("show_map"):
                    map_data = st.session_state.get("filtered_gdf")
                    if map_data is None or map_data.empty:
                        map_data = gdf
                    with st.spinner("🗺️ Loading map..."):
                        m_html = render_map(map_data, pci_col, segment_col, manual_mapping)
                        if isinstance(m_html, str):
                            st.components.v1.html(m_html, height=600)

        with tab3:
            st.session_state["active_tab"] = "📊 Data Table"
            if st.session_state["active_tab"] == "📊 Data Table":
                st.subheader("📋 Data Table")

                user_query_data = st.text_input("📝 Ask a data query (e.g., Pavement type is AC and PCI > 50)", key="data_query")

                if st.button("🔍 Apply Data Filter", key="data_filter") and user_query_data:
                    try:
                        query_string = query_to_filter(user_query_data, manual_mapping)
                        st.info(f"🤠 Filter Applied: `{query_string}`")
                        filtered_gdf = gdf.query(query_string, engine="python")
                        st.session_state["filtered_gdf"] = filtered_gdf
                    except Exception as e:
                        st.error(f"❌ Error applying query: {e}")

                if st.button("📊 Show Data Table"):
                    st.session_state["show_data"] = True

                if st.session_state.get("show_data"):
                    data = st.session_state.get("filtered_gdf")
                    if data is None or data.empty:
                        data = gdf
                    mapped_cols = {k: v for k, v in manual_mapping.items() if v in data.columns}
                    renamed_df = data[list(mapped_cols.values())].rename(columns={v: k for k, v in mapped_cols.items()})
                    st.dataframe(renamed_df)
                    st.download_button("📅 Download CSV", data=renamed_df.to_csv(index=False), file_name="filtered_segments.csv")
