import { useState } from "react";

export function useSilentRisks() {
    const [risksStep, setRisksStep] = useState<"idle" | "generating" | "complete" | "error">("idle");
    const [risksMarkdown, setRisksMarkdown] = useState<string>("");
    const [errorMessage, setErrorMessage] = useState("");

    const handleGenerateRisks = async () => {
        setRisksStep("generating");
        try {
            const res = await fetch("/api/silent-risks", { method: "GET" });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Silent Risks generation failed");

            setRisksMarkdown(data.markdown);
            setRisksStep("complete");
        } catch (err: any) {
            setErrorMessage(err.message);
            setRisksStep("error");
        }
    };

    return {
        risksStep,
        setRisksStep,
        risksMarkdown,
        errorMessage,
        handleGenerateRisks
    };
}
