# AI Sales Agent: Demo Walkthrough & Architecture

This document serves as your guide for live demo sessions. It outlines exactly how to execute the application and provides strategic talking points regarding the final production-grade architecture.

---

## 1. The Live Execution (10 Minutes)

### Step 1: Initialize the Environment
*Start by showing how easily the full-stack application boots up.*
1. Open terminal and run the backend: `cd api && source venv/bin/activate && uvicorn index:app --reload`
2. Open another terminal and run the frontend: `npm run dev`
3. Navigate to **`http://localhost:3000`** to showcase the Next.js Dashboard.

### Step 2: Workstream 2 - Proactive Pipeline Intelligence
*Demonstrate the Daily Briefing engine.*
1. Navigate to the **"Daily Briefing"** tab in the UI.
2. Click **"Generate Daily Briefing"**. 
3. **Explain the background process:** 
   * *"Our FastAPI backend (`/api/briefing`) just queried the live Dataverse Web API for all open opportunities."*
   * *"The Python server executed mathematical percentiles to categorize the pipeline, then securely passed that payload to our Azure AI Foundry Agent (GPT-4o)."*
4. **Showcase the output:** Point out the dynamically rendered Markdown report grouping deals into `Prioritized Deals`, `Quick Wins`, and `Blocked Deals`.

### Step 3: Workstream 1 - The "Meeting-to-CRM" Loop
*Show the interactive, human-in-the-loop sales flow.*
1. Switch to the **"Meeting to CRM"** tab.
2. Click **"Load Dummy Target"** to paste a pre-formatted transcript into the text area.
3. Click **"Analyze Pipeline Data"**.
4. **Explain the extraction:**
   * *"The Azure Agent processed the transcript against the live D365 Opportunity list and definitively matched the record."*
5. **Showcase the "Review & Commit" Screen:**
   * Highlight the **Meeting Summary** and **Draft Email**.
   * Emphasize the **CRM Field Updates** visual diff (e.g., crossing out existing data and replacing it with newly extracted budgets/dates).
   * *"This UI completely blocks AI hallucinations from entering the CRM. The user must manually review the diffs and click approve."*
6. Click **"Approve & Push to D365"**. Wait for the success animation to confirm the PATCH requests resolved successfully.

### Step 4: Workstream 3 - Data Hygiene Monitor
*Conclude with the administrative oversight flow.*
1. Switch to the **"Silent Risks"** tab.
2. Click **"Scan Pipeline for Silent Risks"**.
3. Point out how this tab uses strict heuristic rules (e.g., >7 days inactive) rather than generative guessing to flag "Zombie Deals" and "High-Risk Enterprise" opportunities.

---

## 2. Architectural Reasoning (5 Minutes)

**Question:** *Why did you migrate from a Python CLI prototype to this Next.js/FastAPI stack?*

**Your Answer:**
> "To achieve enterprise production readiness. A Python CLI is great for rapid API testing, but unacceptable for end-user sales teams. 
> By migrating to **Next.js (React)**, we provided a beautiful, interactive, and strictly gated UI to prevent AI hallucinations from poisoning our Dataverse instance. 
> Simultaneously, extracting the Python logic into **FastAPI Serverless Routers** (`api/routers/`) and explicit service layers (`api/services/llm_service.py`) ensures our Microsoft Authentication (MSAL) and Dataverse REST calls remain hyper-secure and mathematically deterministic on the server side, away from the browser."

**Question:** *Explain the "Human-in-the-Loop" design for email and CRM approvals.*

**Your Answer:**
> "In Workstream 1, the AI extracts changes, but intentionally **does not commit them autonomously**. 
> Instead, our Next.js UI freezes on a 'Review' diff screen. Even when approved, the Python backend doesn't email the client. It makes a `POST` request to the Dataverse API to create an `Open (Draft)` Task assigned explicitly to the seller's 'My Work' queue. The human seller remains the final gatekeeper for external communication."

---

## 3. Product Strategy & ROI (5 Minutes)

**Question:** *Quantify the time saved: How many "non-selling" hours does this specific build eliminate for a rep?*

**Your Answer:**
> "Based on typical B2B sales metrics:
> - **Workstream 1 (Post-Meeting):** Reps spend ~15 minutes after every call updating CRM fields and drafting tailored follow-ups. For an average of 10 meetings a week, this automation saves **2.5 hours per week**.
> - **Workstream 2 (Pipeline review):** Account Executives spend at least 1-2 hours a week manually reviewing stalled deals. The Daily Briefing delivers that intelligence instantly every morning, saving another **1.5 hours per week**.
> 
> **Total ROI:** We are returning approximately **4 hours per week (10% of their selling capacity)** back to the rep to focus purely on revenue generation."
