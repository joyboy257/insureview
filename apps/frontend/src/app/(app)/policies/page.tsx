"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  FileText,
  Loader2,
  Plus,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Progress } from "@/components/ui/Progress";
import { usePortfolio } from "@/hooks/usePortfolio";
import type { PolicySummary } from "@/lib/api";

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

const STATUS_VARIANTS: Record<string, "success" | "destructive" | "warning" | "secondary"> = {
  active: "success",
  lapsed: "destructive",
  surrendered: "warning",
  reduced: "warning",
  pending: "secondary",
  expired: "destructive",
};

function formatCents(cents: number): string {
  const dollars = cents / 100;
  if (dollars >= 1_000_000) return `S$${(dollars / 1_000_000).toFixed(2)}M`;
  if (dollars >= 1_000) return `S$${(dollars / 1_000).toFixed(0)}K`;
  return `S$${dollars.toFixed(0)}`;
}

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

type SortKey = "createdAt" | "sumAssuredCents" | "insurerName";
type SortDir = "asc" | "desc";

function SortIcon({ col, sortKey, sortDir }: { col: SortKey; sortKey: SortKey; sortDir: SortDir }) {
  if (sortKey !== col) return <ChevronsUpDown className="h-4 w-4 text-muted-foreground/40" />;
  return sortDir === "asc" ? (
    <ChevronUp className="h-4 w-4 text-primary" />
  ) : (
    <ChevronDown className="h-4 w-4 text-primary" />
  );
}

export default function PoliciesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: policies, isLoading, error } = usePortfolio();

  // Filter state
  const [insurerFilter, setInsurerFilter] = React.useState(searchParams.get("insurer") ?? "");
  const [typeFilter, setTypeFilter] = React.useState(searchParams.get("type") ?? "");
  const [statusFilter, setStatusFilter] = React.useState(searchParams.get("status") ?? "");

  // Sort state
  const [sortKey, setSortKey] = React.useState<SortKey>("createdAt");
  const [sortDir, setSortDir] = React.useState<SortDir>("desc");

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  // Unique values for filter dropdowns
  const insurers = React.useMemo(
    () =>
      policies
        ? Array.from(new Set(policies.map((p) => p.insurerName))).sort()
        : [],
    [policies]
  );
  const productTypes = React.useMemo(
    () =>
      policies
        ? Array.from(new Set(policies.map((p) => p.productType))).sort()
        : [],
    [policies]
  );
  const statuses = React.useMemo(
    () =>
      policies
        ? Array.from(new Set(policies.map((p) => p.policyStatus))).sort()
        : [],
    [policies]
  );

  const filtered = React.useMemo(() => {
    if (!policies) return [];
    return policies
      .filter((p) => {
        if (insurerFilter && p.insurerName !== insurerFilter) return false;
        if (typeFilter && p.productType !== typeFilter) return false;
        if (statusFilter && p.policyStatus !== statusFilter) return false;
        return true;
      })
      .sort((a, b) => {
        let cmp = 0;
        if (sortKey === "createdAt") {
          cmp = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
        } else if (sortKey === "sumAssuredCents") {
          cmp = a.sumAssuredCents - b.sumAssuredCents;
        } else if (sortKey === "insurerName") {
          cmp = a.insurerName.localeCompare(b.insurerName);
        }
        return sortDir === "asc" ? cmp : -cmp;
      });
  }, [policies, insurerFilter, typeFilter, statusFilter, sortKey, sortDir]);

  function clearFilters() {
    setInsurerFilter("");
    setTypeFilter("");
    setStatusFilter("");
  }

  const hasFilters = insurerFilter || typeFilter || statusFilter;

  return (
    <div className="container py-8">
      {/* Header */}
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

      {/* Filter Bar */}
      {policies && policies.length > 0 && (
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <select
            className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            value={insurerFilter}
            onChange={(e) => setInsurerFilter(e.target.value)}
          >
            <option value="">All Insurers</option>
            {insurers.map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>

          <select
            className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="">All Types</option>
            {productTypes.map((t) => (
              <option key={t} value={t}>
                {PRODUCT_TYPE_LABELS[t] ?? t}
              </option>
            ))}
          </select>

          <select
            className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            {statuses.map((s) => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>

          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4 mr-1" />
              Clear
            </Button>
          )}

          <span className="ml-auto text-sm text-muted-foreground">
            {filtered.length} result{filtered.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="h-6 w-6 mr-2 animate-spin" />
          Loading your policies...
        </div>
      )}

      {/* Error */}
      {error && (
        <Card className="py-8 text-center">
          <CardContent>
            <p className="text-muted-foreground">
              Failed to load policies. Please refresh the page or contact support.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Empty */}
      {!isLoading && !error && policies?.length === 0 && (
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

      {/* No filter results */}
      {!isLoading && !error && policies && policies.length > 0 && filtered.length === 0 && (
        <Card className="py-12 text-center">
          <CardContent>
            <p className="text-muted-foreground mb-4">
              No policies match your current filters.
            </p>
            <Button variant="outline" onClick={clearFilters}>
              Clear filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Table */}
      {!isLoading && !error && filtered.length > 0 && (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted/50 border-b">
                <th className="text-left p-3 font-medium">
                  <button
                    className="flex items-center gap-1 hover:text-foreground transition-colors"
                    onClick={() => handleSort("insurerName")}
                  >
                    Insurer
                    <SortIcon col="insurerName" sortKey={sortKey} sortDir={sortDir} />
                  </button>
                </th>
                <th className="text-left p-3 font-medium">Product</th>
                <th className="text-left p-3 font-medium">Type</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-right p-3 font-medium">
                  <button
                    className="ml-auto flex items-center gap-1 hover:text-foreground transition-colors"
                    onClick={() => handleSort("sumAssuredCents")}
                  >
                    Sum Assured
                    <SortIcon col="sumAssuredCents" sortKey={sortKey} sortDir={sortDir} />
                  </button>
                </th>
                <th className="text-left p-3 font-medium">Premium</th>
                <th className="text-right p-3 font-medium">
                  <button
                    className="ml-auto flex items-center gap-1 hover:text-foreground transition-colors"
                    onClick={() => handleSort("createdAt")}
                  >
                    Added
                    <SortIcon col="createdAt" sortKey={sortKey} sortDir={sortDir} />
                  </button>
                </th>
                <th className="text-right p-3 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((policy, idx) => (
                <tr
                  key={policy.id}
                  className={`border-b last:border-0 hover:bg-muted/30 cursor-pointer transition-colors ${
                    idx % 2 === 0 ? "bg-white" : "bg-muted/10"
                  }`}
                  onClick={() => router.push(`/policy/${policy.id}`)}
                >
                  <td className="p-3">
                    <div className="font-medium">{policy.insurerName}</div>
                    {policy.policyNumber && (
                      <div className="text-xs text-muted-foreground">{policy.policyNumber}</div>
                    )}
                  </td>
                  <td className="p-3">
                    <div className="font-medium">{policy.productName}</div>
                    {policy.expiryDate && (
                      <div className="text-xs text-muted-foreground">
                        Expires {policy.expiryDate}
                      </div>
                    )}
                  </td>
                  <td className="p-3">
                    <span className="text-muted-foreground">
                      {PRODUCT_TYPE_LABELS[policy.productType] ?? policy.productType}
                    </span>
                  </td>
                  <td className="p-3">
                    <Badge variant={STATUS_VARIANTS[policy.policyStatus] ?? "secondary"}>
                      {policy.policyStatus.charAt(0).toUpperCase() + policy.policyStatus.slice(1)}
                    </Badge>
                  </td>
                  <td className="p-3 text-right font-semibold">
                    {formatCents(policy.sumAssuredCents)}
                  </td>
                  <td className="p-3 text-muted-foreground">
                    {policy.premiumAmountCents != null
                      ? `${formatCents(policy.premiumAmountCents)} / ${policy.premiumFrequency}`
                      : "—"}
                  </td>
                  <td className="p-3 text-right text-muted-foreground">
                    {new Date(policy.createdAt).toLocaleDateString("en-SG", {
                      day: "2-digit",
                      month: "short",
                      year: "numeric",
                    })}
                  </td>
                  <td className="p-3">
                    <div className="flex items-center justify-end gap-2">
                      <span className="text-xs text-muted-foreground w-10 text-right">
                        {formatConfidence(policy.parseConfidence)}
                      </span>
                      <div className="w-16">
                        <Progress
                          value={policy.parseConfidence * 100}
                          className="h-1.5"
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
