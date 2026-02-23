import { useState } from "react";
import { AnalysisResponse } from "../types";

export function useMeetingAnalysis() {
    const [transcript, setTranscript] = useState("");
    const [step, setStep] = useState<"input" | "analyzing" | "review" | "committing" | "success" | "error">("input");
    const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
    const [errorMessage, setErrorMessage] = useState("");

    const handleAnalyze = async () => {
        if (!transcript.trim()) return;
        setStep("analyzing");

        try {
            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ transcript }),
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Analysis failed");
            }

            setAnalysisData(data);
            setStep("review");
        } catch (err: any) {
            setErrorMessage(err.message);
            setStep("error");
        }
    };

    const handleCommit = async () => {
        if (!analysisData) return;
        setStep("committing");

        try {
            const payload = {
                opportunity_id: analysisData.opportunity.id,
                owner_id: analysisData.opportunity.owner_id,
                budgetamount: analysisData.crm_diff.budget.proposed,
                estimatedclosedate: analysisData.crm_diff.estimated_close_date.proposed,
                decision_maker_name: analysisData.draft_email.decision_maker,
                draft_email_subject: analysisData.draft_email.subject,
                draft_email_body: analysisData.draft_email.body,
            };

            const res = await fetch("/api/commit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Commit failed");

            setStep("success");
        } catch (err: any) {
            setErrorMessage(err.message);
            setStep("error");
        }
    };

    const loadDummyTranscript = async () => {
        try {
            const res = await fetch("/dummy_transcript.txt");
            if (res.ok) {
                const text = await res.text();
                setTranscript(text);
            } else {
                setTranscript(`**Microsoft Teams Transcript: ABC Corp - Enterprise Licenses Sync**
        
Rep (Alex): Hey Sarah, thanks for jumping on. Did you get a chance to review the Enterprise Licenses proposal we sent over?

Client (Sarah): Yes, we had our internal review yesterday. The team is fully on board with the rollout. We've officially approved a budget of $1,950,000 for this first phase.

Rep (Alex): That's fantastic news! And regarding the timeline, are we still aiming to have this closed out by next week?

Client (Sarah): Precisely. Our hard deadline to get this signed and finalized is November 15th, 2024. 

Rep (Alex): Perfect, I'll update the timeline on our end. I'll send over the final contract immediately so we can wrap this up!`);
            }
        } catch {
            setTranscript("Error loading dummy transcript.");
        }
    };

    return {
        transcript,
        setTranscript,
        step,
        setStep,
        analysisData,
        errorMessage,
        handleAnalyze,
        handleCommit,
        loadDummyTranscript
    };
}
