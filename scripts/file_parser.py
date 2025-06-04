import geopandas as gpd
import zipfile
import os
import tempfile
import pandas as pd

def extract_shapefile(uploaded_zip):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getbuffer())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Recursively find .shp (case-insensitive)
        shp_path = None
        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file.lower().endswith(".shp"):
                    shp_path = os.path.join(root, file)
                    break
            if shp_path:
                break

        if not shp_path:
            raise FileNotFoundError("No .shp file found in uploaded ZIP. Ensure it's not deeply nested.")

        gdf = gpd.read_file(shp_path)

        # Convert CRS to WGS84 if needed
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")

        # ✅ Fix duplicate column names
        cols = pd.Series(gdf.columns)
        duplicates = cols.duplicated()
        if duplicates.any():
            for dup in cols[duplicates].unique():
                dups_idx = cols[cols == dup].index.tolist()
                for i, idx in enumerate(dups_idx[1:], start=1):  # skip first occurrence
                    cols[idx] = f"{dup}_{i}"
            gdf.columns = cols

        return gdf
