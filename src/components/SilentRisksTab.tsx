import { motion } from "framer-motion";
import { Target, AlertTriangle, Sparkles } from "lucide-react";
import { useSilentRisks } from "../hooks/useSilentRisks";
import { MarkdownReportRenderer } from "./MarkdownReportRenderer";

export function SilentRisksTab() {
    const {
        risksStep,
        setRisksStep,
        risksMarkdown,
        errorMessage,
        handleGenerateRisks
    } = useSilentRisks();

    return (
        <motion.div
            key="risks"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
        >
            <div className="space-y-2">
                <h2 className="text-3xl font-light tracking-tight text-white">Silent <span className="text-rose-400 font-medium">Risks</span></h2>
                <p className="text-slate-400 text-lg">Proactively identify stalled and blocked deals requiring immediate corrective action.</p>
            </div>

            {risksStep === "idle" && (
                <div className="flex justify-center py-20">
                    <button
                        onClick={handleGenerateRisks}
                        className="px-8 py-4 bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 text-rose-300 rounded-xl font-medium tracking-wide flex items-center gap-3 transition-all shadow-lg shadow-rose-500/10 text-lg group"
                    >
                        <Target className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        Scan Pipeline for Silent Risks
                    </button>
                </div>
            )}

            {risksStep === "generating" && (
                <div className="flex flex-col items-center justify-center py-32 space-y-8">
                    <div className="relative">
                        <div className="absolute inset-0 bg-rose-500 blur-2xl opacity-20 animate-pulse rounded-full" />
                        <div className="w-20 h-20 bg-slate-900 border border-rose-500/30 rounded-2xl flex items-center justify-center shadow-xl">
                            <AlertTriangle className="w-10 h-10 text-rose-400 animate-pulse" />
                        </div>
                    </div>
                    <div className="text-center space-y-2">
                        <h3 className="text-2xl font-medium text-white">Analyzing Data Hygiene...</h3>
                        <p className="text-slate-400 max-w-sm mx-auto">
                            Scanning Dataverse for stalled deals and extracting corrective action plans using Azure AI Foundry...
                        </p>
                    </div>
                </div>
            )}

            {risksStep === "complete" && (
                <div className="space-y-6">
                    <div className="flex justify-end">
                        <button
                            onClick={handleGenerateRisks}
                            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-medium transition flex items-center gap-2"
                        >
                            <Sparkles className="w-4 h-4" />
                            Rescan Pipeline
                        </button>
                    </div>
                    <MarkdownReportRenderer content={risksMarkdown} />
                </div>
            )}

            {risksStep === "error" && (
                <div className="bg-red-950/20 border border-red-500/20 rounded-2xl p-12 text-center">
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <AlertTriangle className="w-8 h-8 text-red-400" />
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-2">Risk Scan Failed</h2>
                    <p className="text-red-200/60 mb-8 max-w-lg mx-auto">{errorMessage}</p>
                    <button
                        onClick={() => setRisksStep("idle")}
                        className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition"
                    >
                        Go Back
                    </button>
                </div>
            )}
        </motion.div>
    );
}
