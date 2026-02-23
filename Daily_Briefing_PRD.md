# AI Revenue Copilot -- Daily Briefing Tool PRD

**Product Name:** Daily briefing tool\
**CRM:** Microsoft Dynamics 365 Sales\
**Version:** v1.0\
**Author:** Ajit G

------------------------------------------------------------------------

# 1. Product Vision

## Problem
CRMs (like Microsoft Dynamics 365 Sales) track data but do not:
-   Prioritize revenue work
-   Surface deal risks clearly
-   Show personal bottlenecks
-   Provide strategic deal coaching

Sales representatives spend too much time navigating raw data rather than selling.

## Goal
The Daily Briefing tool is a prioritization and execution engine built on top of Dynamics 365 Sales. Every morning, a rep should see:

> "If you only do 5 things today, do these."

This product transforms raw CRM data into revenue-focused, actionable intelligence.

## Target Users
Primary:
-   Account Executives (Mid-Market / Enterprise)
-   SMB Sales Reps

------------------------------------------------------------------------

# 2. Strategic Framework: Eisenhower Matrix for Sales

We use the **Eisenhower Matrix (Urgent vs Important)** to structure
prioritization.

## Quadrants Applied to Sales

### Q1 -- Urgent + Important (DO FIRST)

High-value deals closing soon, blocked items, revenue-critical actions.

→ Implemented via: - Revenue Prioritization Engine - Blocked on You
Module - High-Risk Large Deals

### Q2 -- Important + Not Urgent (PLAN)

Strategic accounts, pipeline building, future risk detection.

→ Implemented via: - Pipeline Health Snapshot - AI Deal Coaching

### Q3 -- Urgent + Not Important (DELEGATE / QUICK WINS)

Small but near-close deals.

→ Implemented via: - Quick Wins Module

### Q4 -- Not Urgent + Not Important (ELIMINATE)

Zombie deals, stalled opportunities.

→ Implemented via: - Stalled Deal Detection

------------------------------------------------------------------------

# 3. Modules Overview

## Module 1: Revenue Prioritization Engine

### Objective

Rank opportunities by expected revenue impact if action is taken today.

### Data Used (Opportunity Entity)

-   estimatedvalue
-   estimatedclosedate
-   probability
-   salesstage
-   modifiedon
-   ownerid
-   decisionmakeridentified (custom)
-   nextstep (custom)

### Scoring Logic

Urgency Score = - Deal Size Weight - Close Date Proximity - Days Since
Last Activity - Probability - Stage Weight - Engagement Gap

Example Weights: - Close date \< 14 days → +20 - No activity \> 5 days →
+15 - Deal \> 75th percentile → +25 - No next step → +15

Output: Top 5 ranked deals.

### Sample ranked list 

| Rank | Account | Why Now? | Revenue | Action |
| --- | --- | --- | --- | --- |
| 1 | ABC Corp | Proposal sent, no follow-up in 4 days | ₹18L | Call DM |
| 2 | Wholesome Cafe | Budget confirmed, demo done | ₹42K | Send final quote |
| 3 | XYZ Ltd | Legal stuck, needs your approval | ₹32L | Review contract |


------------------------------------------------------------------------

## Module 2: Blocked on You

### Objective

Detect deals where rep is bottleneck.

### Logic

Case 1: - probability \> 50% - nextstep is null - stage beyond
qualification

Case 2: - Quote exists - Quote state = Draft - Created \> 2 days ago

Case 3: - Customer email received - No outbound activity in 48h

Output: Flagged deals list.

### Sample output like

4 deals blocked because of you
	•	ABC Corp – Proposal drafted but not sent
	•	FinTech Ltd – Contract not reviewed (3 days)
	•	Nova Retail – No next meeting scheduled

------------------------------------------------------------------------

## Module 3: Quick Wins

### Logic

-   Probability \> 70%
-   Deal size below median
-   Close date within 14 days
-   Recent activity within 3 days

Sorted by close date proximity.

### Sample like

'3 deals likely to close in 7 days if followed up' and then show the quick wins.

| Rank | Account | Why Now? | Revenue | Action |
| --- | --- | --- | --- | --- |
| 1 | ABC Corp | Proposal sent, no follow-up in 4 days | ₹18L | Call DM |
| 2 | Wholesome Cafe | Budget confirmed, demo done | ₹42K | Send final quote |
| 3 | XYZ Ltd | Legal stuck, needs your approval | ₹32L | Review contract |


------------------------------------------------------------------------

## Module 4: High-Risk Large Deals

### Logic

-   Deal value in top 25% AND
-   No activity \> 5 days OR
-   No decision maker identified OR
-   Close date \< 14 days and no proposal sent

Flag as red-risk.

------------------------------------------------------------------------

## Module 5: Meeting Intelligence

### Data Sources

Appointment Entity: - scheduledstart - regardingobjectid -
requiredattendees

Pull linked opportunity data and recent notes.

### AI System Prompt

You are a B2B sales assistant. Summarize: 1. Current deal stage 2. Key
objections 3. Stakeholders 4. Meeting objective 5. Suggested closing
move

### Funda

Not just calendar.

For each meeting:
	•	Deal size
	•	Stage
	•	Stakeholders attending
	•	Last conversation summary
	•	Objections raised
	•	Recommended next step

Example:

3:00 PM – Wholesome Cafe (Demo)
Stage: Evaluation
Budget: ₹35–45K
Concern: After-sales support
Suggested goal: Secure verbal commitment

This saves prep time.

------------------------------------------------------------------------

## Module 6: Pipeline Health Snapshot

### Metrics

-   Total open pipeline
-   Weighted forecast
-   \% to quota (from user profile)
-   Slippage risk (close this month + no activity in 7 days)

### Example


You are 68% to quota.
You need ₹12L more booked this month.
3 late-stage deals can cover this.


------------------------------------------------------------------------

## Module 7: Stalled Deals

### Logic

-   No activity \> 14 days
-   Stage in Proposal/Negotiation
-   State = Open

Flag as Zombie Deals.

------------------------------------------------------------------------

# 4. AI Usage Strategy

AI is used for: - Summarization - Risk explanation - Strategic
coaching - Email drafting

AI is NOT used for: - Raw scoring - Deterministic ranking - Numerical
filtering
------------------------------------------------------------------------

# 5. User Experience & Workflow

## Start Trigger
-   The solution will integrate directly into the Next.js web application.
-   The UI will feature a highly visible **"Generate Daily Briefing"** button on the seller's dashboard or navigation bar.
-   **Action:** When clicked, the backend immediately queries Dynamics 365 for all open opportunities, activities, and tasks owned by the current seller.

## Processing & Output
-   **Processing State:** While the Azure AI Foundry (GPT-4o) agent analyzes the pipeline, scores the deals, and synthesizes the briefing, the UI will display dynamic loading steps (e.g., "Analyzing your pipeline...", "Detecting blocked deals...", "Generating meeting prep...").
-   **Output View:** The generated brief is rendered in a beautiful, categorized dashboard directly on the UI using Markdown so the rep can easily consume the ranked deals, quick wins, and meeting intelligence blocks.

------------------------------------------------------------------------

# 6. Success Metrics

-   Increased win rate
-   Reduced sales cycle length
-   Improved quota attainment
-   Reduced deal slippage
-   Higher daily focused activity

------------------------------------------------------------------------

This document defines the functional and technical blueprint for
building an AI-powered Daily Revenue Briefing tool on Dynamics 365
Sales.
