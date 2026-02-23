import { useState } from "react";

export function useDailyBriefing() {
    const [briefingStep, setBriefingStep] = useState<"idle" | "generating" | "complete" | "error">("idle");
    const [briefingMarkdown, setBriefingMarkdown] = useState<string>("");
    const [errorMessage, setErrorMessage] = useState("");

    const handleGenerateBriefing = async () => {
        setBriefingStep("generating");
        try {
            const res = await fetch("/api/briefing", { method: "GET" });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Briefing generation failed");

            setBriefingMarkdown(data.markdown);
            setBriefingStep("complete");
        } catch (err: any) {
            setErrorMessage(err.message);
            setBriefingStep("error");
        }
    };

    return {
        briefingStep,
        setBriefingStep,
        briefingMarkdown,
        errorMessage,
        handleGenerateBriefing
    };
}
