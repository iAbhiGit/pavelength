import openai
import os
import streamlit as st

# Define your expected standard fields
EXPECTED_FIELDS = [
    "Segment_ID",
    "Segment name",
    "Road name",
    "PCI",
    "Width",
    "Thickness",
    "AADT",
    "Length",
    "Last rehab year",
    "Pavement age",
    "Pavement type",
    "Zone",
    "Segment area"
]

FIELD_HINTS = {
    "Segment_ID": ["segment id", "segment_id", "id"],
    "Segment name": ["segment name", "name"],
    "Road name": ["road name", "street name"],
    "PCI": ["pci", "pavement condition index"],
    "Width": ["width", "segment width", "road width"],
    "Thickness": ["thickness", "depth", "avg depth"],
    "AADT": ["aadt", "annual average daily traffic"],
    "Length": ["length", "shape length", "segment length", "lane miles"],
    "Last rehab year": ["last rehab year", "rehab year", "last maintenance year"],
    "Pavement age": ["pavement age", "age"],
    "Pavement type": ["pavement type", "surface", "surface type"],
    "Zone": ["zone", "district", "region"],
    "Segment area": ["segment area", "area", "shape area"]
}

def suggest_column_mapping(columns, expected_fields=EXPECTED_FIELDS):
    prompt = f"""
You are given a list of actual column names from a shapefile: {columns}

Your task is to map each of the following expected field roles (used internally in our pavement condition system) to the correct actual column name from this list.

Expected fields and example synonyms:
"""
    for field in expected_fields:
        examples = ", ".join(FIELD_HINTS.get(field, []))
        prompt += f"- {field}: {examples}\n"

    prompt += """
Respond in valid JSON where:
- The **keys** are the expected field roles from our system
- The **values** are the best-matching actual column names from the uploaded shapefile

Respond like this:
{
  "PCI": "pci_score",
  "Length": "segment_len"
}

Only include mappings you are confident about. Do not guess if unclear.
"""

    openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return eval(response.choices[0].message.content)
    except:
        return {}
