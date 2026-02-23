# Product Requirements Document (PRD): AI Sales Agent

**Product Name:** Next.js + FastAPI Sales Agent
**Core Integrations:** Microsoft Dynamics 365 Sales (Dataverse Web API), Azure AI Foundry (gpt-4o)
**Version:** v1.0 (Production)
**Author:** Ajit G

---

## 1. Product Vision & Overview
The AI Sales Agent is an intelligent MLOps workflow application designed to automate the administrative overhead of B2B sales. By deeply integrating with Dynamics 365 Sales, the Agent autonomously updates CRM records, drafts follow-ups, and proactively coaches sellers on pipeline execution. It operates across three distinct Workstreams.

## 2. Workstream 1: "Meeting-to-CRM" Loop
**Goal:** Automate post-meeting deal management so sellers focus on closing deals rather than data entry.

### User Flow
1. **Transcript Input:** The seller logs into the Next.js application, pastes a raw meeting transcript into the designated input area, and clicks "Process."
2. **Entity Detection:** The Python backend analyzes the text via Azure OpenAI to identify the exact Dynamics 365 Opportunity being discussed based on contextual clues (Topic, Account Name, Contact Persons).
3. **Data Extraction & Formatting:** The AI extracts key sales parameters (Budget, Est. Revenue, Timeline, Decision Maker) and generates a Meeting Summary alongside a Follow-Up Email Draft.
4. **Pre-Update UI Presentation:** Before updating the CRM database, the UI prevents hallucination by presenting a strict Review Screen showing the AI-generated assets and a "Before & After" diff comparing the *Existing Values* in D365 versus the proposed *New Values*.
5. **CRM Commit:** Upon successful user confirmation, the system executes a Dataverse PATCH request modifying the Opportunity record and POSTs a new Activity Task containing the email draft assigned to the seller's "My Work" queue.

---

## 3. Workstream 2: Daily Briefing Engine
**Goal:** Replace raw CRM list-views with a prioritized, coaching-oriented "Morning Action Plan" using the Eisenhower Matrix.

### User Flow
1. A seller clicks "Generate Daily Briefing" in the Next.js dashboard.
2. The Python backend pulls all Open Opportunities in the pipeline via the Dataverse Web API.
3. The server runs **Deterministic Analytics (Python)** to calculate pipeline percentiles and mathematically categorize active deals into strategic modules (Prioritized Deals, Quick Wins, Blocked Deals) based on probability, value, age, and modification dates.
4. The structured data is passed to Azure AI Foundry exclusively for formatting and *Meeting Intelligence* (summarizing the calendar appointments for the day).
5. The UI renders a beautiful, structured B2B Markdown report with actionable insights.

---

## 4. Workstream 3: Data Hygiene Monitor (Silent Risks)
**Goal:** Proactively identify stalled, blocked, and high-risk deals sitting "silently" in the CRM that require immediate corrective action, without corrupting the broader Daily Briefing report.

### User Flow
1. The user navigates to the distinct "Silent Risks" tab in the UI.
2. The specialized `/api/silent-risks` backend fetches Open Opportunities and applies strict heuristic thresholds:
   - **Blocked on You:** >50% probability, late stage, 0 activity > 3 days.
   - **High-Risk Enterprise Deals:** Top 25% pipeline value, 0 activity > 7 days.
   - **Verified Zombie Deals:** Proposal/Negotiation stage, 0 activity > 14 days.
3. The JSON threshold data is passed to an elite Azure Sales Operations AI Manager prompt.
4. The AI returns a highly focused Markdown report prescribing exact, tactical **Corrective Actions** for the seller to execute *today* to unblock each identified deal.
