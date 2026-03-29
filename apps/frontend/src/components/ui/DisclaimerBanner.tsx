import { AlertTriangle } from "lucide-react";

export function DisclaimerBanner() {
  return (
    <div className="mt-8 border-t border-amber-200 bg-amber-50 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-900">
          <strong className="font-semibold">Important:</strong> This analysis is for
          informational purposes only. It does not constitute financial advice.
          Consult a licensed financial adviser before making any insurance decisions.
          This service is not regulated by the Monetary Authority of Singapore.
        </div>
      </div>
    </div>
  );
}
