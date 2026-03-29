"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Layers,
  GitCompare,
  FileText,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { CoverageOverview } from "@/components/dashboard/CoverageOverview";
import { GapAnalysis } from "@/components/dashboard/GapAnalysis";
import { OverlapMap } from "@/components/dashboard/OverlapMap";
import { ConflictAlerts } from "@/components/dashboard/ConflictAlerts";
import { ScenarioBuilder } from "@/components/dashboard/ScenarioBuilder";
import { MASDisclaimer } from "@/components/dashboard/MASDisclaimer";
import { DisclaimerBanner } from "@/components/ui/DisclaimerBanner";
import { GettingStartedGuide } from "@/components/dashboard/GettingStartedGuide";
import { usePortfolio } from "@/hooks/usePortfolio";

const tabs = [
  { value: "overview", label: "Overview", icon: ShieldCheck },
  { value: "gaps", label: "Gaps", icon: AlertTriangle },
  { value: "overlaps", label: "Overlaps", icon: Layers },
  { value: "conflicts", label: "Conflicts", icon: GitCompare },
  { value: "scenarios", label: "Scenarios", icon: TrendingUp },
];

function formatCents(cents: number): string {
  const dollars = cents / 100;
  if (dollars >= 1_000_000) return `S$${(dollars / 1_000_000).toFixed(1)}M`;
  if (dollars >= 1_000) return `S$${(dollars / 1_000).toFixed(0)}K`;
  return `S$${dollars.toFixed(0)}`;
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [guideDismissed, setGuideDismissed] = useState(false);
  const { data: policies, isLoading, error } = usePortfolio();

  const isEmpty = !isLoading && (!policies || policies.length === 0);

  const totalSumAssured = policies?.reduce((s, p) => s + (p.sumAssuredCents || 0), 0) ?? 0;
  const uniqueInsurers = new Set(policies?.map((p) => p.insurerCode)).size ?? 0;

  return (
    <div className="container py-6 md:py-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6 md:mb-8">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">Your Insurance Portfolio</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">
            {isLoading ? (
              <span className="flex items-center gap-1">
                <Loader2 className="h-3 w-3 animate-spin" />
                Loading your policies...
              </span>
            ) : isEmpty ? (
              "No policies yet"
            ) : (
              `${policies!.length} policy${policies!.length === 1 ? "" : "s"} from ${uniqueInsurers} insurer${uniqueInsurers === 1 ? "" : "s"} — ${formatCents(totalSumAssured)} total sum assured`
            )}
          </p>
        </div>
        <Link href="/upload" className="shrink-0">
          <Button>Add More Policies</Button>
        </Link>
      </div>

      {isEmpty && !isLoading ? (
        <>
          <Card className="py-12 text-center">
            <CardContent>
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h2 className="text-xl font-semibold mb-2">No policies yet</h2>
              <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                Upload your first insurance policy PDF to get an instant analysis of your coverage.
                We support term life, whole life, critical illness, hospitalisation, and more.
              </p>
              <Link href="/upload">
                <Button size="lg">Upload Your First Policy</Button>
              </Link>
            </CardContent>
          </Card>
          {!guideDismissed && (
            <div className="mt-6">
              <GettingStartedGuide dismissed={guideDismissed} onDismiss={() => setGuideDismissed(true)} />
            </div>
          )}
        </>
      ) : (
        <>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
            {/* Sum Assured — dominant metric, spans 2 columns on large screens */}
            <Card className="sm:col-span-2 bg-primary/5 border-primary/20">
              <CardContent className="pt-5">
                <p className="text-sm font-medium text-primary mb-1">Total Sum Assured</p>
                <p className="text-3xl md:text-4xl font-bold tracking-tight">
                  {isLoading ? "—" : formatCents(totalSumAssured)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">SGD · across {uniqueInsurers} insurer{uniqueInsurers === 1 ? "" : "s"}</p>
              </CardContent>
            </Card>
            {/* Policies count */}
            <Card>
              <CardContent className="pt-5">
                <p className="text-sm font-medium text-muted-foreground mb-1">Policies</p>
                <p className="text-3xl md:text-4xl font-bold tracking-tight">
                  {isLoading ? "—" : policies!.length}
                </p>
                <p className="text-xs text-muted-foreground mt-1">active in portfolio</p>
              </CardContent>
            </Card>
            {/* Annual premium */}
            <Card>
              <CardContent className="pt-5">
                <p className="text-sm font-medium text-muted-foreground mb-1">Annual Premium</p>
                <p className="text-3xl md:text-4xl font-bold tracking-tight">
                  {isLoading
                    ? "—"
                    : formatCents(
                        policies!.reduce(
                          (s, p) =>
                            s +
                            (p.premiumFrequency === "monthly"
                              ? (p.premiumAmountCents || 0) * 12
                              : p.premiumAmountCents || 0),
                          0
                        )
                      )}
                </p>
                <p className="text-xs text-muted-foreground mt-1">estimated</p>
              </CardContent>
            </Card>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-5">
              {tabs.map((tab) => (
                <TabsTrigger key={tab.value} value={tab.value} className="gap-2">
                  <tab.icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </TabsTrigger>
              ))}
            </TabsList>

            <TabsContent value="overview">
              <CoverageOverview policies={policies ?? []} />
            </TabsContent>
            <TabsContent value="gaps">
              <GapAnalysis />
            </TabsContent>
            <TabsContent value="overlaps">
              <OverlapMap />
            </TabsContent>
            <TabsContent value="conflicts">
              <ConflictAlerts />
            </TabsContent>
            <TabsContent value="scenarios">
              <ScenarioBuilder />
            </TabsContent>
          </Tabs>
        </>
      )}

      <div className="mt-6">
        <MASDisclaimer />
      </div>

      <DisclaimerBanner />

      {!isEmpty && !isLoading && (
        <div className="mt-6">
          <h3 className="font-semibold mb-3">Your Policies</h3>
          <div className="space-y-2">
            {policies!.map((policy) => (
              <Link key={policy.id} href={`/policy/${policy.id}`}>
                <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                  <CardContent className="flex items-center justify-between py-3">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium text-sm">{policy.productName}</p>
                        <p className="text-xs text-muted-foreground">
                          {policy.insurerName} &middot;{" "}
                          {policy.productType.replace("_", " ")}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium">
                        {formatCents(policy.sumAssuredCents)}
                      </span>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
