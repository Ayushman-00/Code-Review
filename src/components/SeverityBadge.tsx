interface SeverityBadgeProps {
  severity: "critical" | "warning" | "suggestion";
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const styles = {
    critical: "bg-red-100 text-red-800 border-red-200",
    warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
    suggestion: "bg-blue-100 text-blue-800 border-blue-200"
  };

  const labels = {
    critical: "Critical",
    warning: "Warning",
    suggestion: "Suggestion"
  };

  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${styles[severity]}`}>
      {labels[severity]}
    </span>
  );
}
