from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

# Load explicitly from the project root if running locally
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Important: these must be directly importable in the Vercel environment
from .d365_client import get_opportunities, update_opportunity, create_draft_task, get_todays_appointments
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

@app.get("/api/briefing")
def generate_daily_briefing():
    """Workstream 2: Generates a proactive daily briefing using custom deterministic Python logic 
    and the Eisenhower Matrix, using LLM only for Meeting Intelligence and final formatting."""
    try:
        # 1. Get Live CRM Data
        opps = get_opportunities()
        if not opps:
            raise HTTPException(status_code=404, detail="No open opportunities found in Dynamics 365 pipeline.")

        # 2. Compute Pipeline Metrics & Categorize via Custom Logic
        from datetime import datetime
        today = datetime.now()
        
        def parse_date(date_str):
            if not date_str: return None
            try:
                if len(date_str) == 10: return datetime.strptime(date_str, "%Y-%m-%d")
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                return None

        # Calculate Percentiles
        valid_opps = [o for o in opps if o.get('estimatedvalue')]
        all_values = sorted([o['estimatedvalue'] for o in valid_opps])
        median_deal_size = all_values[len(all_values) // 2] if all_values else 0
        
        # EXPLANATION: top_25_deal_size represents the threshold value for the top 25% largest deals in the pipeline.
        # Calculation: We sort all open deals by revenue ascending, and grab the value at the 75th percentile index.
        top_25_deal_size = all_values[int(len(all_values) * 0.75)] if all_values else 0
        
        total_open_pipeline = sum(o['estimatedvalue'] for o in valid_opps)
        
        # EXPLANATION: weighted_forecast represents the actual risk-adjusted expected revenue.
        # Calculation: We multiply every active deal's total value by its current confidence probability 
        # (e.g. a $100,000 deal with an 80% probability contributes $80,000 to the forecast) and sum them up.
        weighted_forecast = sum(o['estimatedvalue'] * (o.get('closeprobability') or 0) / 100 for o in valid_opps)

        # Module Bins
        m1_prioritized = []
        m2_blocked = []
        m3_quick_wins = []
        m4_high_risk = []
        m5_activities_for_ai = []
        m7_zombies = []

        for opp in opps:
            name = opp.get("name") or "Unknown"
            value = opp.get("estimatedvalue") or 0
            prob = opp.get("closeprobability") or 0
            stage = opp.get("salesstagecode") or 1 # 1=Qualify, 2=Propose, 3=Close
            
            close_date = parse_date(opp.get("estimatedclosedate"))
            modified_date = parse_date(opp.get("modifiedon"))
            
            days_to_close = (close_date - today).days if close_date else 999
            days_since_active = (today - modified_date).days if modified_date else 999
            
            # Module 1: Revenue Prioritization Engine
            score = 0
            if days_to_close < 14: score += 20
            if days_since_active > 5: score += 15
            if value >= top_25_deal_size: score += 25
            m1_prioritized.append({"name": name, "score": score, "revenue": value, "days_since_active": days_since_active, "why_now": f"No activity in {days_since_active} days" if days_since_active < 999 else "No recent activity"})
            
            # Module 2: Blocked on You 
            if prob >= 50 and stage > 1 and days_since_active > 3:
                m2_blocked.append(f"{name} - High probability ({prob}%) in late stage with no activity in {days_since_active} days.")
                
            # Module 3: Quick Wins
            if prob >= 70 and value <= median_deal_size and days_to_close < 14:
                m3_quick_wins.append({"name": name, "revenue": value, "why_now": f"Closing in {days_to_close} days"})
                
            # Module 4: High-Risk Large Deals
            if value >= top_25_deal_size and (days_since_active > 5 or days_to_close < 14):
                m4_high_risk.append(f"{name} - Large Deal (${value:,.0f}). Closing in {days_to_close} days with no activity in {days_since_active} days.")
                
        # 2b. Module 5 Data (Today's Meetings)
        todays_appointments = get_todays_appointments()
        for appt in todays_appointments:
            subj = appt.get("subject", "Meeting")
            desc = appt.get("description", "")
            time_start = appt.get("scheduledstart", "")
            
            # Extract Opp data if linked
            opp_data = appt.get("regardingobjectid_opportunity_appointment", {})
            opp_name = opp_data.get("name", "Unknown Deal")
            opp_val = opp_data.get("estimatedvalue", 0)
            
            m5_activities_for_ai.append({
                "time": time_start,
                "opportunity": opp_name,
                "value": opp_val,
                "subject": subj,
                "notes": desc
            })

            # Module 7: Stalled Deals (Zombies)
            if days_since_active > 14 and stage > 1:
                m7_zombies.append(f"{name} - No activity in {days_since_active} days. Consider closing out.")

        # Sort and limit Module 1
        m1_prioritized = sorted(m1_prioritized, key=lambda x: x["score"], reverse=True)[:5]
        m3_quick_wins = sorted(m3_quick_wins, key=lambda x: x["revenue"], reverse=True)

        # 3. Call LLM purely for Module 5 Generation and overall Markdown Formatting
        client = get_ai_client()
        current_date_str = today.strftime("%Y-%m-%d")
        
        system_prompt = f"""
        You are a world-class AI Revenue Director formatting a Daily Briefing.
        Today's date is: {current_date_str}.

        I have already processed the CRM data using deterministic Python logic and categorized them into the Eisenhower Matrix modules. 
        Your ONLY job is to:
        1. Read the pre-calculated JSON payload below.
        2. Format it into beautiful, structured B2B Markdown.
        3. For 'Module 5: Meeting Intelligence', use your AI capabilities to read the raw appointment Notes and Context provided, summarize the context as bullet points, and suggest a strategic closing move for the meeting.
        
        Do NOT wrap the output in a ```markdown block, just output the raw text.
        
        CRITICAL FORMATTING RULES:
        1. You MUST include a single italicized sentence directly below each Module's Header explaining the logic used to calculate it (e.g. *Logic: Top 25% deals by value with slipping dates or no activity > 5 days.*)
        2. The table headers for Module 1 and Module 3 MUST naturally say 'Comments' instead of 'Why Now?'.
        3. Module 1 and Module 3 tables must NOT have an 'Action' column.
        4. Module 5 must be formatted EXACTLY like this structure for each meeting:
           **[Time/Date] - [Opportunity Name] ([Subject])**
           - Stage: [Stage]
           - Value: [Budget]
           - Context: [AI summarized bullet point notes]
           - Suggested Goal: [AI suggested goal]
        
        OUTPUT STRUCTURE REQUIRED:
        # 🎯 Your Daily Revenue Briefing

        ## 🚨 Module 1: Revenue Prioritization Engine (Q1 - DO FIRST)
        *Logic: Top 5 opportunities mathematically ranked by close date proximity, deal size weight, and engagement gap.*
        <Format m1_prioritized as a Markdown Table: Rank | Account | Comments | Score | Est. Revenue>

        ## 🛑 Module 2: Blocked on You (Q1 - DO FIRST)
        *Logic: High probability deals (>50%) in late stages with no outbound task activity > 3 days.*
        <Format m2_blocked as bullets, or say "No items currently blocked on you." if empty>

        ## ⚡ Module 3: Quick Wins (Q3 - DELEGATE / QUICK REVENUE)
        *Logic: Deals with >70% probability, smaller than median deal size, closing in < 14 days.*
        <Format m3_quick_wins as a Markdown Table: Rank | Account | Comments | Revenue>

        ## ⚠️ Module 4: High-Risk Large Deals (Q1 - URGENT INTERVENTION)
        *Logic: Deals in top 25% of pipeline value with > 5 days of inactivity or slipping close dates.*
        <Format m4_high_risk as bullets, or say "No high-risk enterprise deals detected." if empty>

        ## 🗓️ Module 5: Meeting Intelligence (Prep)
        *Logic: AI synthesized summaries for today's scheduled Dataverse Appointments.*
        <Read m5_activities_for_ai. Summarize the meetings using the exact bulleted format requested in the rules above.>

        ## 📊 Module 6: Pipeline Health Snapshot
        *Logic: Aggregated totals of the open pipeline and probability-weighted risk forecast.*
        <Write a short executive summary using: Total Pipeline: ${total_open_pipeline:,.0f} | Weighted Forecast: ${weighted_forecast:,.0f}>

        ## 🧟 Module 7: Zombie Deals (Q4 - ELIMINATE)
        *Logic: Deals stuck in Proposal/Negotiation stage with 0 activity in > 14 days.*
        <Format m7_zombies as bullets, or say "No zombie deals detected." if empty>

        PRE-CALCULATED JSON DATA TO FORMAT:
        {json.dumps({
            "m1_prioritized": m1_prioritized,
            "m2_blocked": m2_blocked,
            "m3_quick_wins": m3_quick_wins,
            "m4_high_risk": m4_high_risk,
            "m5_activities_for_ai": m5_activities_for_ai,
            "m7_zombies": m7_zombies
        }, indent=2)}
        """

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Format my briefing."}
            ],
            temperature=0.4
        )
        
        return {"success": True, "markdown": response.choices[0].message.content}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Server Error during briefing generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
