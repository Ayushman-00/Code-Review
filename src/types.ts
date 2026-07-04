export interface ReviewIssue {
  severity: "critical" | "warning" | "suggestion";
  line: number;
  message: string;
  fix: string;
}

export interface ReviewResponse {
  issues: ReviewIssue[];
}
