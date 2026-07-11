import { useState } from 'react';
import { ArrowRight, Github, Loader2 } from 'lucide-react';

interface PRInputProps {
  onReview: (url: string) => void;
  isLoading: boolean;
}

export function PRInput({ onReview, isLoading }: PRInputProps) {
  const [url, setUrl] = useState('');
  const maxLength = 500;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onReview(url.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative flex items-center w-full group">
        <div className="absolute left-4 text-gray-400 group-focus-within:text-blue-500 transition-colors">
          <Github className="w-5 h-5" />
        </div>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo/pull/123"
          maxLength={maxLength}
          className="w-full pl-12 pr-16 py-4 bg-white border border-gray-200 rounded-2xl shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          required
        />
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="absolute right-2 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors flex items-center justify-center"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <ArrowRight className="w-5 h-5" />
          )}
        </button>
      </div>
      <p className="mt-3 text-sm text-gray-500 text-center">
        Paste a GitHub Pull Request URL to get an AI-powered code review.
      </p>
    </form>
  );
}
