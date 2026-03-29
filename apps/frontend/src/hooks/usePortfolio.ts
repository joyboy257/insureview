"use client";

import { useQuery } from "@tanstack/react-query";
import { getPolicies, type PolicySummary } from "@/lib/api";

export function usePortfolio() {
  return useQuery<PolicySummary[]>({
    queryKey: ["portfolio"],
    queryFn: getPolicies,
    staleTime: 1000 * 60 * 5,
    retry: 1,
  });
}
