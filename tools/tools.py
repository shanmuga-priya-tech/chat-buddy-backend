import os
import json
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
# from components.dataset_vectorstore import get_vectorstore


load_dotenv()

#tavily api key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Init Gemini here so tools can use it directly
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


#web search
def web_search(query):
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.search(query, max_results=1)
    return response["results"][0]["content"]



#calculate emi
def extract_and_calculate_emi(user_query):
    """
    Extract loan details (principal, annual interest rate, tenure in years) from a user query
    using Gemini and calculate EMI.
    """
    
    prompt = f"""
    You are a finance assistant. The user will ask about an EMI calculation.
    Parse the loan amount, interest rate, and tenure from their query.
    Then calculate the exact monthly EMI using the formula:

    EMI = P × r × (1+r)^n / ((1+r)^n − 1)
    where:
      P = principal loan amount
      r = monthly interest rate (annual_rate / 12 / 100)
      n = total number of months (years × 12)

    Return ONLY the EMI amount in Indian Rupees rounded to 2 decimal places, along with inputs, 
    formatted with commas, like this:
    "Here is the result: principal=10000, interest rate=12%, year=10, emi = 1411.10"

    Do not include explanations, steps, line breaks, or extra text.

    Query: "{user_query}"
    """
    response = llm.invoke(prompt)
    return response.content.strip()
