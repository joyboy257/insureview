import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface Gap {
  coverage_type: string;
  severity: string;
  description: string;
  recommendation?: string;
  covered_by_policy_ids: string[];
  gap_amount_cents: number | null;
}

export interface Overlap {
  coverage_type: string;
  severity: string;
  overlapping_policies: Array<{
    policy_id: string;
    product_name: string;
    insurer: string;
    sum_assured_cents: number;
  }>;
  policy_count: number;
  total_sum_assured_cents: number;
  note: string;
}

export interface Conflict {
  conflict_type: string;
  severity: string;
  description: string;
  affected_policies: Array<{
    policy_id: string;
    product_name: string;
    insurer: string;
    detail?: Record<string, unknown>;
  }>;
  detail: Record<string, unknown>;
  resolution_hint: string;
}

export interface AnalysisResult {
  gaps: Gap[];
  overlaps: Overlap[];
  conflicts: Conflict[];
  summary: {
    total_gaps: number;
    critical_gaps: number;
    warning_gaps: number;
    total_overlaps: number;
    warning_overlaps: number;
    total_conflicts: number;
    critical_conflicts: number;
  };
}

async function fetchLatestAnalysis(): Promise<AnalysisResult | null> {
  const { data } = await api.get<AnalysisResult | null>("/analysis");
  return data;
}

async function runAnalysis(policyIds?: string[]): Promise<{ id: string }> {
  const { data } = await api.post<{ id: string }>("/analysis", {
    policy_ids: policyIds,
  });
  return data;
}

export function useAnalysis() {
  const query = useQuery<AnalysisResult | null>({
    queryKey: ["analysis"],
    queryFn: fetchLatestAnalysis,
    staleTime: 1000 * 60, // 1 minute
  });

  const mutation = useMutation({
    mutationFn: runAnalysis,
    onSuccess: () => {
      // Refetch analysis after running
      query.refetch();
    },
  });

  return {
    analysis: query.data ?? null,
    isLoading: query.isLoading,
    isRunning: mutation.isPending,
    runAnalysis: mutation.mutate,
    refetch: query.refetch,
  };
}
