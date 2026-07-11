export interface ReviewIssue {
  severity: "critical" | "warning" | "suggestion";
  file: string;
  line?: number;
  message: string;
  fix?: string;
}

export interface ReviewResponse {
  issues: ReviewIssue[];
  summary: string;
  total_issues: number;
  pr_info: {
    title: string;
    author: string;
    files_changed: number;
    additions: number;
    deletions: number;
    pr_url: string;
  };
}
