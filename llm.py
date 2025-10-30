# llm.py
from openai import OpenAI
from config import OPENAI_API_KEY
import json
import re

client = OpenAI(api_key=OPENAI_API_KEY)

# Load schema context
with open("schema_description.txt", "r") as f:
    SCHEMA_CONTEXT = f.read()

def is_relevant_question(question: str) -> bool:
    """
    Returns True if the question is about the retail store database.
    """
    prompt = f"""
You are a gatekeeper for a retail store performance analytics system.
The system ONLY answers questions about:
- Store scores (store_score, phr_score, sof_score, osa_npi_score, etc.)
- Stores, store codes, regions, states, cities
- Area Sales Executives (ASEs)
- Monthly reports (January 2025)

Question: "{question}"

Is this question about the retail store database? Answer ONLY "yes" or "no".
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=5
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except:
        # If LLM fails, assume irrelevant to avoid unsafe SQL
        return False

def clean_sql(sql: str) -> str:
    """Remove markdown code blocks if present."""
    sql = sql.strip()
    if sql.startswith("```"):
        sql = re.split(r"```(?:sql)?", sql, maxsplit=1)[-1].split("```")[0].strip()
    return sql

def generate_sql(question: str) -> str:
    prompt = f"""{SCHEMA_CONTEXT}

Question: {question}
Generate ONLY a PostgreSQL SELECT query. Do not explain. Do not add markdown.
SQL:"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=250
    )
    raw_sql = response.choices[0].message.content
    return clean_sql(raw_sql)

def generate_answer(question: str, result: list) -> str:
    if not result:
        return "No matching records found in the retail store database."

    # Handle aggregation results (e.g., COUNT, AVG)
    first_row = result[0]
    if len(result) == 1 and len(first_row) == 1:
        key = list(first_row.keys())[0]
        value = first_row[key]
        if "count" in key.lower():
            return f"There are {int(value)} stores matching your criteria."
        elif "avg" in key.lower() or "average" in question.lower():
            return f"The average is {float(value):.2f}."
        else:
            return f"The result is {value}."

    # Default: send first 10 rows
    data_str = json.dumps(result[:10], indent=2)
    prompt = f"""You are a precise retail data assistant. Answer using ONLY the data below.

Question: {question}
Data (first {min(10, len(result))} of {len(result)} matching rows): {data_str}

Instructions:
- If more than 10 rows match, mention the total count.
- Round decimals to 2 places.
- NEVER say "not available" — data exists.
- Be concise and professional.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()