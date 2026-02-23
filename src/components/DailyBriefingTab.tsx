import { motion } from "framer-motion";
import { Coffee, Target, Sparkles, AlertTriangle } from "lucide-react";
import { useDailyBriefing } from "../hooks/useDailyBriefing";
import { MarkdownReportRenderer } from "./MarkdownReportRenderer";

export function DailyBriefingTab() {
    const {
        briefingStep,
        setBriefingStep,
        briefingMarkdown,
        errorMessage,
        handleGenerateBriefing
    } = useDailyBriefing();

    return (
        <motion.div
            key="briefing-view"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-8"
        >
            {briefingStep === "idle" && (
                <div className="flex flex-col items-center justify-center py-20 text-center space-y-8">
                    <div className="w-24 h-24 bg-indigo-500/10 rounded-full flex items-center justify-center border border-indigo-500/20">
                        <Coffee className="w-10 h-10 text-indigo-400" />
                    </div>
                    <div className="space-y-4 max-w-lg">
                        <h2 className="text-4xl font-light tracking-tight text-white">Your Morning <span className="font-medium text-indigo-400">Action Plan</span></h2>
                        <p className="text-slate-400 text-lg">Stop digging through CRM tasks. We analyze your live dynamics 365 pipeline and structure your entire day using the Eisenhower Matrix.</p>
                    </div>
                    <button
                        onClick={handleGenerateBriefing}
                        className="px-8 py-4 bg-indigo-500 hover:bg-indigo-400 text-white rounded-xl font-medium tracking-wide flex items-center gap-3 transition-all shadow-lg shadow-indigo-500/20 text-lg group"
                    >
                        <Target className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        Generate Daily Briefing
                    </button>
                </div>
            )}

            {briefingStep === "generating" && (
                <div className="flex flex-col items-center justify-center py-32 space-y-8">
                    <div className="relative">
                        <div className="absolute inset-0 bg-indigo-500 blur-2xl opacity-20 animate-pulse rounded-full" />
                        <div className="w-20 h-20 bg-slate-900 border border-indigo-500/30 rounded-2xl flex items-center justify-center shadow-xl">
                            <Sparkles className="w-10 h-10 text-indigo-400 animate-pulse" />
                        </div>
                    </div>
                    <div className="text-center space-y-2">
                        <h3 className="text-2xl font-medium text-white">Synthesizing Pipeline Intelligence...</h3>
                        <p className="text-slate-400 max-w-sm mx-auto">
                            Querying Dynamics 365 opportunities and scoring velocity using Azure AI Foundry...
                        </p>
                    </div>
                </div>
            )}

            {briefingStep === "complete" && (
                <div className="space-y-6">
                    <div className="flex justify-end">
                        <button
                            onClick={handleGenerateBriefing}
                            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-medium transition flex items-center gap-2"
                        >
                            <Sparkles className="w-4 h-4" />
                            Regenerate Briefing
                        </button>
                    </div>
                    <MarkdownReportRenderer content={briefingMarkdown} />
                </div>
            )}

            {briefingStep === "error" && (
                <div className="bg-red-950/20 border border-red-500/20 rounded-2xl p-12 text-center">
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <AlertTriangle className="w-8 h-8 text-red-400" />
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-2">Briefing Generation Failed</h2>
                    <p className="text-red-200/60 mb-8 max-w-lg mx-auto">{errorMessage}</p>
                    <button
                        onClick={() => setBriefingStep("idle")}
                        className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition"
                    >
                        Go Back
                    </button>
                </div>
            )}
        </motion.div>
    );
}
