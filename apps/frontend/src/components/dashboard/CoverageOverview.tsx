"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Shield } from "lucide-react";
import type { PolicySummary } from "@/lib/api";

const COVERAGE_TYPES = [
  { key: "DEATH", label: "Death / TPD", color: "bg-blue-500" },
  { key: "CI", label: "Critical Illness", color: "bg-red-500" },
  { key: "HOSPITALISATION", label: "Hospitalisation", color: "bg-green-500" },
  { key: "MEDISHIELD_LIFE", label: "MediShield Life", color: "bg-teal-500" },
  { key: "IP", label: "Integrated Shield Plan", color: "bg-emerald-500" },
  { key: "DISABILITY", label: "Disability Income", color: "bg-amber-500" },
  { key: "ACCIDENT", label: "Personal Accident", color: "bg-orange-500" },
  { key: "ENDOWMENT", label: "Endowment / Savings", color: "bg-slate-500" },
];

const PRODUCT_COVERAGE: Record<string, string[]> = {
  TERM_LIFE: ["DEATH"],
  WHOLE_LIFE: ["DEATH"],
  CRITICAL_ILLNESS: ["CI"],
  HOSPITALISATION: ["HOSPITALISATION"],
  MEDISHIELD_LIFE: ["MEDISHIELD_LIFE"],
  IP: ["IP"],
  DISABILITY: ["DISABILITY"],
  ACCIDENT: ["ACCIDENT"],
  ENDOWMENT: ["ENDOWMENT"],
};

export function CoverageOverview({ policies }: { policies: PolicySummary[] }) {
  const coveredTypes = new Set<string>();
  for (const policy of policies) {
    const types = PRODUCT_COVERAGE[policy.productType] ?? [];
    for (const t of types) coveredTypes.add(t);
  }

  const coveredCount = coveredTypes.size;
  const totalCount = COVERAGE_TYPES.length;
  const insurers = new Set(policies.map((p) => p.insurerCode)).size;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Coverage Types in Your Portfolio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {COVERAGE_TYPES.map((ct) => {
              const hasIt = coveredTypes.has(ct.key);
              return (
                <div key={ct.key} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`h-3 w-3 rounded-full ${hasIt ? ct.color : "bg-gray-200"}`} />
                    <span className="text-sm font-medium">{ct.label}</span>
                  </div>
                  {hasIt ? (
                    <Badge variant="success">Covered</Badge>
                  ) : (
                    <Badge variant="outline" className="text-muted-foreground">
                      Not Present
                    </Badge>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Portfolio Summary</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <p>
            Your portfolio covers{" "}
            <strong className="text-foreground">{coveredCount}</strong> of{" "}
            <strong className="text-foreground">{totalCount}</strong> tracked coverage
            types across{" "}
            <strong className="text-foreground">{policies.length}</strong> policy
            {policies.length !== 1 ? "ies" : ""} from{" "}
            <strong className="text-foreground">{insurers}</strong> insurer
            {insurers !== 1 ? "s" : ""}.
          </p>
          {coveredTypes.has("HOSPITALISATION") && !coveredTypes.has("MEDISHIELD_LIFE") && (
            <p className="mt-2 text-amber-700 bg-amber-50 p-3 rounded-md text-xs">
              <strong>Note:</strong> You have hospitalisation coverage but no MediShield Life
              record. Singapore Citizens and PRs are automatically covered under MediShield
              Life via CPF — this may just not have been parsed from your documents.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
