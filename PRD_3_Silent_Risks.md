# Silent Risks (Data Hygiene Monitoring) PRD

## 1. Vision
Provide a dedicated "Data Hygiene Monitoring" tab that specifically surfaces "silent" risks within the Dynamics 365 pipeline. Instead of just listing these deals, the AI agent must proactively recommend a *corrective action* to the seller to help unblock the deal.

## 2. Core Functional Requirements
*   **UI Integration**: Add a third navigation tab titled "Silent Risks" to the main `page.tsx` Header, placed alongside "Meeting to CRM" and "Daily Briefing".
*   **API Endpoint**: Create a new `/api/silent-risks` GET endpoint.
*   **Additive Feature**: **DO NOT change any functionality in the existing Daily Briefing.** The underlying heuristic logic for Blocked Deals, High-Risk Deals, and Zombie Deals will be duplicated and adapted for this new endpoint, leaving the Daily Briefing 100% intact.
*   **AI Action Generation**: The Azure AI Foundry system prompt must be instructed to generate a specific "Corrective Action" column/bullet for each surfaced risk.

## 3. Heuristic Ruleset
The backend Python engine will evaluate all open opportunities against these updated 3 rules:

### A. High-Risk Large Deals (Formerly Module 4)
*   **Logic**: Deals in the top 25% of pipeline value with NO activity for **> 7 days** (updated threshold from 5 to 7 days).
*   **AI Requirement**: Recommend a corrective action (e.g., "Draft an executive summary email to the economic buyer").

### B. Blocked on You (Formerly Module 2)
*   **Logic**: Deals with high win probability (>50%) in late sales stages (Stage > 1) with no outbound task activity > 3 days.
*   **AI Requirement**: Recommend exactly what the seller is blocked on implementing.

### C. Zombie Deals (Formerly Module 7)
*   **Logic**: Deals stuck in Proposal/Negotiation stages (Stage > 1) with NO activity in > 14 days.
*   **AI Requirement**: Suggest a disqualification strategy or a "breakup" email approach.

## 4. UI Layout Specifications
The UX should render cleanly spaced markdown (similar to the Daily Briefing format) using the `<ReactMarkdown>` component:
1.  **High-Risk Accounts**: A table showing `Account | Est. Revenue | Days Inactive | Corrective Action`
2.  **Blocked Deals**: Bullet point list with the block reason and unblocking action.
3.  **Zombie Deals**: Table showing `Account | Stage | Days Inactive | Recommendation`
