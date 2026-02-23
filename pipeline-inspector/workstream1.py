import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

# Import our custom D365 Client methods
from d365_client import get_opportunities, update_opportunity, create_draft_task

load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

def get_ai_client():
    """Initializes the Azure OpenAI Inference client by formatting the Project Endpoint to raw Cognitive Services URL."""
    # Convert https://<resource>.services.ai.azure.com/api/projects/... to https://<resource>.openai.azure.com
    base_endpoint = PROJECT_ENDPOINT.split("/api")[0].replace(".services.ai.azure.com", ".openai.azure.com")
    return AzureOpenAI(
        azure_endpoint=base_endpoint,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-15-preview"
    )

def extract_transcript_data(transcript_text, open_opportunity_names):
    """Uses the Foundry Agent (GPT-4o) to extract structured CRM data and draft an email."""
    client = get_ai_client()
    
    system_prompt = f"""
    You are an expert sales assistant. Read the following meeting transcript.
    You must extract the actionable sales data and return it as a pure JSON object without markdown formatting.
    
    You must also identify which active Opportunity this meeting was regarding. 
    Here is the list of active Opportunity Names in our CRM:
    {open_opportunity_names}
    
    Follow this exact JSON schema:
    {{
        "target_opportunity_name": "<The exact name of the Opportunity from the list above that best matches the transcript context>",
        "budgetamount": <numeric float value of the budget mentioned>,
        "estimatedclosedate": "<YYYY-MM-DD format of the deadline/timeline mentioned>",
        "decision_maker_name": "<name of the decision maker>",
        "draft_email_subject": "<a professional subject line for a follow-up email>",
        "draft_email_body": "<a personalized follow up email thanking them and confirming the details>"
    }}
    """
    
    print("Agent: Analyzing transcript via Azure AI Foundry...")
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
    # Clean up standard markdown wrapping if the LLM adds it
    if result_json.startswith("```json"):
        result_json = result_json[7:-3]
    elif result_json.startswith("```"):
        result_json = result_json[3:-3]
        
    return json.loads(result_json.strip())

def run_workstream_1():
    print("--- STARTING WORKSTREAM 1: MEETING-TO-CRM LOOP ---\n")
    
    # 1. Read the transcript
    with open("dummy_transcript.txt", "r") as f:
        transcript = f.read()
    
    # 2. Querying Dynamics 365 for Open Opportunities first to feed context to AI
    print("[Querying Dynamics 365 for Open Pipeline]")
    opps = get_opportunities()
    if not opps:
        print("No open opportunities found in D365 to update!")
        return
        
    opp_names = [opp.get("name") for opp in opps]
    
    # 3. Extract Data via Azure AI Foundry
    try:
        extracted_data = extract_transcript_data(transcript, opp_names)
        print("\n[AI Extraction Complete]")
        print(f"- Target Opportunity: '{extracted_data.get('target_opportunity_name')}'")
        print(f"- Budget Identified: ${extracted_data.get('budgetamount')}")
        print(f"- Timeline Identified: {extracted_data.get('estimatedclosedate')}")
    except Exception as e:
        print(f"Failed to extract data: {e}")
        return

    # 4. Find target target Opportunity in D365 Data Array
    target_opp_name = extracted_data.get("target_opportunity_name")
    target_opp = next((opp for opp in opps if opp.get("name") == target_opp_name), None)
    
    if not target_opp:
         print(f"CRITICAL ERROR: AI selected an Opportunity ('{target_opp_name}') that doesn't exactly match our CRM.")
         return
         
    opp_id = target_opp.get("opportunityid")
    opp_owner_id = target_opp.get("_ownerid_value")
    
    print(f"\n[Matched Opportunity in Database: ID {opp_id}]")
    
    # 5. Update the Opportunity Record
    print("\n[Updating D365 Opportunity Record]")
    update_payload = {
        "budgetamount": extracted_data.get("budgetamount"),
        "estimatedvalue": extracted_data.get("budgetamount"), # Also update Est. Revenue
        "isrevenuesystemcalculated": False, # Ensure manual override of Revenue is allowed
        "estimatedclosedate": extracted_data.get("estimatedclosedate")
    }
    
    update_opportunity(opp_id, update_payload)
    print("-> Successfully updated Budget, Est. Revenue, and Estimated Close Date!")
    
    # 6. Create the Human-in-the-Loop Draft Task
    print("\n[Creating Draft Follow-up Task for Seller Review]")
    task_subject = f"AI Draft: {extracted_data.get('draft_email_subject')}"
    task_desc = f"Please review and send this drafted email to {extracted_data.get('decision_maker_name')}:\n\n{extracted_data.get('draft_email_body')}"
    
    task_id = create_draft_task(opp_id, task_subject, task_desc, owner_id=opp_owner_id)
    print(f"-> Draft Task created successfully! (Task ID: {task_id})")
    print(f"-> Task bound to human owner ID: {opp_owner_id}")
    
    print("\n--- WORKSTREAM 1 COMPLETE ---")

if __name__ == "__main__":
    run_workstream_1()
