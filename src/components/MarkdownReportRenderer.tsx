import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownReportRendererProps {
    content: string;
}

export function MarkdownReportRenderer({ content }: MarkdownReportRendererProps) {
    return (
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
                {content}
            </ReactMarkdown>
        </div>
    );
}
