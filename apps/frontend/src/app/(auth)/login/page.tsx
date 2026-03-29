"use client";

import { useState } from "react";
import Link from "next/link";
import { signIn } from "next-auth/react";
import { ShieldCheck, Mail, ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
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
        <Card className="w-full max-w-md">
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
  );
}
