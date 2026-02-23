import os
import json
from datetime import datetime
from fastapi import HTTPException
from openai import AzureOpenAI

PROJECT_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

def get_ai_client():
    if not PROJECT_ENDPOINT or not AZURE_OPENAI_KEY:
        raise HTTPException(status_code=500, detail="Missing Azure OpenAI configuration in backend.")
        
    base_endpoint = PROJECT_ENDPOINT.split("/api")[0].replace(".services.ai.azure.com", ".openai.azure.com")
    return AzureOpenAI(
        azure_endpoint=base_endpoint,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-15-preview"
    )

def extract_transcript_data(transcript_text: str, open_opportunity_names: list):
    client = get_ai_client()
    current_year = datetime.now().year
    
    system_prompt = f"""
    You are an expert sales assistant. Read the following meeting transcript.
    You must extract the actionable sales data and return it as a pure JSON object without markdown formatting.
    
    CRITICAL CONTEXT: The current year is {current_year}. If a month/day is mentioned without a year (e.g. "March 15th"), you MUST assume it is for the upcoming occurrence (e.g. {current_year} or {current_year + 1}). DO NOT default to past years like 2024.
    
    You must identify which active Opportunity this meeting was regarding. 
    Here is the list of active Opportunity Names in our CRM:
    {open_opportunity_names}
    
    If none of the opportunities in the list match the transcript exactly or contextually, set "target_opportunity_name" to null.
    
    Follow this exact JSON schema:
    {{
        "target_opportunity_name": "<The exact name of the Opportunity from the list above, or null if no match>",
        "meeting_summary": "<A brief 2-3 sentence executive summary of the meeting context>",
        "budgetamount": <numeric float value of the budget mentioned>,
        "estimatedclosedate": "<YYYY-MM-DD format of the deadline/timeline mentioned>",
        "decision_maker_name": "<name of the decision maker>",
        "draft_email_subject": "<a professional subject line for a follow-up email>",
        "draft_email_body": "<a personalized follow up email thanking them and confirming the details>"
    }}
    """
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript_text}
        ],
        response_format={ "type": "json_object" },
        temperature=0.2
    )

    result_json = response.choices[0].message.content
    if result_json.startswith("```json"):
        result_json = result_json[7:-3]
    elif result_json.startswith("```"):
        result_json = result_json[3:-3]
        
    return json.loads(result_json.strip())
