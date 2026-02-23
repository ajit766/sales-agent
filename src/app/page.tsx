"use client";

import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";
import clsx from "clsx";

import { MeetingLoopTab } from "../components/MeetingLoopTab";
import { DailyBriefingTab } from "../components/DailyBriefingTab";
import { SilentRisksTab } from "../components/SilentRisksTab";

export default function SalesAgent() {
  const [activeTab, setActiveTab] = useState<"loop" | "briefing" | "risks">("loop");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 pb-20">
      <header className="border-b border-white/5 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between relative">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-500/10 p-2 rounded-lg border border-indigo-500/20">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            <h1 className="font-semibold text-lg tracking-tight">Sales Agent</h1>
          </div>

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
              <button
                onClick={() => setActiveTab("risks")}
                className={clsx(
                  "px-4 py-1.5 text-sm font-medium rounded-md transition",
                  activeTab === "risks" ? "bg-slate-800 text-rose-400 shadow-sm" : "text-slate-400 hover:text-rose-400/70"
                )}
              >
                Silent Risks
              </button>
            </div>
          </div>

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
          {activeTab === "loop" && <MeetingLoopTab />}
          {activeTab === "briefing" && <DailyBriefingTab />}
          {activeTab === "risks" && <SilentRisksTab />}
        </AnimatePresence>
      </main>
    </div>
  );
}
