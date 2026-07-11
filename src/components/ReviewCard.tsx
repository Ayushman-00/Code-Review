import { ReviewIssue } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { AlertCircle, CheckCircle2, FileCode } from 'lucide-react';

interface ReviewCardProps {
  issue: ReviewIssue;
}

export function ReviewCard({ issue }: ReviewCardProps) {
  const lineLabel = issue.line ?? 'N/A';

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden transition-all hover:shadow-md">
      <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-white border border-gray-200 shadow-sm">
            <FileCode className="w-4 h-4 text-gray-500" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Line {lineLabel}</h3>
          </div>
        </div>
        <SeverityBadge severity={issue.severity} />
      </div>
      
      <div className="p-5 space-y-4">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-gray-400 shrink-0 mt-0.5" />
          <p className="text-gray-700 text-sm leading-relaxed">{issue.message}</p>
        </div>
        
        {issue.fix && (
          <div className="mt-4 bg-gray-900 rounded-xl overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 border-b border-gray-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-medium text-gray-300">Suggested Fix</span>
            </div>
            <div className="p-4 overflow-x-auto">
              <pre className="text-sm font-mono text-gray-300">
                <code>{issue.fix}</code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
