# scripts/visualizations.py
import pandas as pd
import matplotlib.pyplot as plt

def pci_pie_chart(gdf, pci_col="PCI"):
    bins = [0, 40, 70, 100]
    labels = ["Poor", "Fair", "Good"]
    # Convert to numeric and coerce errors
    pci_values = pd.to_numeric(gdf[pci_col], errors='coerce')
    categories = pd.cut(pci_values, bins=bins, labels=labels)
    fig, ax = plt.subplots()
    categories.value_counts().plot.pie(autopct="%1.1f%%", ax=ax, colors=["red", "orange", "green"])
    ax.set_ylabel("")
    ax.set_title("PCI Condition Distribution")
    return fig

def functional_class_bar(gdf, col):
    if not col or col == "None" or col not in gdf.columns:
        return None

    fig, ax = plt.subplots()
    gdf[col].value_counts().plot.bar(ax=ax, color="skyblue")
    ax.set_title("Segments by Functional Class")
    ax.set_ylabel("Count")
    return fig
