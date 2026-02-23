# AI Sales Agent Prototype Implementation Plan

## Goal Description
Build a functional AI Sales Agent prototype that automates the lifecycle of a deal using the Microsoft ecosystem (D365 and Azure AI Foundry). The prototype will address two workstreams: 
1. The "Meeting-to-CRM" Loop (Summarize transcripts, update D365, draft emails & tasks).
2. Proactive Pipeline Intelligence (Generate daily briefs, identify silent risks).

## Proposed Changes

### Architecture Strategy: All-In on Azure AI Foundry

We are taking a pro-code approach, utilizing **Azure AI Foundry (Agent Service)** as the orchestration engine for *both* workstreams. This provides maximum control, flexibility, and a unified architecture.

While Workstream 1 *could* be built in Copilot Studio, building it entirely in Python with Azure AI Foundry demonstrates deep technical competency and allows for more sophisticated "Agentic" reasoning patterns (like tool calling/function calling).

#### Core Technologies
1.  **Language:** Python
2.  **LLM Backend:** Azure AI Foundry (using `azure-ai-projects` SDK) or direct Azure OpenAI Service if the Agent Service is not yet available in your region.
3.  **Data Layer:** Dynamics 365 Dataverse Web API
4.  **Authentication:** Microsoft Authentication Library (MSAL) using a Server-to-Server (S2S) App Registration (Service Principal).

#### Workstream 1: The "Meeting-to-CRM" Loop (Azure AI Foundry + Python)
*   **The Flow:** We will write a Python script that takes a raw meeting transcript as input.
*   **Agentic Extraction:** The script will send the transcript to the Foundry Agent with a strong system prompt, instructing it to extract `Budget`, `Timeline`, and `Decision Maker`, and output the result as a structured JSON object.
*   **D365 Integration:** The script will parse the JSON and use the `requests` library to make a `PATCH` request to the Dataverse Web API, updating the specific Opportunity record.
*   **Draft Task Creation:** In the same execution, the Agent will generate a follow-up email draft. The script will make a `POST` request to Dataverse to create a new `Task` record linked to the Opportunity, containing the drafted email, with its state set to "Open" for human review.

#### Workstream 2: Proactive Pipeline Intelligence (Azure AI Foundry + Python)
*   **The Flow:** A separate Python script designed to run as a scheduled job (e.g., daily cron).
*   **Data Retrieval:** The script will authenticate and send a `GET` request to Dataverse to retrieve all "Open" Opportunities, filtering for key fields and `Last Activity Date`.
*   **Agentic Analysis:** The data payload is passed to the Foundry Agent. The Agent is instructed to identify "stalled" deals (e.g., no activity > 7 days) and generate a formatted "Daily Brief" report with recommended actions.
*   **Output:** The script will print or save the generated Daily Brief (in reality, this might be emailed to the team lead).

## Verification Plan

### Automated Tests
*   N/A - This is a prototype build focused on functional orchestration.

### Manual Verification
1.  **Workstream 1:** Run `process_transcript.py` with a sample text file. Verify in the D365 UI that the target Opportunity fields are updated and a Draft Task is present.
2.  **Workstream 2:** Run `daily_brief.py`. Verify that it correctly queries D365, correctly identifies the "stalled" mock opportunity, and generates a sensible recommendation in the console/output file.
3.  **Demo Readiness:** Run through the 20-minute presentation format defined in the requirements, ensuring both scripts function seamlessly.
