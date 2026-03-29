import Link from "next/link";
import { ShieldCheck, Upload, BarChart3, AlertTriangle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { MASDisclaimer } from "@/components/dashboard/MASDisclaimer";

/* Inline SVG illustration: abstract policy document + coverage chart — brand anchor */
function HeroIllustration() {
  return (
    <svg
      viewBox="0 0 480 320"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mx-auto mt-12 w-full max-w-lg opacity-90"
      aria-hidden="true"
    >
      {/* Background card shadow */}
      <rect x="40" y="50" width="260" height="200" rx="12" fill="hsl(174,52%,32%)" opacity="0.08" />
      {/* Back document */}
      <rect x="56" y="30" width="240" height="188" rx="8" fill="white" stroke="hsl(214,32%,91%)" strokeWidth="1.5" />
      {/* Document header bar */}
      <rect x="56" y="30" width="240" height="36" rx="8" fill="hsl(174,52%,32%)" />
      <rect x="56" y="58" width="240" height="8" fill="hsl(174,52%,32%)" />
      {/* Document lines */}
      {[0,1,2,3,4].map(i => (
        <rect key={i} x="76" y={80 + i * 18} width={160 + (i % 2) * 40} height="6" rx="3" fill="hsl(215,16%,47%)" opacity={0.15 + i * 0.03} />
      ))}
      {/* Coverage bars — partial fill */}
      <rect x="280" y="100" width="120" height="18" rx="4" fill="hsl(174,52%,32%)" opacity="0.12" />
      <rect x="280" y="100" width="72" height="18" rx="4" fill="hsl(174,52%,32%)" opacity="0.5" />
      <rect x="280" y="126" width="120" height="18" rx="4" fill="hsl(174,52%,32%)" opacity="0.12" />
      <rect x="280" y="126" width="108" height="18" rx="4" fill="hsl(174,52%,32%)" opacity="0.5" />
      <rect x="280" y="152" width="120" height="18" rx="4" fill="hsl(174,52%,32%)" opacity="0.12" />
      <rect x="280" y="152" width="36" height="18" rx="4" fill="#DC2626" opacity="0.7" />
      {/* Gap indicator arrow */}
      <path d="M360 161 L396 161" stroke="#DC2626" strokeWidth="2" strokeLinecap="round" markerEnd="url(#arrow)" />
      {/* Warning dot */}
      <circle cx="424" cy="161" r="10" fill="#DC2626" />
      <text x="424" y="165" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">!</text>
      {/* Coverage label */}
      <text x="280" y="92" fontSize="9" fill="hsl(215,16%,47%)" fontFamily="sans-serif">Coverage</text>
      <text x="280" y="118" fontSize="9" fill="hsl(215,16%,47%)" fontFamily="sans-serif">Gap</text>
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#DC2626" />
        </marker>
      </defs>
    </svg>
  );
}

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container flex items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <span className="font-semibold text-lg">Insureview</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/upload">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="py-20 text-center">
          <div className="container">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-6">
              See your entire insurance picture &mdash;&nbsp;
              <span className="text-primary">in plain English</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
              Upload your Singapore insurance policies. Get an instant analysis of
              coverage gaps, overlaps, and conflicts across your portfolio.
            </p>
            <div className="flex justify-center gap-4 mb-4">
              <Link href="/upload">
                <Button size="lg">
                  Upload Your Policies
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="outline">
                  View Sample Dashboard
                </Button>
              </Link>
            </div>
            <HeroIllustration />
          </div>
        </section>

        <section className="py-16 bg-slate-50">
          <div className="container">
            <div className="grid md:grid-cols-3 gap-8">
              <Card>
                <CardHeader>
                  <Upload className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>1. Upload</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground">
                  Drop your policy PDFs. We read every page using AI trained on
                  Singapore insurance products. Your PDFs are deleted immediately
                  after parsing.
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <BarChart3 className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>2. Analyze</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground">
                  We map every benefit, rider, and exclusion across all your
                  policies into a unified view. We flag gaps, overlaps, and
                  potential conflicts.
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <AlertTriangle className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>3. Understand</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground">
                  See your coverage in plain English. Compare against Singapore
                  household benchmarks. Know what you have and what you do not.
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="container">
            <h2 className="text-2xl font-bold text-center mb-10">
              What We Analyze
            </h2>
            <div className="grid sm:grid-cols-2 gap-x-16 gap-y-6 max-w-3xl mx-auto">
              {[
                { label: "Life Insurance", desc: "Term, whole life, and endowment" },
                { label: "Critical Illness", desc: "LIA 37-condition definitions" },
                { label: "Hospitalisation", desc: "MediShield Life and Integrated Shield Plans" },
                { label: "Disability Income", desc: "TPD and income replacement coverage" },
              ].map((item, i) => (
                <div key={item.label} className="flex items-start gap-4">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center mt-0.5">
                    {i + 1}
                  </span>
                  <div>
                    <p className="font-medium text-sm">{item.label}</p>
                    <p className="text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16 bg-amber-50 border-t border-amber-200">
          <div className="container">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="text-2xl font-bold mb-4">Important Notice</h2>
              <p className="text-amber-900">
                This service provides informational analysis only. It does not
                constitute financial advice. Consult a licensed financial adviser
                before making any insurance decisions. Insureview is not regulated
                by the Monetary Authority of Singapore as a financial advisory
                service.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t py-6">
        <div className="container flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <p>&copy; 2026 Insureview. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="/privacy" className="hover:underline">
              Privacy Policy
            </Link>
            <Link href="/disclaimer" className="hover:underline">
              Disclaimer
            </Link>
            <Link href="/terms" className="hover:underline">
              Terms of Service
            </Link>
          </div>
        </div>
      </footer>

      <MASDisclaimer />
    </div>
  );
}
