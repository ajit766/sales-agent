import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from api.clients.d365_client import get_opportunities, get_todays_appointments
from api.services.llm_service import get_ai_client, DEPLOYMENT_NAME
from api.utils.date_utils import parse_date
from api.utils.math_utils import calculate_pipeline_metrics

router = APIRouter()

@router.get("/api/briefing")
def generate_daily_briefing():
    """Workstream 2: Generates a proactive daily briefing using custom deterministic Python logic."""
    try:
        opps = get_opportunities()
        if not opps:
            raise HTTPException(status_code=404, detail="No open opportunities found in Dynamics 365 pipeline.")

        today = datetime.now()
        metrics = calculate_pipeline_metrics(opps)
        
        top_25_deal_size = metrics["top_25_deal_size"]
        median_deal_size = metrics["median_deal_size"]
        total_open_pipeline = metrics["total_open_pipeline"]
        weighted_forecast = metrics["weighted_forecast"]

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
            stage = opp.get("salesstagecode") or 1 
            
            close_date = parse_date(opp.get("estimatedclosedate"))
            modified_date = parse_date(opp.get("modifiedon"))
            
            days_to_close = (close_date - today).days if close_date else 999
            days_since_active = (today - modified_date).days if modified_date else 999
            
            score = 0
            if days_to_close < 14: score += 20
            if days_since_active > 5: score += 15
            if value >= top_25_deal_size: score += 25
            m1_prioritized.append({"name": name, "score": score, "revenue": value, "days_since_active": days_since_active, "why_now": f"No activity in {days_since_active} days" if days_since_active < 999 else "No recent activity"})
            
            if prob >= 50 and stage > 1 and days_since_active > 3:
                m2_blocked.append(f"{name} - High probability ({prob}%) in late stage with no activity in {days_since_active} days.")
                
            if prob >= 70 and value <= median_deal_size and days_to_close < 14:
                m3_quick_wins.append({"name": name, "revenue": value, "why_now": f"Closing in {days_to_close} days"})
                
            if value >= top_25_deal_size and (days_since_active > 5 or days_to_close < 14):
                m4_high_risk.append(f"{name} - Large Deal (${value:,.0f}). Closing in {days_to_close} days with no activity in {days_since_active} days.")
                
            if days_since_active > 14 and stage > 1:
                m7_zombies.append(f"{name} - No activity in {days_since_active} days. Consider closing out.")

        todays_appointments = get_todays_appointments()
        for appt in todays_appointments:
            subj = appt.get("subject", "Meeting")
            desc = appt.get("description", "")
            time_start = appt.get("scheduledstart", "")
            
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

        m1_prioritized = sorted(m1_prioritized, key=lambda x: x["score"], reverse=True)[:5]
        m3_quick_wins = sorted(m3_quick_wins, key=lambda x: x["revenue"], reverse=True)

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
