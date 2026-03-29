import { CheckCircle } from "lucide-react";

interface Benefit {
  id: string;
  benefitType: string;
  triggerDescription: string | null;
  payoutType: string | null;
  amountCents: number | null;
  isActive: boolean;
}

export function BenefitList({ benefits }: { benefits: Benefit[] }) {
  return (
    <div className="space-y-4">
      {benefits.map((benefit) => (
        <div key={benefit.id} className="border rounded-lg p-4">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="font-semibold text-sm capitalize">
                {benefit.benefitType.replace("_", " ")}
              </span>
            </div>
            <span className="text-sm font-bold text-green-700">
              {benefit.amountCents != null ? `S$${(benefit.amountCents / 100).toLocaleString()}` : "—"}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">{benefit.triggerDescription ?? "—"}</p>
          <p className="text-xs text-muted-foreground mt-1 capitalize">
            Payout type: {benefit.payoutType?.replace("_", " ") ?? "—"}
          </p>
        </div>
      ))}
    </div>
  );
}
