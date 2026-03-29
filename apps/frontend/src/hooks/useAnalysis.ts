import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface Gap {
  coverage_type: string;
  severity: string;
  description: string;
  recommendation?: string | null;
  covered_by_policy_ids: string[];
  gap_amount_cents: number | null;
  current_amount_cents?: number | null;
}

export interface OverlappingPolicy {
  policy_id: string;
  product_name: string;
  insurer: string;
  sum_assured_cents: number;
}

export interface Overlap {
  coverage_type: string;
  severity: string;
  overlapping_policies: OverlappingPolicy[];
  policy_count: number;
  total_sum_assured_cents: number;
  note: string;
}

export interface AffectedPolicy {
  policy_id: string;
  product_name: string;
  insurer: string;
  detail?: Record<string, unknown>;
}

export interface Conflict {
  conflict_type: string;
  severity: string;
  description: string;
  affected_policies: AffectedPolicy[];
  resolution_hint: string;
}

export interface AnalysisData {
  gaps: Gap[];
  overlaps: Overlap[];
  conflicts: Conflict[];
  plain_english_summary: string;
}

/** Shape returned by GET /api/v1/analysis */
interface AnalysisApiResponse {
  data: AnalysisData;
  mas_disclaimer: string;
  generated_at: string;
  disclaimer_version: string;
}

async function fetchLatestAnalysis(): Promise<AnalysisData | null> {
  const { data: response } = await api.get<AnalysisApiResponse>("/analysis");
  // API returns { data: { gaps, overlaps, conflicts }, ... }
  return response?.data ?? null;
}

async function runAnalysis(policyIds?: string[]): Promise<{ id: string }> {
  const { data } = await api.post<{ id: string }>("/analysis", {
    policy_ids: policyIds,
  });
  return data;
}

export function useAnalysis() {
  const query = useQuery<AnalysisData | null>({
    queryKey: ["analysis"],
    queryFn: fetchLatestAnalysis,
    staleTime: 1000 * 60, // 1 minute
  });

  const mutation = useMutation({
    mutationFn: runAnalysis,
    onSuccess: () => {
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
