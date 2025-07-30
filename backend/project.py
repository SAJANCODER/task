import os
import json
import sys
import re
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from security_key import open_api_key

os.environ['OPENAI_API_KEY'] = open_api_key

# Use a Chat Model
llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

# This prompt is now more precise for our server's needs
prompt_template = ChatPromptTemplate.from_messages# Use this updated prompt in backend/project.py

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert SQLite data analyst for the Northwind database.
        Your goal is to generate a JSON object to answer the user's question.

        Database Schema Context:
        - Key tables are Categories, Customers, Employees, Orders, Products, and Shippers.
        - IMPORTANT: The table for order line items is named "Order Details" (with a space). When querying this table, you MUST enclose its name in double quotes. Example: SELECT * FROM "Order Details";
        - The "Order Details" table contains: OrderID, ProductID, UnitPrice, Quantity, Discount.

        User's question: '{question}'

        Perform the following actions:
        1.  **SQL Generation**: Write a single, executable SQLite query. Remember to use "Order Details" for the order items table.
        2.  **Chart Type Suggestion**: Suggest the best chart type. Choose ONLY from 'bar', 'pie', 'line'.
        3.  **Natural Language Insight**: Write a one-sentence summary of what the data would likely show.

        Return ONLY a single, valid JSON object with this exact structure:
        {{
            "sql_query": "SELECT ...",
            "chart_type": "...",
            "insight": "..."
        }}
    """),
])

chain = prompt_template | llm | StrOutputParser()

# Read the user question passed from the main.py server
user_question = sys.stdin.read().strip()
string_response = chain.invoke({"question": user_question})

# Print only the clean JSON string for the server to read
print(string_response.strip())