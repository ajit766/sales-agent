from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.llm_service import extract_transcript_data
from api.clients.d365_client import get_opportunities, update_opportunity, create_draft_task

router = APIRouter()

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

@router.post("/api/analyze")
def analyze_transcript(req: AnalyzeRequest):
    """Step 1: Analyzes the transcript, matches to D365 Opportunity, and returns before/after diffs to UI."""
    if not req.transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")

    try:
        opps = get_opportunities()
        if not opps:
            raise HTTPException(status_code=404, detail="No open opportunities found in Dynamics 365 pipeline.")
            
        opp_names = [opp.get("name") for opp in opps]
        extracted_data = extract_transcript_data(req.transcript, opp_names)
        
        target_opp_name = extracted_data.get("target_opportunity_name")
        if not target_opp_name:
             raise HTTPException(status_code=404, detail="No matching Opportunity found in CRM.")
             
        target_opp = next((opp for opp in opps if opp.get("name") == target_opp_name), None)
        if not target_opp:
             raise HTTPException(status_code=404, detail=f"Extracted Opportunity '{target_opp_name}' does not exactly match CRM pipeline.")
             
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

@router.post("/api/commit")
def commit_to_crm(req: CommitRequest):
    """Step 2: Commits the validated data to Dynamics 365."""
    try:
        update_payload = {
            "budgetamount": req.budgetamount,
            "estimatedvalue": req.budgetamount,
            "isrevenuesystemcalculated": False,
            "estimatedclosedate": req.estimatedclosedate
        }
        update_opportunity(req.opportunity_id, update_payload)
        
        task_desc = f"Please review and send this drafted email to {req.decision_maker_name}:\n\n{req.draft_email_body}"
        task_id = create_draft_task(req.opportunity_id, req.draft_email_subject, task_desc, owner_id=req.owner_id)
        
        return {"success": True, "task_id": task_id, "message": "CRM perfectly updated."}
        
    except Exception as e:
        print(f"Server Error during commit: {e}")
        raise HTTPException(status_code=500, detail=str(e))
