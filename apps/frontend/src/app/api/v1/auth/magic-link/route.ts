import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // authorize (callback from NextAuth) — verify the magic link token
  if (body.token) {
    const res = await fetch(`${backendUrl}/api/v1/auth/verify-magic-link?token=${encodeURIComponent(body.token)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    if (!res.ok) return NextResponse.json(data, { status: res.status });
    // Return user object that NextAuth expects
    return NextResponse.json({ id: data.id, email: data.email, name: data.full_name || data.email });
  }

  // New magic-link request — send email
  const res = await fetch(`${backendUrl}/api/v1/auth/magic-link?email=${encodeURIComponent(body.email)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
