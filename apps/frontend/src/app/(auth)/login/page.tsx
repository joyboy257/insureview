"use client";

import { useState } from "react";
import Link from "next/link";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { ShieldCheck, Mail, ArrowRight, Loader2, User } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";

const DEMO_USERS = [
  {
    id: "sarah",
    name: "Sarah Chen",
    description: "5 policies — whole life, term, endowment, hospitalisation",
  },
  {
    id: "ravi",
    name: "Ravi Kumar",
    description: "5 policies — whole life, term, hospitalisation, investment-linked",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const result = await signIn("email", {
        email: email.trim(),
        redirect: false,
      });
      if (result?.error) {
        setError("Failed to send magic link. Please try again.");
      } else {
        setSubmitted(true);
      }
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDemoLogin(demoUserId: string) {
    setDemoLoading(demoUserId);
    setError(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/demo-login/${demoUserId}`,
        { method: "POST" }
      );
      if (!res.ok) throw new Error("Demo login failed");
      const data = await res.json();
      localStorage.setItem("session_token", data.token);
      await signIn("credentials", {
        token: data.token,
        redirect: false,
      });
      router.push("/dashboard");
    } catch {
      setError("Demo login failed. Make sure the backend is running.");
    } finally {
      setDemoLoading(null);
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center space-y-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
              <Mail className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Check your email</h2>
              <p className="mt-2 text-muted-foreground text-sm">
                We sent a magic link to <span className="font-medium text-foreground">{email}</span>.
                Click the link in the email to sign in. The link expires in 15 minutes.
              </p>
            </div>
            <Button variant="outline" className="w-full" onClick={() => setSubmitted(false)}>
              Use a different email
            </Button>
            <p className="text-xs text-muted-foreground">
              Didn&apos;t receive the email? Check your spam folder or{" "}
              <button
                className="underline hover:text-foreground"
                onClick={() => setSubmitted(false)}
              >
                try again
              </button>
              .
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container flex items-center justify-between py-4">
          <Link href="/" className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <span className="font-semibold text-lg">Insureview</span>
          </Link>
          <Link href="/">
            <Button variant="ghost" size="sm">Back to home</Button>
          </Link>
        </div>
      </header>

      {/* Login form */}
      <div className="flex-1 flex items-center justify-center px-4 py-16 bg-slate-50">
        <div className="w-full max-w-md space-y-6">
          {/* Demo login section */}
          <Card className="border-amber-200 bg-amber-50">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-amber-700" />
                <CardTitle className="text-base text-amber-900">Try without an account</CardTitle>
              </div>
              <CardDescription className="text-amber-700 text-xs">
                Explore with sample insurance data — no email required
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {DEMO_USERS.map((user) => (
                <button
                  key={user.id}
                  onClick={() => handleDemoLogin(user.id)}
                  disabled={!!demoLoading}
                  className="w-full text-left px-3 py-2.5 rounded-md border border-amber-200 bg-white hover:bg-amber-100 transition-colors disabled:opacity-50 flex items-center justify-between"
                >
                  <div>
                    <div className="text-sm font-medium text-amber-900">{user.name}</div>
                    <div className="text-xs text-amber-700">{user.description}</div>
                  </div>
                  {demoLoading === user.id ? (
                    <Loader2 className="h-4 w-4 text-amber-600 animate-spin" />
                  ) : (
                    <ArrowRight className="h-4 w-4 text-amber-600" />
                  )}
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-slate-50 px-2 text-muted-foreground">or continue with email</span>
            </div>
          </div>

          {/* Magic link form */}
          <Card>
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl">Sign in</CardTitle>
              <CardDescription>
                Enter your email to receive a magic link. No password needed.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    Email address
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoFocus
                    autoComplete="email"
                    disabled={loading}
                  />
                </div>

                {error && (
                  <p className="text-sm text-destructive">{error}</p>
                )}

                <Button type="submit" className="w-full" disabled={loading || !email.trim()}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending link...
                    </>
                  ) : (
                    <>
                      Send magic link
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 pt-6 border-t text-center">
                <p className="text-sm text-muted-foreground">
                  Don&apos;t have an account?{" "}
                  <span className="text-foreground font-medium">
                    Just enter your email above — you&apos;ll be signed up automatically.
                  </span>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
