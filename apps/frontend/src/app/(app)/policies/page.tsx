"use client";

import Link from "next/link";
import { FileText, ChevronRight, Loader2, Plus } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { usePortfolio } from "@/hooks/usePortfolio";

function formatCents(cents: number): string {
  const dollars = cents / 100;
  if (dollars >= 1_000_000) return `S$${(dollars / 1_000_000).toFixed(1)}M`;
  if (dollars >= 1_000) return `S$${(dollars / 1_000).toFixed(0)}K`;
  return `S$${dollars.toFixed(0)}`;
}

const PRODUCT_TYPE_LABELS: Record<string, string> = {
  TERM_LIFE: "Term Life",
  WHOLE_LIFE: "Whole Life",
  CRITICAL_ILLNESS: "Critical Illness",
  HOSPITALISATION: "Hospitalisation",
  MEDISHIELD_LIFE: "MediShield Life",
  IP: "Integrated Shield Plan",
  DISABILITY: "Disability Income",
  ACCIDENT: "Personal Accident",
  ENDOWMENT: "Endowment",
};

const STATUS_COLORS: Record<string, string> = {
  active: "text-green-600 bg-green-50",
  lapsed: "text-red-600 bg-red-50",
  surrendered: "text-yellow-600 bg-yellow-50",
  reduced: "text-orange-600 bg-orange-50",
};

export default function PoliciesPage() {
  const { data: policies, isLoading, error } = usePortfolio();

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Your Policies</h1>
          <p className="text-muted-foreground mt-1">
            {isLoading
              ? "Loading..."
              : policies
              ? `${policies.length} policy${policies.length === 1 ? "" : "s"} parsed`
              : "Unable to load policies"}
          </p>
        </div>
        <Link href="/upload">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Policy
          </Button>
        </Link>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="h-6 w-6 mr-2 animate-spin" />
          Loading your policies...
        </div>
      )}

      {error && (
        <Card className="py-8 text-center">
          <CardContent>
            <p className="text-muted-foreground">
              Failed to load policies. Please refresh the page or contact support.
            </p>
          </CardContent>
        </Card>
      )}

      {!isLoading && policies?.length === 0 && (
        <Card className="py-16 text-center">
          <CardContent>
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">No policies yet</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Upload your first insurance policy PDF to start building your portfolio view.
            </p>
            <Link href="/upload">
              <Button>Upload Your First Policy</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {policies && policies.length > 0 && (
        <div className="space-y-3">
          {policies.map((policy) => (
            <Link key={policy.id} href={`/policy/${policy.id}`}>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <FileText className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-medium">{policy.productName}</p>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            STATUS_COLORS[policy.policyStatus] ?? "text-gray-600 bg-gray-50"
                          }`}
                        >
                          {policy.policyStatus}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-0.5">
                        {policy.insurerName}
                        {policy.policyNumber && ` · ${policy.policyNumber}`}
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {PRODUCT_TYPE_LABELS[policy.productType] ?? policy.productType}
                        {policy.policyYear && ` · Year ${policy.policyYear}`}
                        {policy.expiryDate && ` · Expires ${policy.expiryDate}`}
                      </p>
                      {policy.plainEnglishSummary && (
                        <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                          {policy.plainEnglishSummary}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 ml-4 shrink-0">
                    <div className="text-right">
                      <p className="text-sm font-semibold">
                        {formatCents(policy.sumAssuredCents)}
                      </p>
                      <p className="text-xs text-muted-foreground">sum assured</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
