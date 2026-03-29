/**
 * MAS Disclaimer Banner
 *
 * Non-dismissible, visually prominent sandbox compliance notice.
 * Appears on every page via the root layout.
 */
export function MASDisclaimer() {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
      <strong>Important:</strong> This service is an informational tool only. It is not
      regulated by the Monetary Authority of Singapore (MAS) as a financial advisory
      service. Nothing on this site constitutes financial advice.
    </div>
  );
}
