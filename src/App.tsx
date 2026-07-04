/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { PRInput } from './components/PRInput';
import { ReviewCard } from './components/ReviewCard';
import { ReviewIssue } from './types';
import { Bot, GitPullRequest, AlertTriangle } from 'lucide-react';
import { motion } from 'motion/react';

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [issues, setIssues] = useState<ReviewIssue[] | null>(null);
  const [repoInfo, setRepoInfo] = useState<{ owner: string; repo: string; prNumber: number } | null>(null);

const handleReview = async (url: string) => {
  setIsLoading(true);
  setError(null);
  setIssues(null);
  setRepoInfo(null);

  try {
  const baseUrl = 'https://laughing-winner-5g6qp9rp9vw4hv9-8000.app.github.dev';
    const response = await fetch(`${baseUrl}/api/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pr_url: url }),  // ← fixed: pr_url not prUrl
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to analyze PR');
    }

    // Parse owner/repo/prNumber from the PR URL the backend echoes back
    const match = data.pr_info.pr_url.match(
      /github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)/
    );

    setIssues(data.issues);
    setRepoInfo({
      owner: match ? match[1] : data.pr_info.author,
      repo: match ? match[2] : 'unknown',
      prNumber: match ? parseInt(match[3]) : 0,
    });

  } catch (err: any) {
    setError(err.message || 'An unexpected error occurred');
  } finally {
    setIsLoading(false);
  }
};
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-gray-900 font-sans selection:bg-blue-100 selection:text-blue-900">
      <div className="max-w-5xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        
        {/* Header Section */}
        <div className="text-center mb-12 space-y-4">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 rounded-2xl blur opacity-20"></div>
              <div className="relative bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-center">
                <Bot className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            AI Code Reviewer
          </h1>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            Get instant, intelligent feedback on your GitHub pull requests. Detect bugs, improve performance, and enforce best practices automatically.
          </p>
        </div>

        {/* Input Section */}
        <div className="mb-12">
          <PRInput onReview={handleReview} isLoading={isLoading} />
          
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3"
            >
              <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </motion.div>
          )}
        </div>

        {/* Results Section */}
        {issues && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
              <div className="p-2 bg-gray-100 rounded-lg">
                <GitPullRequest className="w-5 h-5 text-gray-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Review Results for #{repoInfo?.prNumber}
                </h2>
                <p className="text-sm text-gray-500">
                  {repoInfo?.owner}/{repoInfo?.repo}
                </p>
              </div>
            </div>

            {issues.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-2xl border border-gray-200 shadow-sm">
                <p className="text-gray-500">No issues found. LGTM! 🎉</p>
              </div>
            ) : (
              <div className="grid gap-6">
                {issues.map((issue, index) => (
                  <ReviewCard key={index} issue={issue} />
                ))}
              </div>
            )}
          </motion.div>
        )}

      </div>
    </div>
  );
}
