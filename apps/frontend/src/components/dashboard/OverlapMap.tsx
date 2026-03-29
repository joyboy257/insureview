import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Layers } from "lucide-react";
import { useAnalysis } from "@/hooks/useAnalysis";

function formatCents(cents: number | null): string {
  if (cents === null || cents === undefined) return "—";
  const dollars = cents / 100;
  if (dollars >= 1_000_000) return `S$${(dollars / 1_000_000).toFixed(1)}M`;
  if (dollars >= 1_000) return `S$${(dollars / 1_000).toFixed(0)}K`;
  return `S$${dollars.toFixed(0)}`;
}

export function OverlapMap() {
  const { analysis, isLoading } = useAnalysis();

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6 text-center py-12 text-muted-foreground">
          Loading overlaps...
        </CardContent>
      </Card>
    );
  }

  if (!analysis || analysis.overlaps.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6 text-center py-12">
          <Layers className="h-8 w-8 mx-auto text-blue-500 mb-3" />
          <p className="font-semibold text-lg">No overlapping coverage detected</p>
          <p className="text-muted-foreground text-sm mt-1">
            Your portfolio has no policies with overlapping coverage types.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-900">
        <strong>How overlapping coverage works in Singapore:</strong> Life and CI policies
        typically stack independently — a CI diagnosis pays the CI benefit in addition
        to any death benefit. Hospitalisation plans are the exception: combined payouts cannot
        exceed 100% of actual hospital costs.
      </div>
      {analysis.overlaps.map((overlap, i) => (
        <Card key={i}>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-muted-foreground" />
                <span className="font-semibold">
                  {overlap.coverage_type.replace(/_/g, " ")}
                </span>
              </div>
              <Badge
                variant={overlap.severity === "warning" ? "warning" : "secondary"}
              >
                {overlap.severity}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mb-3">{overlap.note}</p>

            <div className="space-y-2 mb-3">
              {overlap.overlapping_policies.map((policy) => (
                <div
                  key={policy.policy_id}
                  className="flex items-center justify-between text-sm border-b pb-2 last:border-0"
                >
                  <div>
                    <span className="font-medium">{policy.product_name}</span>
                    <span className="text-muted-foreground"> · {policy.insurer}</span>
                  </div>
                  <span className="font-medium">{formatCents(policy.sum_assured_cents)}</span>
                </div>
              ))}
            </div>

            <div className="text-sm">
              <span className="text-muted-foreground">Combined amount: </span>
              <span className="font-medium">{formatCents(overlap.total_sum_assured_cents)}</span>
              <span className="text-muted-foreground"> across {overlap.policy_count} policies</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
