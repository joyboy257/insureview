"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Upload, BarChart3, AlertTriangle, CheckCircle2, ArrowRight, BookOpen } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

const STEPS = [
  {
    id: "upload",
    icon: Upload,
    title: "Upload your policies",
    description:
      "Drop one or more insurance policy PDFs onto the upload page. We support term life, whole life, critical illness, hospitalisation, endowment, and investment-linked plans.",
    href: "/upload",
    cta: "Go to Upload",
  },
  {
    id: "analyze",
    icon: BarChart3,
    title: "Review your coverage",
    description:
      "Once parsed, your policies appear in the Overview tab. See total sum assured, annual premiums, and a breakdown by insurer at a glance.",
    href: "/dashboard?tab=overview",
    cta: "View Overview",
  },
  {
    id: "gaps",
    icon: AlertTriangle,
    title: "Check for coverage gaps",
    description:
      "Head to the Gaps tab to see where your portfolio may be under-insured — death benefit shortfalls, missing critical illness cover, or hospitalisation limits that are too low.",
    href: "/dashboard?tab=gaps",
    cta: "Find Gaps",
  },
];

interface Props {
  dismissed?: boolean;
  onDismiss: () => void;
}

export function GettingStartedGuide({ dismissed = false, onDismiss }: Props) {
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  useEffect(() => {
    try {
      const saved = localStorage.getItem("insureview_guide_completed");
      if (saved) setCompletedSteps(new Set(JSON.parse(saved)));
    } catch {
      // ignore
    }
  }, []);

  if (dismissed) return null;

  const allDone = completedSteps.size >= STEPS.length;

  function markDone(id: string) {
    const next = new Set(completedSteps);
    next.add(id);
    setCompletedSteps(next);
    try {
      localStorage.setItem("insureview_guide_completed", JSON.stringify([...next]));
    } catch {
      // ignore
    }
  }

  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">Getting Started</CardTitle>
          </div>
          <Button variant="ghost" size="sm" onClick={onDismiss} className="text-xs">
            Dismiss
          </Button>
        </div>
        {!allDone && (
          <p className="text-sm text-muted-foreground mt-1">
            {completedSteps.size} of {STEPS.length} steps completed
          </p>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {STEPS.map((step, idx) => {
          const done = completedSteps.has(step.id);
          const Icon = step.icon;
          return (
            <div
              key={step.id}
              className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                done
                  ? "border-green-200 bg-green-50/50 opacity-70"
                  : "border-primary/10 bg-white hover:border-primary/30"
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  done ? "bg-green-100 text-green-600" : "bg-primary/10 text-primary"
                }`}
              >
                {done ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className={`text-sm font-medium ${done ? "line-through" : ""}`}>
                    {idx + 1}. {step.title}
                  </p>
                </div>
                {!done && (
                  <>
                    <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Link href={step.href}>
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 text-xs gap-1.5"
                          onClick={() => markDone(step.id)}
                        >
                          {step.cta}
                          <ArrowRight className="h-3 w-3" />
                        </Button>
                      </Link>
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })}

        {allDone && (
          <div className="text-center py-2">
            <p className="text-sm text-green-700 font-medium">
              You&apos;re all set — keep your portfolio up to date!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
