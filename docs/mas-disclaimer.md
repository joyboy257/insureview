# MAS Disclaimer

> **Important Notice -- Mandatory Disclaimer**
> Applies to: All pages, all API responses, all analysis outputs
> Version: 1.0.0
> Last Updated: 28 March 2026

---

## Display Text (All Pages)

The following disclaimer must appear on every page of the Insureview application:

> **Important:** This analysis is for informational purposes only. It does not constitute financial advice. Consult a licensed financial adviser before making any insurance decisions. Actual policy terms, benefits, and payouts are subject to the full policy documents and insurer discretion. This service is not regulated by the Monetary Authority of Singapore as a financial advisory service.

This text is displayed via the `MASDisclaimer` component (`frontend/src/components/dashboard/MASDisclaimer.tsx`) at the bottom of every dashboard tab, and via the `DisclaimerBanner` component at the bottom of upload and landing pages.

---

## API Response Disclaimer

Every API response from the analysis endpoints includes the following disclaimer text:

> "This analysis is for informational purposes only. It is not financial advice and does not constitute a recommendation to purchase, cancel, or modify any insurance product. Actual policy terms, benefits, and payouts are subject to the full policy documents and insurer discretion. Consult a licensed financial adviser for personalised advice. This service is not regulated by the Monetary Authority of Singapore as a financial advisory service."

This text is returned in the `mas_disclaimer` field of all `AnalysisResponse` objects.

---

## Scenario Output Disclaimer

Every scenario modelling result must include the following notice:

> "This is a hypothetical illustration based on the information in your uploaded policies. Actual payouts depend on the specific circumstances of a claim and are subject to the full terms and conditions of each policy."

---

## Tone Rules for Analysis Output

All plain English analysis output must comply with the following tone rules:

### Never Say
The following phrases must never appear in analysis output:
- "you should", "you need to"
- "recommend", "buy more"
- "cancel this", "switch to"
- "you are at risk", "danger"
- "underinsured", "overpaying", "waste"
- "inadequate coverage", "you lack"
- "you must", "action required", "fix this", "problem detected"

### Always Say
Output should be framed descriptively:
- "your portfolio includes"
- "you have"
- "this analysis shows"
- "it does not include"
- "a typical household carries"
- "based on your declared income"
- "for your consideration"
- "a financial adviser can help you"

### Benchmark Framing
Benchmark comparisons must be framed as descriptive norms, not prescriptive advice:
- GOOD: "Typical Singapore households carry 10-12x annual income in life coverage."
- BAD: "You need 10-12x annual income in life coverage."

---

## Pre-Launch Legal Actions Required

The following must be completed before any public launch:

1. **MAS FinTech Office Pre-Submission Meeting**: Schedule at mas.gov.sg/fintech to confirm the service does not constitute regulated financial advice
2. **Engage Singapore Regulatory Lawyer**: Have Rajah & Tann or Allen & Gledhill review the gap/overlap/conflict framing
3. **Formal Disclaimer Page**: The `/disclaimer` route with full legal text must be live before launch
4. **DPA Review**: Confirm whether the Claude API and GPT-4o DPAs cover insurance document processing under PDPA

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 28 March 2026 | Initial version |
