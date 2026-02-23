# Product Requirements Document (PRD): AI Sales Agent

## 1. Overview
The AI Sales Agent is an intelligent workflow application designed to automate the administrative overhead of post-meeting deal management ("Meeting-to-CRM" loop). By analyzing raw meeting transcripts, the Agent autonomously updates CRM records and drafts personalized follow-up communications, allowing sellers to focus on closing deals rather than data entry.

## 2. In Scope
This PRD covers **Workstream 1** of the product vision, focusing entirely on migrating the prototype into a production-grade, secure, and scalable web application.

## 3. User Flow

1. **Transcript Input (UI):** 
   - The user (seller) logs into the application and is presented with a clean, modern interface.
   - The user pastes or uploads a meeting transcript into the designated input area and clicks "Process."

2. **Opportunity Detection:**
   - The Agent analyzes the transcript to identify the exact Dynamics 365 Opportunity being discussed based on contextual clues (Topic, Account Name, Contact Persons).
   - *Graceful Fallback & Override:* If no exact match is found (or if the AI has low confidence), the UI will display a warning and provide a dropdown menu containing all active Dynamics 365 Opportunities. The user can manually select the correct Opportunity to resume the workflow.

3. **Data Extraction, Analysis & UI Review:**
   - The Agent extracts key sales parameters from the transcript (Budget, Est. Revenue, Timeline, Decision Maker).
   - The Agent generates a **Brief Summary** of the meeting.
   - The Agent generates a **Personalized Follow-Up Email Draft**.
   - **Pre-Update UI Presentation:** Before updating the CRM database, the UI will present the user with a comprehensive review screen showing:
     - The AI-generated Meeting Summary.
     - The AI-generated Follow-Up Email Draft.
     - A "Before & After" comparative view showing the *Existing Values* of the D365 Opportunity fields versus the *New Values* being proposed by the AI.

4. **CRM Update & Human-in-the-Loop Activity Creation:**
   - Upon successful execution (or user confirmation, if configured), the system patches the new parameters onto the matched Opportunity record in Dynamics 365.
   - The system creates a new `Task` (Activity) in Dynamics 365 containing the drafted email.
   - *Crucial Linking:* The Task is bound to the target Opportunity (appearing in its Timeline) AND explicitly assigned to the Opportunity's human Owner. This ensures the draft correctly appears in the seller's personal **"My Work" -> "Activities"** queue.
   - The seller reviews the drafted task natively in Dynamics 365, makes any desired edits, and executes the formal send.
