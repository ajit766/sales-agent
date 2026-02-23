# AI Sales Agent Prototype: Demo Walkthrough & Architecture

This document serves as your guide for the 20-minute live demo session. It outlines exactly how to execute the technical build and answers the required strategic questions.

## 1. The Live Execution (10 Minutes)

### Workstream 2: Proactive Pipeline Intelligence
*Start by showing how the AI acts autonomously in the background.*

1.  **Open Dynamics 365 Sales.** Show the "Opportunities" view to ground the audience in the current state of the pipeline.
2.  **Run the script.** Open your terminal in the `pipeline-inspector` directory and execute:
    ```bash
    source venv/bin/activate
    python workstream2.py
    ```
3.  **Explain the output:** 
    *   *"The Python orchestrator just queried the Dataverse Web API for all open opportunities."*
    *   *"It passed that live telemetry to our Azure AI Foundry Agent (GPT-4o) with strict instructions to flag deals inactive for over 7 days."*
    *   *Show the Markdown "Daily Sales Brief" generated in the console, highlighting the specific corrective actions the AI recommended for the stalled deals.*

### Workstream 1: The "Meeting-to-CRM" Loop
*Now show how the AI assists a seller actively.*

1.  **Show the target record:** In D365, open the Opportunity: `"10 Airpot XL Coffee Makers for Alpine Ski House"`. Show that the Budget Amount and Est. Close Date can be modified.
2.  **Show the input:** Open `dummy_transcript.txt`. Point out the conversational mention of the "$5,500 budget" and the "November 15th timeline".
3.  **Run the script.** In the terminal, execute:
    ```bash
    python workstream1.py
    ```
4.  **Explain the output:**
    *   *"The Azure Agent processed the transcript, structured the data into JSON, and our orchestrator automatically patched the Dynamics 365 record using the Dataverse API."*
5.  **Verify in D365:**
    *   Refresh the Opportunity in D365. Show that the **Budget** and **Est. Revenue** now say $5,500, and the **Close Date** is updated.
    *   Navigate to the **Timeline/Activities** section of that Opportunity. Show the newly created **Draft Task** containing the fully drafted follow-up email ready for the seller to review.

---

## 2. Architectural Reasoning (5 Minutes)

**Question:** *Explain your choice of tools (e.g., why this specific orchestration layer?).*

**Your Answer:**
> "I chose a **pro-code architecture** utilizing Python and the **Azure AI Foundry (OpenAI) SDK**, connecting directly to the Dynamics 365 **Dataverse Web API**. 
> 
> While low-code tools like Copilot Studio are excellent for building chat interfaces quickly, this requirement emphasized *Agentic reasoning* and complex background autonomous tasks (like cron-based pipeline monitoring). By building a custom Python orchestrator, I achieved maximum control over the data payload sent to the LLM, ensured strict JSON schema adherence for CRM updates, and laid a foundation that can easily be deployed as an Azure Function or GitHub Action for true enterprise-scale automation."

**Advanced Implementation Detail (Record Ownership vs Context):**
> *If asked about the "My Work" Activities view vs the Opportunity Timeline view:*
> "Because this is an enterprise-grade backend integration using a **Server-to-Server App Registration**, the D365 records are technically 'owned' by the backend application user, not the human seller. That is why the AI's drafted task appears perfectly in the contextual Opportunity Timeline (because it is linked via the `regardingobjectid`), but does not clutter the human rep's personal 'My Work' queue. In a production rollout, the orchestrator would be configured to query the seller's `systemuserid` and dynamically bind the ownership so it routes directly to their personal inbox!"

**Question:** *Discuss the "Human-in-the-Loop" design for email and CRM approvals.*

**Your Answer:**
> "In Workstream 1, the script automatically updates objective data facts (like Budget and Date) to save the seller time. However, it intentionally **does not send the email autonomously**. 
> 
> Instead, the Python script calls the Dataverse API to create a `Task` record with a status of `Open (Draft)`. The AI writes the email, but places it on the seller's D365 dashboard as a task to review. This ensures the human seller remains the final gatekeeper for external client communication, maintaining relationship quality and preventing AI hallucinations from reaching the customer."

---

## 3. Product Strategy & ROI (5 Minutes)

**Question:** *How do you handle "Conflicting Data" (e.g., The transcript says one thing, the CRM says another)?*

**Your Answer:**
> "In a production environment, the orchestrator should be designed to query the current CRM state *before* updating. If the CRM budget is $10k but the transcript says $5k, the script would catch the delta. 
> 
> Instead of silently overwriting the Dataverse record (which we did here in the prototype for speed), the script should generate a different type of Human-in-the-Loop Task: an 'Anomaly Alert'. It would flag the discrepancy to the seller on their dashboard, asking them to explicitly confirm which value is the final source of truth before the database commits the change."

**Question:** *Quantify the time saved: How many "non-selling" hours does this specific build eliminate for a rep?*

**Your Answer:**
> "Based on typical sales metrics:
> - **Workstream 1 (Post-Meeting):** Reps spend ~15 minutes after every call updating CRM fields and drafting tailored follow-ups. For an average of 10 meetings a week, this automation saves **2.5 hours per week**.
> - **Workstream 2 (Pipeline review):** Account Executives spend at least 1-2 hours a week manually reviewing stalled deals and deciding next steps. This Agent delivers that intelligence instantly every morning, saving another **1.5 hours per week**.
> 
> **Total ROI:** We are returning approximately **4 hours per week (10% of their selling capacity)** back to the rep to focus purely on revenue-generating conversations rather than administrative maintenance."
