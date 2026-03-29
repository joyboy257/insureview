"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { TrendingUp, AlertCircle } from "lucide-react";
import { usePortfolio } from "@/hooks/usePortfolio";

interface Scenario {
  id: string;
  label: string;
  description: string;
  coverageTypes: string[];
}

const SCENARIOS: Scenario[] = [
  {
    id: "death_primary_earner",
    label: "Death of primary earner",
    description: "What your family receives if the primary earner passes away.",
    coverageTypes: ["DEATH", "TERM_LIFE", "WHOLE_LIFE"],
  },
  {
    id: "ci_diagnosis_core",
    label: "Critical Illness (heart attack, cancer, stroke)",
    description: "What you receive on diagnosis of a major CI condition.",
    coverageTypes: ["CRITICAL_ILLNESS", "CI"],
  },
  {
    id: "hospitalisation_30_days",
    label: "Hospitalisation: 30 days in hospital",
    description: "Estimated hospital bill coverage for a 30-day stay (A ward).",
    coverageTypes: ["HOSPITALISATION", "MEDISHIELD_LIFE", "IP"],
  },
  {
    id: "tpd_total_permanent_disability",
    label: "Total Permanent Disability (TPD)",
    description: "What you receive if unable to work due to TPD.",
    coverageTypes: ["TPD", "DISABILITY"],
  },
];

function formatCents(cents: number | null): string {
  if (cents === null || cents === undefined) return "—";
  const dollars = cents / 100;
  if (dollars >= 1_000_000) return `S$${(dollars / 1_000_000).toFixed(1)}M`;
  if (dollars >= 1_000) return `S$${(dollars / 1_000).toFixed(0)}K`;
  return `S$${dollars.toFixed(0)}`;
}

export function ScenarioBuilder() {
  const { data: policies, isLoading } = usePortfolio();
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);

  const active = SCENARIOS.find((s) => s.id === selectedScenario);

  const scenarioData = useMemo(() => {
    if (!active || !policies) return null;

    const relevantPolicies = policies.filter((p) => {
      if (!active.coverageTypes.includes(p.productType)) return false;
      return p.policyStatus === "active" || p.policyStatus === "reduced";
    });

    const totalPayout = relevantPolicies.reduce(
      (sum, p) => sum + (p.sumAssuredCents ?? 0),
      0
    );

    return {
      policies: relevantPolicies,
      totalPayout,
    };
  }, [active, policies]);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6 text-center py-12 text-muted-foreground">
          Loading scenarios...
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid sm:grid-cols-2 gap-4">
        {SCENARIOS.map((scenario) => (
          <Card
            key={scenario.id}
            className={`cursor-pointer transition-colors ${
              selectedScenario === scenario.id ? "border-primary" : "hover:border-primary/50"
            }`}
            onClick={() => setSelectedScenario(scenario.id)}
          >
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium text-sm">{scenario.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{scenario.description}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {active && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle>{active.label}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">{active.description}</p>

            {policies && policies.length === 0 ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <AlertCircle className="h-4 w-4" />
                Upload policies to see personalised scenario analysis.
              </div>
            ) : scenarioData && scenarioData.policies.length > 0 ? (
              <>
                <div className="p-4 bg-primary/5 rounded-lg">
                  <p className="text-sm text-muted-foreground">Estimated payout</p>
                  <p className="text-3xl font-bold text-primary">
                    {formatCents(scenarioData.totalPayout)}
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Policies that apply:</p>
                  {scenarioData.policies.map((p) => (
                    <div
                      key={p.id}
                      className="flex items-center justify-between text-sm border-b pb-2 last:border-0"
                    >
                      <div>
                        <span className="font-medium">{p.productName}</span>
                        <span className="text-muted-foreground"> · {p.insurerName}</span>
                      </div>
                      <span className="font-medium">{formatCents(p.sumAssuredCents)}</span>
                    </div>
                  ))}
                </div>

                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-900">
                  This is a hypothetical illustration based on the information in your uploaded
                  policies. Actual payouts depend on the specific circumstances of a claim and
                  are subject to the full terms and conditions of each policy.
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <AlertCircle className="h-4 w-4" />
                No active policies match this scenario in your portfolio.
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
