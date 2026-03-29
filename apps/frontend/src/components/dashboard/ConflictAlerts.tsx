import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { GitCompare } from "lucide-react";
import { useAnalysis } from "@/hooks/useAnalysis";

export function ConflictAlerts() {
  const { analysis, isLoading } = useAnalysis();

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6 text-center py-12 text-muted-foreground">
          Loading conflicts...
        </CardContent>
      </Card>
    );
  }

  if (!analysis || analysis.conflicts.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6 text-center py-12">
          <GitCompare className="h-8 w-8 mx-auto text-green-500 mb-3" />
          <p className="font-semibold text-lg">No conflicts detected</p>
          <p className="text-muted-foreground text-sm mt-1">
            Your portfolio policies are well-coordinated with no conflicting terms.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {analysis.conflicts.map((conflict) => (
        <Card key={conflict.conflict_type}>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <GitCompare className="h-4 w-4 text-muted-foreground" />
                <span className="font-semibold">
                  {conflict.conflict_type.replace(/_/g, " ")}
                </span>
              </div>
              <Badge
                variant={
                  conflict.severity === "critical"
                    ? "destructive"
                    : conflict.severity === "moderate"
                    ? "warning"
                    : "secondary"
                }
              >
                {conflict.severity}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mb-3">{conflict.description}</p>

            {conflict.affected_policies.length > 0 && (
              <div className="mb-3">
                <p className="text-sm text-muted-foreground mb-1">Affected policies:</p>
                <ul className="text-sm space-y-1">
                  {conflict.affected_policies.map((p) => (
                    <li key={p.policy_id} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground inline-block" />
                      {p.product_name} ({p.insurer})
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm">
              <p className="text-green-900">
                <strong>Resolution:</strong> {conflict.resolution_hint}
              </p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
