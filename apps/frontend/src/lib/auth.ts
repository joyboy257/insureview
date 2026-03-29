import NextAuth from "next-auth";
import type { NextAuthOptions } from "next-auth";
import EmailProvider from "next-auth/providers/email";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { PrismaClient } from "@prisma/client";
import { sendMagicLinkEmail } from "@/lib/email";

const prisma = new PrismaClient();

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    EmailProvider({
      server: {
        host: process.env.EMAIL_SERVER_HOST,
        port: Number(process.env.EMAIL_SERVER_PORT || 587),
        auth: {
          user: process.env.EMAIL_SERVER_USER,
          pass: process.env.EMAIL_SERVER_PASS,
        },
      },
      from: process.env.EMAIL_FROM,
      sendVerificationRequest({ identifier, url }) {
        if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVER_USER) {
          console.log(`\n📧 Magic link for ${identifier}: ${url}\n`);
          return;
        }
        return sendMagicLinkEmail(identifier, url);
      },
    }),
    CredentialsProvider({
      name: "Demo Token",
      credentials: {
        token: { label: "Token", type: "text" },
      },
      async authorize(credentials) {
        if (!credentials?.token) return null;
        try {
          // Decode the JWT from our backend
          const secret = process.env.NEXTAUTH_SECRET ?? "dev-secret-minimum-32-chars-for-auth";
          const { default: jwtDecodeFn } = await import("jose");
          const { payload } = jwtDecodeFn(credentials.token, new TextEncoder().encode(secret));
          if (!payload.sub) return null;
          return { id: payload.sub, email: (payload as { email?: string }).email ?? null };
        } catch {
          return null;
        }
      },
    }),
  ],
  pages: {
    signIn: "/login",
    verifyRequest: "/verify",
    error: "/login",
  },
  session: { strategy: "jwt" },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      // If credentials token present, decode it
      const credToken = (token as { credToken?: string }).credToken;
      if (credToken) {
        try {
          const secret = process.env.NEXTAUTH_SECRET ?? "dev-secret-minimum-32-chars-for-auth";
          const { default: jwtDecodeFn } = await import("jose");
          const { payload } = jwtDecodeFn(credToken, new TextEncoder().encode(secret));
          token.id = payload.sub;
          (token as { email?: string }).email = (payload as { email?: string }).email;
        } catch {
          // ignore
        }
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as { id?: string }).id = token.id as string;
        session.user.email = (token as { email?: string }).email ?? session.user.email ?? null;
      }
      return session;
    },
    async redirect({ url, baseUrl }) {
      if (url.startsWith(baseUrl)) return url;
      return baseUrl + "/dashboard";
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};

export default NextAuth(authOptions);
