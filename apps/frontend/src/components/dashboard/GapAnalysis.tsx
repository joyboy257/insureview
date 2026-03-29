"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useAnalysis } from "@/hooks/useAnalysis";
import { usePortfolio } from "@/hooks/usePortfolio";

function formatCents(cents: number | null): string {
  if (cents === null || cents === undefined) return "—";
  const dollars = cents / 100;
  if (dollars >= 1_000_000) return `S$${(dollars / 1_000_000).toFixed(1)}M`;
  if (dollars >= 1_000) return `S$${(dollars / 1_000).toFixed(0)}K`;
  return `S$${dollars.toFixed(0)}`;
}

export function GapAnalysis() {
  const { analysis, isLoading, isRunning, runAnalysis } = useAnalysis();
  const { data: policies } = usePortfolio();

  if (isLoading) {
    return (
      <Card className="py-12 text-center">
        <CardContent className="text-muted-foreground">
          Loading analysis...
        </CardContent>
      </Card>
    );
  }

  if (!analysis || analysis.gaps.length === 0) {
    return (
      <div className="space-y-4">
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <AlertTriangle className="h-8 w-8 mx-auto text-green-500 mb-3" />
            <p className="font-semibold text-lg">No coverage gaps detected</p>
            <p className="text-muted-foreground text-sm mt-1">
              Your portfolio appears well-covered across the major risk categories.
            </p>
          </CardContent>
        </Card>
        {policies && policies.length > 0 && (
          <div className="flex justify-center">
            <Button
              variant="outline"
              size="sm"
              onClick={() => runAnalysis(policies!.map((p) => p.id))}
              disabled={isRunning}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRunning ? "animate-spin" : ""}`} />
              {isRunning ? "Re-analysing..." : "Re-run Analysis"}
            </Button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {analysis.gaps.map((gap) => (
        <Card key={gap.coverage_type}>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <AlertTriangle
                  className={`h-4 w-4 ${
                    gap.severity === "critical"
                      ? "text-red-500"
                      : gap.severity === "warning"
                      ? "text-amber-500"
                      : "text-blue-500"
                  }`}
                />
                <span className="font-semibold">
                  {gap.coverage_type.replace("_", " ")}
                </span>
              </div>
              <Badge
                variant={
                  gap.severity === "critical"
                    ? "destructive"
                    : gap.severity === "warning"
                    ? "warning"
                    : "secondary"
                }
              >
                {gap.severity}
              </Badge>
            </div>

            <p className="text-sm text-muted-foreground mb-3">
              {gap.description || gap.recommendation}
            </p>

            {gap.gap_amount_cents !== null && (
              <div className="text-sm">
                <span className="text-muted-foreground">Coverage gap: </span>
                <span className="font-medium text-destructive">
                  {formatCents(gap.gap_amount_cents)}
                </span>
              </div>
            )}

            {gap.recommendation && gap.severity !== "info" && (
              <div className="mt-3 bg-slate-50 border rounded-lg p-3 text-sm">
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Recommendation:</strong>{" "}
                  {gap.recommendation}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      ))}

      <div className="flex justify-center">
        <Button
          variant="outline"
          size="sm"
          onClick={() => policies && runAnalysis(policies.map((p) => p.id))}
          disabled={isRunning}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isRunning ? "animate-spin" : ""}`} />
          {isRunning ? "Analysing..." : "Re-run Analysis"}
        </Button>
      </div>
    </div>
  );
}
