import { AlertCircle } from "lucide-react";

interface Exclusion {
  id: string;
  exclusionText: string;
  category: string | null;
}

const CATEGORY_LABELS: Record<string, string> = {
  self_inflicted: "Self-inflicted",
  pre_existing: "Pre-existing condition",
  war: "War / terrorism",
  dangerous_hobby: "Dangerous activities",
  substance_abuse: "Substance abuse",
  travel_advisory: "Travel advisory",
};

export function ExclusionList({ exclusions }: { exclusions: Exclusion[] }) {
  return (
    <div className="space-y-3">
      {exclusions.map((exclusion) => (
        <div key={exclusion.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
          <AlertCircle className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm">{exclusion.exclusionText}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {exclusion.category ? (CATEGORY_LABELS[exclusion.category] ?? exclusion.category) : "General"}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
