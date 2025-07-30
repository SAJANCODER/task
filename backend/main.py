import json
import sqlite3
import pandas as pd
import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuration & Initialization ---
DB_PATH = "northwind.db"
app = FastAPI()

# Allow frontend to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

def get_ai_analysis_from_script(user_question: str) -> str:
    """Executes project.py using the correct python environment."""
    command = [sys.executable, "project.py"]
    process = subprocess.run(
        command, input=user_question, capture_output=True, text=True
    )
    if process.returncode != 0:
        print("Error from project.py:", process.stderr)
        return json.dumps({"error": "The analysis script failed.", "details": process.stderr})
    return process.stdout

def execute_sql_query(query: str):
    """Executes the SQL query on the actual database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(query, conn)
            return df.to_dict(orient="records")
    except (sqlite3.OperationalError, pd.io.sql.DatabaseError) as e:
        print(f"SQL Error: {e}")
        return {"error": str(e), "query": query}

@app.post("/api/query")
async def handle_query(request: QueryRequest):
    """API endpoint that orchestrates the full request cycle."""
    script_output = get_ai_analysis_from_script(request.question)

    try:
        llm_response_json = json.loads(script_output)

        sql_query = llm_response_json.get("sql_query")

        if not sql_query:
            return {"error": "AI failed to generate an SQL query.", "raw_output": script_output}

        data = execute_sql_query(sql_query)

        if "error" in data:
            return {"error": f"Failed to execute SQL. {data['error']}", "query": data['query']}

        final_response = {
            "data": data,
            # This is the corrected line
            "chartType": llm_response_json.get("chart_type", "bar"),
            "insight": llm_response_json.get("insight", "No insight provided."),
            "sqlQuery": sql_query
        }
        return final_response
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response from script output.", "raw_output": script_output}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}