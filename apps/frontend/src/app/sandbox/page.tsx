"use client";

import { useState } from "react";
import { CheckCircle2, AlertCircle, Loader2, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { DisclaimerBanner } from "@/components/ui/DisclaimerBanner";
import { api } from "@/lib/api";

type TimelineOption = "6_months" | "12_months";

interface FormData {
  companyName: string;
  contactEmail: string;
  website: string;
  productDescription: string;
  targetUsers: string;
  proposedTimeline: TimelineOption;
  expectedUsers: string;
}

interface SubmitResponse {
  status: string;
  applicationId: string;
  nextSteps: string;
}

const TIMELINE_OPTIONS: { value: TimelineOption; label: string }[] = [
  { value: "6_months", label: "6 months" },
  { value: "12_months", label: "12 months" },
];

const INITIAL_FORM: FormData = {
  companyName: "Insureview",
  contactEmail: "",
  website: "https://insureview.sg",
  productDescription: "",
  targetUsers: "Singaporean households with multiple insurance policies",
  proposedTimeline: "12_months",
  expectedUsers: "",
};

export default function SandboxPage() {
  const [form, setForm] = useState<FormData>(INITIAL_FORM);
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [response, setResponse] = useState<SubmitResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  function update(field: keyof FormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setErrorMessage("");
    setResponse(null);

    try {
      const payload = {
        company_name: form.companyName,
        contact_email: form.contactEmail,
        product_description: form.productDescription,
        target_users: form.targetUsers,
        proposed_timeline: form.proposedTimeline,
        expected_users: form.expectedUsers ? Number(form.expectedUsers) : 0,
      };

      const { data } = await api.post<SubmitResponse>("/sandbox", payload);
      setResponse(data);
      setStatus("success");
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    }
  }

  return (
    <div className="container py-10 max-w-3xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <span className="inline-flex items-center rounded-full bg-primary/10 text-primary text-xs font-semibold px-3 py-1">
            FinTech Sandbox
          </span>
          <span className="text-xs text-muted-foreground">Monetary Authority of Singapore</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight">Apply for MAS FinTech Sandbox</h1>
        <p className="text-muted-foreground mt-2 text-base max-w-2xl">
          Insureview is applying to operate under the MAS FinTech Sandbox prior to obtaining a
          full Financial Adviser licence.
        </p>
      </div>

      {/* Explanation Card */}
      <Card className="mb-8 bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="text-lg">About the MAS FinTech Sandbox</CardTitle>
          <CardDescription>
            What it means for Insureview and what restrictions apply
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-foreground/80">
          <p>
            The{" "}
            <a
              href="https://www.mas.gov.sg/development/fintech/sandbox"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline underline-offset-2 inline-flex items-center gap-1"
            >
              MAS FinTech Sandbox <ExternalLink className="h-3 w-3" />
            </a>{" "}
            is a regulatory environment that allows financial technology companies to test
            innovative products in a live environment with real consumers — under a modified
            regulatory regime and enhanced supervisory oversight.
          </p>
          <p>
            Insureview&apos;s portfolio analysis tool will operate within the sandbox before
            potentially seeking a full Financial Adviser (FA) licence under the Financial
            Advisers Act. During the sandbox period, Insureview will be subject to the
            following restrictions:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Services are limited to Singapore resident households with multiple insurance policies</li>
            <li>No handling of client funds or premiums — advisory and analysis only</li>
            <li>Clear disclosure that the service operates under sandbox conditions and is not independently regulated by MAS</li>
            <li>Enhanced data protection and transparency obligations</li>
            <li>Regular reporting to MAS on service usage and any incidents</li>
          </ul>
          <p>
            Submitting this application does not guarantee sandbox admission. MAS will review
            and respond within 5 business days.
          </p>
        </CardContent>
      </Card>

      {/* Success State */}
      {status === "success" && response ? (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <CheckCircle2 className="h-8 w-8 text-green-600 flex-shrink-0" />
              <div>
                <h2 className="text-xl font-semibold text-green-900 mb-1">
                  Application Received
                </h2>
                <p className="text-sm text-green-800 mb-4">
                  Reference ID: <span className="font-mono font-medium">{response.applicationId}</span>
                </p>
                <div className="bg-green-100 border border-green-200 rounded-lg p-4 text-sm text-green-900">
                  <p className="font-medium mb-1">What happens next</p>
                  <p className="text-green-800">{response.nextSteps}</p>
                </div>
                <div className="mt-6">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setStatus("idle");
                      setForm(INITIAL_FORM);
                      setResponse(null);
                    }}
                  >
                    Submit Another Application
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* Application Form */
        <Card>
          <CardHeader>
            <CardTitle>Apply for Sandbox</CardTitle>
            <CardDescription>
              Complete the form below to submit your sandbox application to MAS via Insureview
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Company Info */}
              <fieldset className="space-y-4">
                <legend className="text-sm font-semibold text-foreground mb-3">
                  Company Information
                </legend>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label htmlFor="companyName" className="text-sm font-medium">
                      Company Name
                    </label>
                    <input
                      id="companyName"
                      type="text"
                      value={form.companyName}
                      onChange={(e) => update("companyName", e.target.value)}
                      required
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="Insureview"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label htmlFor="contactEmail" className="text-sm font-medium">
                      Contact Email <span className="text-destructive">*</span>
                    </label>
                    <input
                      id="contactEmail"
                      type="email"
                      value={form.contactEmail}
                      onChange={(e) => update("contactEmail", e.target.value)}
                      required
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="contact@insureview.sg"
                    />
                  </div>
                  <div className="space-y-1.5 sm:col-span-2">
                    <label htmlFor="website" className="text-sm font-medium">
                      Website
                    </label>
                    <input
                      id="website"
                      type="url"
                      value={form.website}
                      onChange={(e) => update("website", e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="https://insureview.sg"
                    />
                  </div>
                </div>
              </fieldset>

              {/* Product Description */}
              <fieldset className="space-y-4">
                <legend className="text-sm font-semibold text-foreground mb-3">
                  Product Description
                </legend>
                <div className="space-y-1.5">
                  <label htmlFor="productDescription" className="text-sm font-medium">
                    Describe your product{" "}
                    <span className="text-destructive">*</span>
                  </label>
                  <textarea
                    id="productDescription"
                    value={form.productDescription}
                    onChange={(e) => update("productDescription", e.target.value)}
                    required
                    rows={4}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 min-h-[80px]"
                    placeholder="Describe the portfolio analysis tool, how it works, and the value it provides to users..."
                  />
                </div>
                <div className="space-y-1.5">
                  <label htmlFor="targetUsers" className="text-sm font-medium">
                    Target Users{" "}
                    <span className="text-destructive">*</span>
                  </label>
                  <textarea
                    id="targetUsers"
                    value={form.targetUsers}
                    onChange={(e) => update("targetUsers", e.target.value)}
                    required
                    rows={2}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 min-h-[60px]"
                    placeholder="e.g. Singaporean households with multiple insurance policies"
                  />
                </div>
              </fieldset>

              {/* Sandbox Details */}
              <fieldset className="space-y-4">
                <legend className="text-sm font-semibold text-foreground mb-3">
                  Sandbox Details
                </legend>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label htmlFor="proposedTimeline" className="text-sm font-medium">
                      Proposed Timeline
                    </label>
                    <select
                      id="proposedTimeline"
                      value={form.proposedTimeline}
                      onChange={(e) =>
                        update("proposedTimeline", e.target.value as TimelineOption)
                      }
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {TIMELINE_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label htmlFor="expectedUsers" className="text-sm font-medium">
                      Expected Number of Users
                    </label>
                    <input
                      id="expectedUsers"
                      type="number"
                      min="1"
                      value={form.expectedUsers}
                      onChange={(e) => update("expectedUsers", e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="e.g. 500"
                    />
                  </div>
                </div>
              </fieldset>

              {/* Error State */}
              {status === "error" && (
                <div className="flex items-start gap-3 rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-sm text-destructive">
                  <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Submit */}
              <div className="pt-2">
                <Button type="submit" size="lg" disabled={status === "loading"} className="w-full sm:w-auto">
                  {status === "loading" ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Submitting...
                    </>
                  ) : (
                    "Submit Application"
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <DisclaimerBanner />
    </div>
  );
}
