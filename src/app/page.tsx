"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText, Sparkles, ArrowRight, CheckCircle2, AlertTriangle, UserCheck,
  CalendarDays, DollarSign, Send, MapPin, Target, Coffee
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import clsx from "clsx";

// --- Types ---
type CrmDiff = {
  budget: { existing: number | null; proposed: number | null };
  estimated_close_date: { existing: string | null; proposed: string | null };
};

type AnalysisResponse = {
  success: boolean;
  opportunity: { id: string; name: string; owner_id: string };
  meeting_summary: string;
  draft_email: { subject: string; body: string; decision_maker: string };
  crm_diff: CrmDiff;
};

// --- Components ---
export default function SalesAgent() {
  const [activeTab, setActiveTab] = useState<"loop" | "briefing">("loop");

  // Workstream 1 State
  const [transcript, setTranscript] = useState("");
  const [step, setStep] = useState<"input" | "analyzing" | "review" | "committing" | "success" | "error">("input");
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  // Workstream 2 State
  const [briefingStep, setBriefingStep] = useState<"idle" | "generating" | "complete" | "error">("idle");
  const [briefingMarkdown, setBriefingMarkdown] = useState<string>("");

  // Step 1: Analyze Transcript
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

  // Step 2: Commit to CRM
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
        setTranscript("**Meeting Transcript: Q3 Expansion Planning**\\nRep: What did finance approve?\\nMark: $50,000 budget by March 15th.");
      }
    } catch {
      setTranscript("Error loading dummy transcript.");
    }
  };

  // Workstream 2 Generation
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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 pb-20">

      {/* Premium Header */}
      <header className="border-b border-white/5 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between relative">

          {/* Left: Branding */}
          <div className="flex items-center gap-2">
            <div className="bg-indigo-500/10 p-2 rounded-lg border border-indigo-500/20">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            <h1 className="font-semibold text-lg tracking-tight">Sales Agent</h1>
          </div>

          {/* Center: Tabs */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="flex bg-slate-900 rounded-lg p-1 border border-white/5 shadow-inner">
              <button
                onClick={() => setActiveTab("loop")}
                className={clsx(
                  "px-4 py-1.5 text-sm font-medium rounded-md transition",
                  activeTab === "loop" ? "bg-slate-800 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
                )}
              >
                Meeting to CRM
              </button>
              <button
                onClick={() => setActiveTab("briefing")}
                className={clsx(
                  "px-4 py-1.5 text-sm font-medium rounded-md transition",
                  activeTab === "briefing" ? "bg-slate-800 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
                )}
              >
                Daily Briefing
              </button>
            </div>
          </div>

          {/* Right: Status */}
          <div className="flex items-center gap-4">
            <div className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-medium rounded-full border border-emerald-500/20 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
              Dynamics 365
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">

          {/* WORKSTREAM 2: DAILY BRIEFING VIEW */}
          {activeTab === "briefing" && (
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
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl prose prose-invert prose-indigo max-w-none
                        prose-h1:text-3xl prose-h1:font-light prose-h1:tracking-tight prose-h1:mb-8 prose-h1:pb-4 prose-h1:border-b prose-h1:border-white/10
                        prose-h2:text-xl prose-h2:font-medium prose-h2:text-indigo-300 prose-h2:mt-10
                        prose-table:overflow-hidden prose-table:rounded-lg prose-table:border prose-table:border-white/10
                        prose-th:bg-slate-950 prose-th:px-4 prose-th:py-3 prose-th:text-xs prose-th:uppercase prose-th:tracking-wider prose-th:text-slate-400 text-left
                        prose-td:px-4 prose-td:py-3 prose-td:border-t prose-td:border-white/5
                        prose-li:text-slate-300 text-slate-300"
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h2: ({ node, ...props }) => <h2 className="text-xl font-medium text-indigo-300 mt-16 pt-8 border-t border-white/10" {...props} />,
                        em: ({ node, ...props }) => <em className="text-slate-500 italic text-sm block mt-4 mb-4" {...props} />,
                        br: ({ node, ...props }) => <br className="block content-[''] h-8 mt-4 mb-8 border-b border-white/5" {...props} />,
                      }}
                    >
                      {briefingMarkdown}
                    </ReactMarkdown>
                  </div>
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
          )}

          {/* WORKSTREAM 1: MEETING TO CRM LOOP VIEW */}
          {activeTab === "loop" && step === "input" && (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <h2 className="text-3xl font-light tracking-tight text-white">Meeting to <span className="text-indigo-400 font-medium">CRM Loop</span></h2>
                <p className="text-slate-400 text-lg">Paste your raw meeting transcript to automatically update CRM and draft follow-ups.</p>
              </div>

              <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
                <div className="relative bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
                    <div className="flex gap-2">
                      <div className="w-3 h-3 rounded-full bg-slate-700" />
                      <div className="w-3 h-3 rounded-full bg-slate-700" />
                      <div className="w-3 h-3 rounded-full bg-slate-700" />
                    </div>
                    <button
                      onClick={loadDummyTranscript}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition"
                    >
                      Load Dummy Target
                    </button>
                  </div>
                  <textarea
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Paste your Microsoft Teams or Zoom transcript here..."
                    className="w-full h-80 bg-transparent p-6 text-slate-300 placeholder-slate-600 focus:outline-none resize-none font-mono text-sm leading-relaxed"
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleAnalyze}
                  disabled={!transcript.trim()}
                  className="px-6 py-3 bg-indigo-500 hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium tracking-wide flex items-center gap-2 transition-all shadow-lg shadow-indigo-500/20"
                >
                  <Sparkles className="w-4 h-4" />
                  Analyze Pipeline Data
                </button>
              </div>
            </motion.div>
          )}

          {/* STATE: ANALYZING / COMMITTING */}
          {activeTab === "loop" && (step === "analyzing" || step === "committing") && (
            <motion.div
              key="loading"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center py-32 space-y-8"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-indigo-500 blur-2xl opacity-20 animate-pulse rounded-full" />
                <div className="w-20 h-20 bg-slate-900 border border-indigo-500/30 rounded-2xl flex items-center justify-center shadow-xl">
                  {step === "analyzing" ? (
                    <Sparkles className="w-10 h-10 text-indigo-400 animate-pulse" />
                  ) : (
                    <ArrowRight className="w-10 h-10 text-indigo-400 animate-bounce" />
                  )}
                </div>
              </div>
              <div className="text-center space-y-2">
                <h3 className="text-2xl font-medium text-white">
                  {step === "analyzing" ? "Analyzing Context & Hydrating Pipeline..." : "Pushing to Dynamics 365..."}
                </h3>
                <p className="text-slate-400 max-w-sm mx-auto">
                  {step === "analyzing"
                    ? "GPT-4o is extracting the target opportunity and comparing state against live Dataverse values."
                    : "Executing PATCH requests to the Dataverse REST API..."}
                </p>
              </div>
            </motion.div>
          )}

          {/* STATE: REVIEW UI */}
          {activeTab === "loop" && step === "review" && analysisData && (
            <motion.div
              key="review"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              <div className="flex items-center justify-between border-b border-white/10 pb-6">
                <div>
                  <h2 className="text-3xl font-semibold text-white">Review & Commit</h2>
                  <p className="text-slate-400 mt-1">Verify the AI extractions before patching CRM.</p>
                </div>
                <div className="px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-indigo-400" />
                  <div>
                    <p className="text-xs text-slate-400 font-medium">Target Opportunity</p>
                    <p className="text-sm text-indigo-300 font-semibold">{analysisData.opportunity.name}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left Column: Summary & Fields */}
                <div className="space-y-6">
                  {/* Meeting Summary */}
                  <div className="bg-slate-900 border border-white/5 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <FileText className="w-5 h-5 text-emerald-400" />
                      <h3 className="text-lg font-medium text-white">Meeting Summary</h3>
                    </div>
                    <p className="text-slate-300 leading-relaxed text-sm">
                      {analysisData.meeting_summary}
                    </p>
                  </div>

                  {/* CRM Before/After Diff */}
                  <div className="bg-slate-900 border border-white/5 rounded-xl p-6">
                    <h3 className="text-lg font-medium text-white mb-6">CRM Field Updates</h3>

                    <div className="space-y-6">
                      {/* Budget Diff */}
                      <div>
                        <div className="flex items-center gap-2 mb-2 text-sm font-medium text-slate-400">
                          <DollarSign className="w-4 h-4" /> Est. Revenue / Budget
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex-1 bg-slate-950 border border-red-500/20 p-3 rounded-lg line-through text-slate-500 font-mono text-sm">
                            ${analysisData.crm_diff.budget.existing || "0"}
                          </div>
                          <ArrowRight className="w-5 h-5 text-slate-600" />
                          <div className="flex-1 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg text-emerald-400 font-mono text-sm font-bold">
                            ${analysisData.crm_diff.budget.proposed}
                          </div>
                        </div>
                      </div>

                      {/* Date Diff */}
                      <div>
                        <div className="flex items-center gap-2 mb-2 text-sm font-medium text-slate-400">
                          <CalendarDays className="w-4 h-4" /> Estimated Close Date
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex-1 bg-slate-950 border border-red-500/20 p-3 rounded-lg line-through text-slate-500 font-mono text-sm">
                            {analysisData.crm_diff.estimated_close_date.existing?.split('T')[0] || "None"}
                          </div>
                          <ArrowRight className="w-5 h-5 text-slate-600" />
                          <div className="flex-1 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg text-emerald-400 font-mono text-sm font-bold">
                            {analysisData.crm_diff.estimated_close_date.proposed}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Column: Email Draft */}
                <div className="bg-slate-900 border border-white/5 rounded-xl flex flex-col overflow-hidden">
                  <div className="p-4 border-b border-white/5 bg-slate-800/50 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Send className="w-4 h-4 text-blue-400" />
                      <span className="text-sm font-medium text-slate-300">Activity Task: Email Draft</span>
                    </div>
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <UserCheck className="w-3 h-3" /> Will assign to your "My Work"
                    </span>
                  </div>
                  <div className="p-5 flex-1 space-y-4">
                    <div>
                      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">To:</span>
                      <div className="text-sm text-white font-medium">{analysisData.draft_email.decision_maker}</div>
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">Subject:</span>
                      <div className="text-sm text-white font-medium bg-slate-950 p-2 rounded border border-white/5">
                        {analysisData.draft_email.subject}
                      </div>
                    </div>
                    <div className="pt-2">
                      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Body:</span>
                      <div className="text-sm text-slate-300 bg-slate-950 p-4 rounded border border-white/5 whitespace-pre-wrap leading-relaxed h-56 overflow-y-auto">
                        {analysisData.draft_email.body}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-6 border-t border-white/10">
                <button
                  onClick={() => setStep("input")}
                  className="px-6 py-2.5 text-slate-400 hover:text-white transition font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCommit}
                  className="px-8 py-3 bg-indigo-500 hover:bg-indigo-400 text-white rounded-lg font-medium tracking-wide flex items-center gap-2 transition-all shadow-lg shadow-indigo-500/20"
                >
                  <CheckCircle2 className="w-5 h-5" />
                  Approve & Push to D365
                </button>
              </div>
            </motion.div>
          )}

          {/* STATE: SUCCESS */}
          {activeTab === "loop" && step === "success" && (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-emerald-950/20 border border-emerald-500/20 rounded-2xl p-12 text-center space-y-6"
            >
              <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="w-10 h-10 text-emerald-400" />
              </div>
              <h2 className="text-3xl font-semibold text-white">Sync Complete</h2>
              <p className="text-emerald-200/60 max-w-md mx-auto text-lg leading-relaxed">
                The {analysisData?.opportunity.name} Opportunity has been successfully updated in Dynamics 365, and the drafted email is waiting in your My Work dashboard.
              </p>
              <div className="pt-8">
                <button
                  onClick={() => {
                    setTranscript("");
                    setStep("input");
                    setAnalysisData(null);
                  }}
                  className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition"
                >
                  Process Another Transcript
                </button>
              </div>
            </motion.div>
          )}

          {/* STATE: ERROR */}
          {activeTab === "loop" && step === "error" && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-950/20 border border-red-500/20 rounded-2xl p-12 text-center"
            >
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">Analysis Failed</h2>
              <p className="text-red-200/60 mb-8 max-w-lg mx-auto">
                {errorMessage}
              </p>
              <div className="flex justify-center gap-4">
                <button
                  onClick={() => setStep("input")}
                  className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition"
                >
                  Go Back
                </button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </main>
    </div>
  );
}
