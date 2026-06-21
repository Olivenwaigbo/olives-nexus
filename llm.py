# llm.py
# Sends the user prompt + retrieved knowledge to Groq (Qwen/LLaMA)
# and parses the JSON chart config it returns
# Drop-in replacement for the Ollama version — app.py/charts.py unchanged

import os
import json
from groq import Groq

# ── Model config ───────────────────────────────────────────────────────────────
# Free Groq models — llama-3.3-70b-versatile is the best free option
MODEL  = "llama-3.3-70b-versatile"
client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """
You are a dashboard generation assistant. 
The user will describe what they want to visualise.
You will receive relevant domain knowledge as context.

Your job: return a JSON object describing which charts to render.

RULES:
1. Return ONLY valid JSON. No explanation, no markdown fences, no extra text.
2. Choose chart types based on the context provided.
3. For trends over time → use "line"
4. For comparisons by category → use "bar"
5. For part-of-whole breakdowns → use "pie"
6. For pipeline/funnel stages → use "funnel"
7. For summary numbers → use "kpi"
8. For timeline/schedule → use "gantt"
9. Always include 1-4 KPI cards for overview requests.
10. Use orientation "h" (horizontal) when category labels are long (names, departments).

OUTPUT FORMAT:
{
  "dashboard_title": "string",
  "domain": "business_finance | hr | project_management | general",
  "charts": [
    {
      "chart_id": "chart_1",
      "chart_type": "bar | line | pie | funnel | scatter | histogram | gauge",
      "title": "string",
      "x_column": "column_name or null",
      "y_column": "column_name or null",
      "color_column": "column_name or null",
      "orientation": "v | h | null",
      "barmode": "group | stack | null",
      "description": "one sentence describing this chart"
    }
  ],
  "kpi_cards": [
    {
      "kpi_id": "kpi_1",
      "label": "string",
      "value_column": "column_name",
      "aggregation": "sum | mean | count | max | min",
      "prefix": "$ or null",
      "suffix": "% or null"
    }
  ],
  "layout": "kpi_top_charts_below | 2_columns | 3_columns",
  "reasoning": "brief explanation of your choices"
}
"""


def ask_llm(user_prompt: str, context: str) -> dict:
    """
    Send prompt + knowledge context to Groq and return parsed JSON config.
    Identical return signature to the Ollama version — app.py needs no changes.
    """
    full_prompt = f"""
DOMAIN KNOWLEDGE (use this to pick the right charts and metrics):
{context}

USER REQUEST:
{user_prompt}

Remember: return ONLY the JSON object. Nothing else.
"""

    try:
        response = client.chat.completions.create(
            model    = MODEL,
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": full_prompt},
            ],
            temperature = 0.1,   # low = more predictable JSON output
            max_tokens  = 2000,
        )

        raw_text = response.choices[0].message.content.strip()

        # Clean up common LLM mistakes before parsing
        # Sometimes the model wraps JSON in ```json ... ``` fences
        if raw_text.startswith("```"):
            lines    = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])   # strip first and last line

        config = json.loads(raw_text)
        return {"success": True, "config": config, "raw": raw_text}

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error":   f"LLM returned invalid JSON: {e}",
            "raw":     raw_text if "raw_text" in locals() else "",
        }
    except Exception as e:
        return {
            "success": False,
            "error":   str(e),
            "raw":     "",
        }


def extract_table_from_text(text: str, max_chars: int = 6000) -> dict:
    """
    For PDFs/Word docs/text files that have no clean embedded table (e.g. a
    narrative report with numbers in prose), ask the LLM to pull out any
    structured data it can find and return it as JSON rows. app.py turns
    "records" into a DataFrame if found_table is true.
    """
    snippet = text[:max_chars]
    prompt = f"""
Read this document and extract any numeric or tabular data it contains —
metrics, line items, financial figures, statistics, dated values, lists
with numbers, etc.

Return ONLY a JSON object in this exact shape, nothing else:
{{
  "found_table": true or false,
  "records": [ {{"column_name": "value", "...": "..."}}, ... ],
  "note": "one short sentence describing what was extracted, or why nothing was found"
}}

Rules:
- Use consistent column names across all records.
- If there genuinely isn't enough numeric/structured data to build a table,
  set "found_table" to false and "records" to [].
- Do not invent numbers that aren't in the document.

DOCUMENT:
{snippet}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You extract structured data from documents. Return only JSON, no commentary, no markdown fences."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```"):
            lines    = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])
        return json.loads(raw_text)
    except Exception as e:
        return {"found_table": False, "records": [], "note": f"Extraction failed: {e}"}


def generate_insights(dashboard_title: str, stats_summary: str, user_prompt: str) -> dict:
    """
    Given pre-computed, real numbers about the rendered dashboard (NOT the
    raw dataframe and NOT the chart config), ask the LLM to write a short,
    concrete insights narrative. Restricting the LLM to numbers we've already
    calculated in Python keeps it from inventing stats.
    """
    prompt = f"""
DASHBOARD: {dashboard_title}
USER ASKED FOR: {user_prompt}

COMPUTED DATA SUMMARY (these are the only numbers you may reference — do not invent any others):
{stats_summary}

Write 3-5 short, specific insight bullets a business user would find useful.
Focus on notable trends, the highest/lowest values, and anything that stands
out or might need attention. Reference the actual numbers given above.
Don't just restate chart titles — interpret them.

Return ONLY a JSON object: {{"insights": ["bullet 1", "bullet 2", ...]}}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a sharp, concise data analyst. Return only JSON, no commentary, no markdown fences."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```"):
            lines    = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])
        parsed = json.loads(raw_text)
        return {"success": True, "insights": parsed.get("insights", [])}
    except Exception as e:
        return {"success": False, "insights": [], "error": str(e)}


def refine_dashboard(previous_config: dict, correction: str, context: str) -> dict:
    """
    Adjust a previously generated dashboard based on user feedback
    (e.g. "you used the wrong column for revenue", "make this a line chart
    instead", "the headcount KPI is off"). Sends the existing config back to
    the LLM along with the correction so it fixes what's wrong instead of
    regenerating the whole thing from scratch.
    """
    prompt = f"""
You previously generated this dashboard config:
{json.dumps(previous_config, indent=2)}

DOMAIN KNOWLEDGE / DATA CONTEXT:
{context}

The user has this correction or feedback about what's wrong:
"{correction}"

Update the dashboard config to fix the issue described. Keep everything
else unchanged unless the feedback implies it should also change. Return
the FULL corrected JSON object in the exact same schema as before — not a
diff, not an explanation.

Remember: return ONLY the JSON object. Nothing else.
"""
    try:
        response = client.chat.completions.create(
            model    = MODEL,
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature = 0.1,
            max_tokens  = 2000,
        )

        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```"):
            lines    = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])

        config = json.loads(raw_text)
        return {"success": True, "config": config, "raw": raw_text}

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error":   f"LLM returned invalid JSON: {e}",
            "raw":     raw_text if "raw_text" in locals() else "",
        }
    except Exception as e:
        return {
            "success": False,
            "error":   str(e),
            "raw":     "",
        }