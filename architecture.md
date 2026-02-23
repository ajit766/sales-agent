# AI Sales Agent: Architecture Document

## 1. Overview
The goal of this architecture is to provide a production-grade web application to automate the "Meeting-to-CRM" loop alongside proactive pipeline analytics. The design prioritizes scalability, security (Server-to-Server Dynamics 365 authentication), and a seamless, modern, modular user interface.

## 2. Technology Stack

### **Frontend Framework: Next.js (React)**
The frontend is built with Next.js using App Router conventions. The UI is componentized to separate visual rendering from data management:
- **`src/components/`**: Modularized presentation layers (e.g., `MeetingLoopTab.tsx`, `DailyBriefingTab.tsx`).
- **`src/hooks/`**: Data fetching and state isolation (e.g., `useMeetingAnalysis.ts` orchestrating API calls).
- **Styling**: TailwindCSS with `framer-motion` for micro-interactions.

### **Backend Framework: Python (FastAPI)**
The backend operates entirely on Python, structured around FastAPI routing to handle decoupled complex data workflows in a scalable API format.
- **`api/routers/`**: Separate namespaces isolating different endpoint logic (`meeting_router.py`, `briefing_router.py`).
- **`api/clients/d365_client.py`**: Centralized HTTP client managing MSAL Service Principal authentication to Dynamics 365.
- **`api/services/llm_service.py`**: Encapsulates all Azure OpenAI connectivity, model configuration, and prompt construction.

### **AI Orchestration: Azure AI Foundry**
- **Model:** GPT-4o
- **SDK:** `openai` (AzureOpenAI client)
- *Workflow:* Structured JSON extraction via strong system prompts and schemas to guarantee exact data adherence for the CRM.

### **CRM Integration: Dynamics 365 Sales (Dataverse)**
- **Authentication:** MSAL (Microsoft Authentication Library) using Client Credentials Flow (Service Principal/App Registration).
- **Communication:** Standard REST requests to the `v9.2` Dataverse Web API.

---

## 3. Workflow & Data Sequence (Two-Step API)

### Example: Meeting-to-CRM Loop (`/api/analyze` & `/api/commit`)

1. **Client Event (Analysis phase):** The user pastes their meeting transcript into the Next.js `MeetingLoopTab` UI.
2. **API Request 1 (`POST /api/analyze`):** The `useMeetingAnalysis` React hook sends the transcript to the FastAPI Router.
3. **Pipeline Hydration:** The Python backend securely authenticates via MSAL and makes a `GET` request to Dynamics 365 to download the current state of the pipeline (active Opportunity names, IDs, Owners, and existing values for Budget/Revenue/Date).
4. **Agentic Inference (`llm_service.py`):** 
   - The Python backend formats the transcript + pipeline names into a dedicated System Prompt directed at Azure AI Foundry GPT-4o.
   - The Agent returns a structured JSON payload containing the matched Opportunity Name, Meeting Summary, Budget, Est. Revenue, Date, and drafted Email.
5. **Logic Gate & UI Presentation:** 
   - The backend validates the Opportunity. It responds to the React UI with the *Existing Values* from D365 alongside the *Proposed New Values*.
   - The UI completely pauses, rendering a "Review & Commit" diff presentation to prevent any AI hallucination injection into the CRM.
6. **Client Event (Commit phase):** The user visually verifies the data and clicks "Approve & Push".
7. **API Request 2 (`POST /api/commit`):** The frontend sends the explicitly confirmed values back to the router backend.
8. **CRM Integration (`d365_client.py`):** 
   - The backend makes a `PATCH` request to D365 to update the Opportunity record fields.
   - The backend makes a `POST` request to D365 to create a new `Task` Activity, securely binding both the `regardingobjectid_opportunity` and the human `ownerid`.

---

## 4. Hosting & Deployment Strategy
- **Frontend**: Easily deployable to modern CDN Edge networks like Vercel or Netlify.
- **Backend**: Can execute on Serverless Platforms (AWS Lambda / Vercel Python Functions) or traditional containerized VM hosting (Docker / Render / Azure App Service). This project uses native Python WSGI standard abstractions.
