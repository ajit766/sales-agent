import os
from datetime import datetime
from dotenv import load_dotenv

# Import AI Client setup directly from Workstream 1
from workstream1 import get_ai_client, DEPLOYMENT_NAME
from d365_client import get_opportunities

load_dotenv()

def generate_daily_brief(opportunities_data):
    """Passes the raw D365 pipeline data to Azure AI Foundry to generate a proactive briefing."""
    client = get_ai_client()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    system_prompt = f"""
    You are an expert Sales Director running a proactive pipeline intelligence briefing.
    Today's date is {current_date}.
    
    You will be provided with a JSON array of active Opportunities from Microsoft Dynamics 365.
    
    Your task:
    1. Analyze the pipeline and identify high-value deals (Budget/Est. Revenue > $0).
    2. Identify 'Silent Risks': Deals that have not been modified/acted upon in the last 7 days (compare the 'modifiedon' date to today's date).
    3. Generate a concise, punchy "Daily Brief" in Markdown format.
       - Include a short summary of the overall pipeline health.
       - Highlight the 1-3 most critical "Stalled Deals" and provide ONE concrete corrective action for the sales rep to take.
    
    Keep the tone professional, urgent, and actionable. Do not output raw JSON, just the Markdown report.
    """
    
    print("Agent: Analyzing D365 Pipeline Data via Azure AI Foundry...")
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the raw D365 Opportunity Data:\n{opportunities_data}"}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

def run_workstream_2():
    print("--- STARTING WORKSTREAM 2: PROACTIVE PIPELINE INTELLIGENCE ---\n")
    
    # 1. Fetch live data from D365
    print("[1] Querying Dynamics 365 for Open Pipeline...")
    try:
        opps = get_opportunities()
        print(f"-> Fetched {len(opps)} active opportunities.")
    except Exception as e:
        print(f"Failed to fetch D365 data: {e}")
        return

    if not opps:
        print("No open opportunities found to analyze.")
        return

    # Clean the data payload to only send what the LLM needs (saves tokens & context window)
    clean_pipeline_data = []
    for opp in opps:
        clean_pipeline_data.append({
            "Name": opp.get("name"),
            "Est_Revenue": opp.get("budgetamount"),
            "Est_Close_Date": opp.get("estimatedclosedate"),
            "Sales_Stage": opp.get("stepname"),
            "Last_Modified_Date": opp.get("modifiedon")
        })

    # 2. Agentic Analysis
    print("\n[2] Generating Daily Intelligence Brief...")
    try:
        daily_brief_markdown = generate_daily_brief(str(clean_pipeline_data))
    except Exception as e:
        print(f"Failed to generate brief via AI: {e}")
        return
        
    # 3. Output the result
    print("\n================ DAILY SALES BRIEF ================\n")
    print(daily_brief_markdown)
    print("\n===================================================\n")
    
    print("--- WORKSTREAM 2 COMPLETE ---")

if __name__ == "__main__":
    run_workstream_2()
