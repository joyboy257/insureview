"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { signIn } from "next-auth/react";
import Link from "next/link";
import { ShieldCheck, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";

type VerifyState = "loading" | "success" | "error";

function VerifyContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [state, setState] = useState<VerifyState>("loading");

  useEffect(() => {
    if (!token) {
      setState("error");
      return;
    }

    async function verify() {
      try {
        const result = await signIn("email", {
          email: token, // token is used as the email in callback
          redirect: false,
        });
        if (result?.error) {
          setState("error");
        } else {
          setState("success");
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1500);
        }
      } catch {
        setState("error");
      }
    }

    verify();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-16 bg-slate-50">
      <Card className="w-full max-w-md text-center">
        <CardContent className="pt-6">
          {state === "loading" && (
            <div className="space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Signing you in...</h2>
                <p className="mt-2 text-muted-foreground text-sm">
                  Verifying your email and creating your session.
                </p>
              </div>
            </div>
          )}

          {state === "success" && (
            <div className="space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">You&apos;re signed in!</h2>
                <p className="mt-2 text-muted-foreground text-sm">
                  Redirecting you to your dashboard...
                </p>
              </div>
            </div>
          )}

          {state === "error" && (
            <div className="space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Verification failed</h2>
                <p className="mt-2 text-muted-foreground text-sm">
                  The magic link may have expired or already been used.
                  Please request a new one.
                </p>
              </div>
              <Link href="/login">
                <Button className="w-full">Back to sign in</Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-white">
        <div className="container flex items-center justify-between py-4">
          <Link href="/" className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <span className="font-semibold text-lg">Insureview</span>
          </Link>
        </div>
      </header>
      <Suspense
        fallback={
          <div className="flex-1 flex items-center justify-center px-4 py-16 bg-slate-50">
            <Card className="w-full max-w-md text-center">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="mx-auto w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold">Verifying...</h2>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        }
      >
        <VerifyContent />
      </Suspense>
    </div>
  );
}
