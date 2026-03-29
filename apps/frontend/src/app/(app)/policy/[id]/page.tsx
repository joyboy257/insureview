"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { BenefitList } from "@/components/policy/BenefitList";
import { ExclusionList } from "@/components/policy/ExclusionList";
import { PlainEnglishSummary } from "@/components/policy/PlainEnglishSummary";
import { MASDisclaimer } from "@/components/dashboard/MASDisclaimer";
import { getPolicy } from "@/lib/api";

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

const STATUS_BADGE: Record<string, { variant: "success" | "destructive" | "warning" | "secondary"; label: string }> = {
  active: { variant: "success", label: "Active" },
  lapsed: { variant: "destructive", label: "Lapsed" },
  surrendered: { variant: "warning", label: "Surrendered" },
  reduced: { variant: "secondary", label: "Reduced" },
};

function formatCents(cents: number | null): string {
  if (cents === null || cents === undefined) return "—";
  const dollars = cents / 100;
  return `S$${dollars.toLocaleString()}`;
}

export default function PolicyDetailPage({ params }: { params: { id: string } }) {
  const { data: policy, isLoading, error } = useQuery({
    queryKey: ["policy", params.id],
    queryFn: () => getPolicy(params.id),
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="container py-16 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !policy) {
    return (
      <div className="container py-16 text-center">
        <AlertCircle className="h-8 w-8 mx-auto text-destructive mb-4" />
        <h2 className="text-xl font-semibold mb-2">Policy not found</h2>
        <p className="text-muted-foreground mb-6">
          This policy may have been deleted or you don&apos;t have access.
        </p>
        <Link href="/dashboard">
          <Button variant="outline">Back to Dashboard</Button>
        </Link>
      </div>
    );
  }

  const statusInfo = STATUS_BADGE[policy.policyStatus] ?? {
    variant: "secondary" as const,
    label: policy.policyStatus,
  };

  return (
    <div className="container py-8 max-w-4xl">
      <div className="mb-6">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="mb-2 pl-0">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold">{policy.productName}</h1>
              <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
            </div>
            <p className="text-muted-foreground">
              {policy.insurerName}
              {policy.policyNumber && ` · ${policy.policyNumber}`}
              &middot; {PRODUCT_TYPE_LABELS[policy.productType] ?? policy.productType}
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{formatCents(policy.sumAssuredCents)}</p>
            <p className="text-sm text-muted-foreground">sum assured</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6">
        {policy.plainEnglishSummary && (
          <Card>
            <CardHeader>
              <CardTitle>Plain English Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <PlainEnglishSummary text={policy.plainEnglishSummary} />
              <div className="mt-4 flex flex-wrap gap-4 text-sm text-muted-foreground">
                {policy.issueDate && <span>Issued: {policy.issueDate}</span>}
                {policy.expiryDate && <span>Expires: {policy.expiryDate}</span>}
                {policy.premiumAmountCents && (
                  <span>
                    Premium: {formatCents(policy.premiumAmountCents)}/
                    {policy.premiumFrequency}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  Parse confidence: {(policy.parseConfidence * 100).toFixed(0)}%
                  {policy.parseConfidence > 0.9 ? (
                    <CheckCircle className="h-3 w-3 text-green-600" />
                  ) : (
                    <AlertCircle className="h-3 w-3 text-amber-600" />
                  )}
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {policy.benefits.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Benefits ({policy.benefits.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <BenefitList
                benefits={policy.benefits.map((b) => ({
                  id: b.id,
                  benefitType: b.benefitType,
                  triggerDescription: b.triggerDescription ?? null,
                  payoutType: b.payoutType ?? null,
                  amountCents: b.amountCents ?? null,
                  isActive: b.isActive,
                }))}
              />
            </CardContent>
          </Card>
        )}

        {policy.riders.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Riders ({policy.riders.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {policy.riders.map((rider) => (
                  <div
                    key={rider.id}
                    className="flex items-center justify-between border-b pb-3 last:border-0"
                  >
                    <div>
                      <p className="font-medium text-sm">{rider.riderName}</p>
                      {rider.riderType && (
                        <p className="text-xs text-muted-foreground capitalize">
                          {rider.riderType.replace("_", " ")} rider
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      {rider.additionalSumAssuredCents !== null && (
                        <p className="text-sm font-medium">
                          +{formatCents(rider.additionalSumAssuredCents)}
                        </p>
                      )}
                      {rider.additionalPremiumCents !== null && (
                        <p className="text-xs text-muted-foreground">
                          +{formatCents(rider.additionalPremiumCents)}/yr
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {policy.exclusions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Key Exclusions ({policy.exclusions.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <ExclusionList
                exclusions={policy.exclusions.map((e) => ({
                  id: e.id,
                  exclusionText: e.exclusionText,
                  category: e.exclusionCategory ?? null,
                }))}
              />
            </CardContent>
          </Card>
        )}

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <FileText className="h-3 w-3" />
          <span>Policy parsed from uploaded PDF</span>
        </div>
      </div>

      <div className="mt-8">
        <MASDisclaimer />
      </div>
    </div>
  );
}
