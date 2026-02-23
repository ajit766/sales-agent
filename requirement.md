Assignment: Director of Product
Objective
Build and demonstrate a functional AI Sales Agent prototype that automates the lifecycle of
a deal—from meeting intelligence to proactive pipeline management—using the Microsoft
ecosystem (D365, Azure AI Foundry, and Copilot Studio).
The Build Requirement
You are required to configure a "Builder's Prototype" that addresses the following two
high-impact workstreams:
Workstream 1: The "Meeting-to-CRM" Loop
●
Note-taking & CRM Updates: Input a meeting transcript. The agent must
summarise the interaction and automatically detect/update missing fields (e.g.,
Budget, Timeline, or Decision Maker) in a D365 Lead or Opportunity record.
●
Email & Task Generation: The agent must generate a personalised follow-up email
draft and create a CRM "Task" for the seller to approve/execute.
Workstream 2: Proactive Pipeline Intelligence
●
Actionable Daily Briefs: Configure the agent to "read" a mock pipeline (3–5 deals).
It must generate a short daily brief highlighting high-value insights (e.g.,
"Deal X is
stalling at Stage 2; suggest reaching out to the VP of Finance").
●
Data Hygiene Monitoring: The agent must identify "silent" risks—such as a deal
with a high value but no activity for 7 days—and recommend a corrective action to
the seller.
Technical Instructions & Resources
●
●
●
Orchestration: Use Microsoft Copilot Studio or Azure AI Foundry (Agent
Service).
Integration: Use the D365/Dataverse Connector for reading/writing records.
Reference Materials: Utilize Microsoft’s Agent SDK or Azure AI Foundry
Quickstarts.
The Demo Session (20 Minutes)
Your submission will be evaluated during a live session structured as follows:
1. The Live Execution (10 Minutes):
○
Trigger the "Daily Brief" and "Data Hygiene" alert for a mock pipeline.
○
Run the "Meeting-to-CRM" loop: Input a transcript, see the D365 update, &
Review the email draft.
○
Note: If a live API error occurs, you may use a pre-recorded screen capture,
but the backend logic must be walked through live.
2. Architectural Reasoning (5 Minutes):
○
Explain your choice of tools (e.g., why this specific orchestration layer?).
○
Discuss the "Human-in-the-Loop" design for email and CRM approvals.
3. Product Strategy & ROI (5 Minutes):
○
How do you handle "Conflicting Data" (e.g., The transcript says one thing, the
CRM says another)?
○
Quantify the time saved: How many "non-selling" hours does this specific
build eliminate for a rep?
Assumptions & Constraints
●
Environment: Use a Microsoft Developer Program 90-day trial or a Personal Azure
Sandbox. Beacon will not provide a tenant for this prototype.
●
Data: Use dummy sales data
●
Scope: Focus on functional orchestration and "Agentic" reasoning over a polished
UI.