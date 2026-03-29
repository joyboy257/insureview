import nodemailer from "nodemailer";

const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_SERVER_HOST,
  port: Number(process.env.EMAIL_SERVER_PORT || 587),
  auth: {
    user: process.env.EMAIL_SERVER_USER,
    pass: process.env.EMAIL_SERVER_PASS,
  },
});

export async function sendMagicLinkEmail(email: string, url: string) {
  // In dev, just log the URL to console
  if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVER_USER) {
    console.log(`\n📧 Magic link for ${email}: ${url}\n`);
    return;
  }

  await transporter.sendMail({
    from: process.env.EMAIL_FROM,
    to: email,
    subject: "Your Insureview sign-in link",
    html: `
      <p>Click the link below to sign in to Insureview:</p>
      <a href="${url}">${url}</a>
      <p>This link expires in 15 minutes.</p>
    `,
  });
}
