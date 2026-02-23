import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from api.clients.d365_client import get_opportunities
from api.services.llm_service import get_ai_client, DEPLOYMENT_NAME
from api.utils.date_utils import parse_date

router = APIRouter()

@router.get("/api/silent-risks")
def generate_silent_risks():
    """
    WORKSTREAM 3: DATA HYGIENE MONITORING (SILENT RISKS)
    Pulls Open Opportunities, evaluates against 3 risk heuristics (High Risk >7 days,
    Blocked >3 days, Zombies >14 days), and formats via Azure AI with explicit
    Corrective Action recommendations for the seller.
    """
    try:
        opps = get_opportunities()
        
        valid_opps = [o for o in opps if o.get('estimatedvalue')]
        all_values = sorted([o['estimatedvalue'] for o in valid_opps])
        top_25_deal_size = all_values[int(len(all_values) * 0.75)] if all_values else 0

        m2_blocked = []
        m4_high_risk = []
        m7_zombies = []

        today = datetime.now()
        
        for opp in opps:
            name = opp.get("name") or "Unknown"
            value = opp.get("estimatedvalue") or 0
            prob = opp.get("closeprobability") or 0
            stage = opp.get("salesstagecode") or 1 
            
            modified_date = parse_date(opp.get("modifiedon"))
            days_since_active = (today - modified_date).days if modified_date else 999
            
            if prob >= 50 and stage > 1 and days_since_active > 3:
                m2_blocked.append(f"{name} - Probability ({prob}%) Deal in late stage with NO ACTIVITY in {days_since_active} days.")
                
            if value >= top_25_deal_size and days_since_active > 7:
                m4_high_risk.append(f"{name} - Large Deal (${value:,.0f}) with NO ACTIVITY in {days_since_active} days.")

            if stage > 1 and days_since_active > 14:
                m7_zombies.append({"name": name, "stage": stage, "days_inactive": days_since_active})

        client = get_ai_client()
        system_prompt = f"""
        You are an elite Sales Operations AI Manager. You are conducting a Data Hygiene Review on the CRM pipeline.
        
        Your ONLY job is to take the raw JSON data provided and format it into a stunning Markdown report focused entirely on SILENT RISKS.
        For EVERY single risk surfaced, you MUST prescribe a specific, tactical "Corrective Action" for the seller to execute today to unblock the deal.
        
        CRITICAL FORMATTING RULES:
        1. You MUST include a single italicized sentence directly below each Module's Header explaining the logic used to calculate it.
        2. Do NOT use standard bullet points. Use tables wherever instructed.
        
        OUTPUT STRUCTURE REQUIRED:
        # 🚦 Silent Risks & Data Hygiene Monitor

        ## 🛑 Blocked on You
        *Logic: High probability deals (>50%) in late stages with no outbound task activity > 3 days.*
        <Format m2_blocked as bullets displaying the deal info, followed by a bold **Corrective Action:** suggesting how to unblock it.>

        ## ⚠️ High-Risk Enterprise Deals
        *Logic: Deals in top 25% of pipeline value with > 7 days of complete inactivity.*
        <Format m4_high_risk as a Markdown Table: Account | Est. Revenue | Days Inactive | Corrective Action>

        ## 🧟 Verified Zombie Deals
        *Logic: Deals stuck in Proposal/Negotiation stage with 0 activity in > 14 days.*
        <Format m7_zombies as a Markdown Table: Account | Stage | Days Inactive | Recommended Next Step>
        
        PRE-CALCULATED JSON DATA TO FORMAT:
        {json.dumps({
            "m2_blocked": m2_blocked,
            "m4_high_risk": m4_high_risk,
            "m7_zombies": m7_zombies
        }, indent=2)}
        """

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Format the Silent Risks Data Hygiene report."}
            ],
            temperature=0.4
        )
        
        return {"success": True, "markdown": response.choices[0].message.content}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Server Error during silent risks generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
