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

def query_to_filter(user_query, column_mapping):
    """
    Converts a natural language query to a Pandas-compatible query string using OpenAI,
    fully aware of pavement engineering standards (ASTM D6433, FAA, FHWA).
    """
    openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

    expected_to_actual = column_mapping

    prompt = f"""
You are a pavement condition analysis assistant. Your task is to convert user queries into Pandas filter expressions.

Available fields:
{expected_to_actual}

Pavement Engineering Context:
- ASTM D6433 PCI Classification:
  - Excellent: PCI >= 85
  - Very Good: 70 <= PCI < 85
  - Good: 55 <= PCI < 70
  - Fair: 40 <= PCI < 55
  - Poor: 25 <= PCI < 40
  - Very Poor: 10 <= PCI < 25
  - Failed: PCI < 10

- FAA Runway Standards (if zone or surface type includes runway/taxiway/apron):
  - Runway Excellent: PCI >= 85
  - Taxiway/Apron Satisfactory: PCI >= 70
  - Serious Condition: 10 <= PCI < 25
  - Failed: PCI < 10

- Synonyms to recognize:
  - "excellent condition" = PCI >= 85
  - "serious" = 10 <= PCI < 25
  - "recently rehabilitated" = Last rehab year >= 2020
  - "AC" = Pavement type == "Asphalt"
  - "major" or "arterial" = Functional Class == "Arterial"
  - "bad roads" or "worst segments" = PCI < 25

Rules:
- Output only the Pandas query string. No explanation.
- Quote string values with double quotes.
- Wrap any column with spaces/special characters in backticks.
- Use only fields from the mapping.
- Use parentheses with AND/OR combinations.

Examples:
1. Show segments in excellent condition
→ PCI >= 85

2. Taxiways in serious condition
→ `Zone` == "Taxiway" and PCI >= 10 and PCI < 25

3. Recently rehabilitated AC roads with PCI > 55
→ `Last rehab year` >= 2020 and `Pavement type` == "Asphalt" and PCI > 55

4. Roads with good PCI and AADT > 5000
→ PCI >= 55 and PCI < 70 and AADT > 5000

User query:
{user_query}
"""

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()
    cleaned = result.replace("df[", "").replace("]", "").replace("\"", "").replace("`", "")
    return cleaned
