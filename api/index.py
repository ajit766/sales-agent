from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

# Load explicitly from the project root if running locally
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Important: these must be directly importable in the Vercel environment
from .d365_client import get_opportunities, update_opportunity, create_draft_task
from openai import AzureOpenAI

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Copilot Sales Agent API is running. Please test via the React frontend on localhost:3000."}

# --- Pydantic Models for Next.js <-> Python Communication ---
class AnalyzeRequest(BaseModel):
    transcript: str

class CommitRequest(BaseModel):
    opportunity_id: str
    owner_id: str
    budgetamount: float
    estimatedclosedate: str
    decision_maker_name: str
    draft_email_subject: str
    draft_email_body: str

# --- Azure AI Client Setup ---
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
    from datetime import datetime
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

@app.post("/api/analyze")
def analyze_transcript(req: AnalyzeRequest):
    """Step 1: Analyzes the transcript, matches to D365 Opportunity, and returns before/after diffs to UI."""
    if not req.transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")

    try:
        # 1. Get Live CRM Data
        opps = get_opportunities()
        if not opps:
            raise HTTPException(status_code=404, detail="No open opportunities found in Dynamics 365 pipeline.")
            
        opp_names = [opp.get("name") for opp in opps]
        
        # 2. Extract Data via Azure AI Foundry
        extracted_data = extract_transcript_data(req.transcript, opp_names)
        
        target_opp_name = extracted_data.get("target_opportunity_name")
        if not target_opp_name:
             # Graceful Fallback: The UI will catch this 404 and let the user select manually
             raise HTTPException(status_code=404, detail="No matching Opportunity found in CRM.")
             
        # 3. Match Data
        target_opp = next((opp for opp in opps if opp.get("name") == target_opp_name), None)
        if not target_opp:
             raise HTTPException(status_code=404, detail=f"Extracted Opportunity '{target_opp_name}' does not exactly match CRM pipeline.")
             
        # Generate the Before/After response for the UI validation screen
        return {
            "success": True,
            "opportunity": {
                "id": target_opp.get("opportunityid"),
                "name": target_opp.get("name"),
                "owner_id": target_opp.get("_ownerid_value")
            },
            "meeting_summary": extracted_data.get("meeting_summary"),
            "draft_email": {
                "subject": extracted_data.get("draft_email_subject"),
                "body": extracted_data.get("draft_email_body"),
                "decision_maker": extracted_data.get("decision_maker_name")
            },
            "crm_diff": {
                "budget": {
                    "existing": target_opp.get("budgetamount"),
                    "proposed": extracted_data.get("budgetamount")
                },
                "estimated_close_date": {
                    "existing": target_opp.get("estimatedclosedate"),
                    "proposed": extracted_data.get("estimatedclosedate")
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server Error during analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/commit")
def commit_to_crm(req: CommitRequest):
    """Step 2: Commits the validated data to Dynamics 365."""
    try:
        # Patch Opportunity
        update_payload = {
            "budgetamount": req.budgetamount,
            "estimatedvalue": req.budgetamount,
            "isrevenuesystemcalculated": False,
            "estimatedclosedate": req.estimatedclosedate
        }
        update_opportunity(req.opportunity_id, update_payload)
        
        # Post Human-in-the-Loop Task Activity
        task_desc = f"Please review and send this drafted email to {req.decision_maker_name}:\n\n{req.draft_email_body}"
        task_id = create_draft_task(req.opportunity_id, req.draft_email_subject, task_desc, owner_id=req.owner_id)
        
        return {"success": True, "task_id": task_id, "message": "CRM perfectly updated."}
        
    except Exception as e:
        print(f"Server Error during commit: {e}")
        raise HTTPException(status_code=500, detail=str(e))
