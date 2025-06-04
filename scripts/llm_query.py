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
    including context-aware logic for pavement engineering (ASTM D6433).
    """
    openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

    # Prompt with domain context and examples
    expected_to_actual = column_mapping

    prompt = f"""
You are a pavement condition analysis assistant. Convert user queries into valid Pandas filter expressions.

Mapped fields:
{expected_to_actual}

Important fields:
- PCI: Pavement Condition Index (0–100)
- AADT: Annual Average Daily Traffic (numeric)
- Zone: Name of subdivision, area, region (string) — treat like free-text
- Pavement type: May include Asphalt, Concrete, etc.
- Last rehab year: Integer year (e.g., 2015, 2020)

Synonyms and NLP mappings:
- "excellent condition" → PCI >= 85
- "very good condition" → 70 <= PCI < 85
- "good" → 55 <= PCI < 70
- "fair" → 40 <= PCI < 55
- "poor" → 25 <= PCI < 40
- "very poor" → 10 <= PCI < 25
- "failed" or "bad roads" or "worst" → PCI < 10 or PCI < 25
- "recently rehabilitated" → `Last rehab year` >= 2020
- "AC" → `Pavement type` == "Asphalt"
- "concrete" → `Pavement type` == "Concrete"
- "high traffic" → AADT > 5000
- "low traffic" → AADT < 1000

Formatting rules:
- Return ONLY a valid Pandas `.query()` string
- Wrap column names with spaces or special characters using backticks: \` \`
- Use double quotes for string values
- Combine filters using parentheses for clarity

Example conversions:
1. Bad roads in zone South-East
→ PCI < 25 and `Zone` == "South-East"

2. Recently rehabilitated roads with AADT above 7000
→ `Last rehab year` >= 2020 and AADT > 7000

3. Concrete pavement segments in Sector 5 with PCI below 40
→ `Pavement type` == "Concrete" and `Zone` == "Sector 5" and PCI < 40

Now generate the filter for:
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
