import openai
import os
import streamlit as st

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

    expected_to_actual = {field: column_mapping.get(field, field) for field in EXPECTED_FIELDS}

    prompt = f"""
You are a pavement condition analysis assistant specialized in road and pavement management systems. Your task is to convert natural language queries into valid Pandas-compatible `.query()` strings.

Input:
- User-provided query: a natural language description
- Field mapping: a dictionary mapping standardized field names (like 'PCI', 'Zone') to actual column names in the uploaded dataset

Mapped Fields (use these in output):
{expected_to_actual}

Domain Context:
- PCI: Pavement Condition Index (0–100)
- AADT: Annual Average Daily Traffic (numeric)
- Zone: area or region string
- Pavement type: values like Asphalt, Concrete
- Last rehab year: year field (e.g., 2020)

Synonyms:
- "excellent condition" → PCI >= 85
- "very good condition" → 70 <= PCI < 85
- "good" → 55 <= PCI < 70
- "fair" → 40 <= PCI < 55
- "poor" → 25 <= PCI < 40
- "very poor" → 10 <= PCI < 25
- "failed", "worst roads", "bad roads" → PCI < 25
- "recently rehabilitated" → Last rehab year >= 2020
- "concrete" → Pavement type == "Concrete"
- "AC" or "asphalt" → Pavement type == "Asphalt"
- "high traffic" → AADT > 5000
- "low traffic" → AADT < 1000

Output Format Rules:
- Return ONLY the Pandas query string (no variable assignments)
- Combine expressions with parentheses
- Wrap column names (even if no spaces) in backticks
- Use double quotes for string values (e.g., `Zone` == "North")
- NO triple backticks or markdown
- Do not comment your output or return explanations

User Query:
{user_query}
"""

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        raw_query = response.choices[0].message.content.strip()

        # Remove code wrappers
        for token in ["```python", "```", "query =", "query="]:
            raw_query = raw_query.replace(token, "")

        # Replace expected fields with actual mapped columns
        for expected, actual in expected_to_actual.items():
            if actual:
                raw_query = raw_query.replace(f"`{expected}`", f"`{actual}`")

        cleaned_query = raw_query.replace("\n", " ").replace("\\", "").strip()
        return cleaned_query

    except Exception as e:
        st.error(f"❌ LLM query generation failed: {e}")
        return "PCI >= 0"
