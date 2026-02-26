# AI Sales Agent

**A Next.js & FastAPI workflow application that automates B2B sales administration using Azure AI Foundry and Microsoft Dynamics 365 Dataverse.**

## 🌟 Overview

The AI Sales Agent acts as an intelligent Revenue Copilot directly inside your workflow. It solves the critical problem of CRM data stagnation by providing three core functionalities:

1. **Meeting-to-CRM Loop**: Paste a raw meeting transcript (Teams/Zoom) and the AI will extract the target Dynamics 365 Opportunity, compare existing CRM data against the transcript, draft an executive summary, and write a personalized follow-up email.
2. **Daily Briefing**: Instantly mathematically analyzes your entire active Dataverse pipeline using the Eisenhower Matrix to generate a prioritized, daily "Morning Action Plan."
3. **Silent Risks Monitor**: Automatically flags "zombie deals" and high-risk enterprise opportunities that require immediate corrective action based on heuristic velocity analysis.

## 🏗️ Architecture Stack

- **Frontend**: Next.js 15 (React), Tailwind CSS, Framer Motion
- **Backend (Serverless API)**: FastAPI (Python 3.10+) 
- **AI Engine**: Azure AI Foundry (OpenAI GPT-4o)
- **CRM Integration**: Microsoft Dynamics 365 Sales (Dataverse REST API v9.2)
- **Authentication**: MSAL (Microsoft Authentication Library) Server-to-Server App Flow

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Node.js > 18.x
- Python 3.10+
- A Microsoft Entra ID (Azure AD) App Registration with `Dataverse.User` Impersonation access.
- An Azure Open AI resource with a deployed GPT-4o model.

### 2. Environment Variables
Create a `.env` file in the root directory duplicating the `.env.example` file (you will need to provide your own Azure and Dataverse tenant credentials):

```ini
D365_TENANT_ID=your_tenant_id
D365_CLIENT_ID=your_client_id
D365_CLIENT_SECRET=your_client_secret
D365_RESOURCE=your_org_url

AZURE_OPENAI_ENDPOINT=your_endpoint_url
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 3. Start the Backend (FastAPI)
The backend runs locally via Uvicorn.
```bash
# 1. Create and activate a virtual environment
python3 -m venv api/venv
source api/venv/bin/activate

# 2. Install dependencies
pip install -r api/requirements.txt

# 3. Boot Uvicorn Server (Port 8000)
cd api
uvicorn index:app --reload
```

### 4. Start the Frontend (Next.js)
In a separate terminal window:
```bash
# 1. Install Node dependencies
npm install

# 2. Start Next.js Development Server (Port 3000)
npm run dev
```

Navigate to `http://localhost:3000` to interact with the dashboard.

---

## 📂 Core Folder Structure

The application is heavily modularized for production maintainability:

```text
/
├── src/
│   ├── app/page.tsx               # Main Route & Tab Manager
│   ├── components/                # Modular React UI views (MeetingLoop, DailyBriefing, etc.)
│   ├── hooks/                     # Custom React hooks containing all networking state
│   └── types/                     # Shared TypeScript interfaces
├── api/
│   ├── index.py                   # FastAPI Application Entrypoint
│   ├── routers/                   # Isolated API endpoints (meeting, briefing, risks)
│   ├── services/llm_service.py    # Centralized Azure OpenAI prompting logic
│   ├── clients/d365_client.py     # Dataverse REST API Integration
│   ├── utils/                     # Shared deterministic math & date parsers
│   └── scripts/                   # Dummy CRM data seeding utilities
```

## 📚 Documentation
For detailed structural reading, please reference:
- `PRD_1_Meeting_Loop.md`: The core meeting-to-CRM automation requirements.
- `PRD_2_Daily_Briefing.md`: Pipeline dashboard and Eisenhower Matrix logic.
- `PRD_3_Silent_Risks.md`: Stagnation heuristic monitoring logic.
- `architecture.md`: Detailed breakdown of the Dataverse authentication sequence and frontend/backend separation of concerns.
