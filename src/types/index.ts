export type CrmDiff = {
    budget: { existing: number | null; proposed: number | null };
    estimated_close_date: { existing: string | null; proposed: string | null };
};

export type AnalysisResponse = {
    success: boolean;
    opportunity: { id: string; name: string; owner_id: string };
    meeting_summary: string;
    draft_email: { subject: string; body: string; decision_maker: string };
    crm_diff: CrmDiff;
};
