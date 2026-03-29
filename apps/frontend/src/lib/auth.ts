import NextAuth from "next-auth";
import type { NextAuthConfig } from "next-auth";
import EmailProvider from "next-auth/providers/email";

export const authConfig: NextAuthConfig = {
  providers: [
    EmailProvider({
      server: {
        host: process.env.EMAIL_SERVER_HOST,
        port: Number(process.env.EMAIL_SERVER_PORT),
        auth: {
          user: process.env.EMAIL_SERVER_USER,
          pass: process.env.EMAIL_SERVER_PASS,
        },
      },
      from: process.env.EMAIL_FROM,
    }),
  ],
  pages: {
    signIn: "/login",
    verifyRequest: "/verify",
  },
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnApp = nextUrl.pathname.startsWith("/dashboard") ||
        nextUrl.pathname.startsWith("/upload") ||
        nextUrl.pathname.startsWith("/settings") ||
        nextUrl.pathname.startsWith("/policies");
      if (isOnApp) {
        return isLoggedIn;
      }
      return true;
    },
  },
  session: { strategy: "jwt" },
};

export const { handlers } = NextAuth(authConfig);
