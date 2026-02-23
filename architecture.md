# AI Sales Agent: Architecture Document

## 1. Overview
The goal of this architecture is to transition the "Meeting-to-CRM" loop from a local Python script into a production-grade web application. The design prioritizes scalability, security (Server-to-Server Dynamics 365 authentication), and a seamless, modern user interface.

## 2. Technology Stack

### **Frontend Framework: Next.js (React)**
- *Why Next.js over Streamlit?* While Streamlit is excellent for rapid data science prototypes, it is heavily opinionated and limits UI/UX customization. Next.js is the industry standard for production-grade web applications. It allows us to build a stunning, highly responsive, tailored user interface using **React** and **Tailwind CSS**. It also provides fantastic loading states and error handling, critical for a great user experience.

### **Backend Framework: Python Serverless Functions (FastAPI/Vercel APIs)**
- We will retain our core Python logic (AI calls, MSAL authentication, Dataverse API integration) but package it as **Serverless API Routes**.
- The Next.js frontend will make secured HTTP requests to these Python endpoints when the user clicks "Process".

### **AI Orchestration: Azure AI Foundry**
- **Model:** GPT-4o
- **SDK:** `openai` (AzureOpenAI client)
- *Workflow:* Structured JSON extraction via strong system prompts and schemas to guarantee exact data adherence for the CRM.

### **CRM Integration: Dynamics 365 Sales (Dataverse)**
- **Authentication:** MSAL (Microsoft Authentication Library) using Client Credentials Flow (Service Principal/App Registration).
- **Communication:** Standard REST requests to the `v9.2` Dataverse Web API.

### **Hosting & Deployment: Vercel**
- *Why Vercel?* Vercel seamlessly hosts Next.js applications and simultaneously supports deploying Python scripts as serverless backend functions in the exact same repository. This eliminates the need to manage two separate servers (e.g., a separate Heroku backend and Netlify front-end) and provides built-in CI/CD via GitHub.

---

## 3. Workflow & Data Sequence (Two-Step API)

1. **Client Event (Analysis phase):** The user pastes their meeting transcript into the Next.js UI and submits.
2. **API Request 1 (`/api/analyze`):** The React frontend sends the transcript string.
3. **Pipeline Hydration:** The Python backend securely authenticates via MSAL and makes a `GET` request to Dynamics 365 to download the current state of the pipeline (active Opportunity names, IDs, Owners, and existing values for Budget/Revenue/Date).
4. **Agentic Inference:** 
   - The Python backend sends the transcript + pipeline names to the Azure AI Foundry GPT-4o model.
   - The Agent returns a structured JSON payload containing the matched Opportunity Name, Meeting Summary, Budget, Est. Revenue, Date, and drafted Email.
5. **Logic Gate & UI Presentation:** 
   - The backend validates the Opportunity. It responds to the UI with the *Existing Values* from D365 alongside the *Proposed New Values*, the meeting summary, and the email draft.
   - If no opportunity matched exactly, it responds with the list of active opportunities for the user to manually select via a dropdown.
   - The Next.js UI renders the "Before & After" diff, Summary, and Draft Email for human review.
6. **Client Event (Commit phase):** The user visually verifies the data and clicks "Update CRM".
7. **API Request 2 (`/api/commit`):** The React frontend sends the confirmed values to the backend.
8. **CRM Integration:** 
   - The backend makes a `PATCH` request to D365 to update the Opportunity record fields.
   - The backend makes a `POST` request to D365 to create a `Task` Activity, binding both `regardingobjectid_opportunity` and `ownerid` (the human seller).
9. **Client Feedback:** The serverless function successfully resolves, and the Next.js UI displays a success animation.
