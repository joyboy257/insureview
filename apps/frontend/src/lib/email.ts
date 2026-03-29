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
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Insureview sign-in link</title>
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:Inter,Helvetica Neue,Helvetica,Arial,sans-serif;">
  <div style="max-width:480px;margin:40px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <!-- Header -->
    <div style="background:hsl(174,52%,32%);padding:24px 32px;">
      <h1 style="color:#ffffff;margin:0;font-size:20px;font-weight:700;letter-spacing:-0.3px;">Insureview</h1>
    </div>
    <!-- Body -->
    <div style="padding:32px;">
      <p style="font-size:15px;color:#334155;margin:0 0 16px;">Click the button below to sign in to your Insureview account.</p>
      <p style="font-size:15px;color:#334155;margin:0 0 24px;">This link expires in <strong>15 minutes</strong> and can only be used once.</p>
      <!-- CTA -->
      <div style="text-align:center;margin:24px 0;">
        <a href="${url}"
           style="display:inline-block;background:hsl(174,52%,32%);color:#ffffff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;">
          Sign in to Insureview
        </a>
      </div>
      <!-- Fallback link -->
      <p style="font-size:13px;color:#64748b;margin:0 0 4px;">Or copy and paste this link into your browser:</p>
      <p style="font-size:12px;color:#64748b;word-break:break-all;margin:0;"><a href="${url}" style="color:#64748b;">${url}</a></p>
      <!-- MAS disclaimer -->
      <div style="margin-top:28px;padding:12px 16px;background:hsl(48,92%,95%);border:1px solid hsl(48,92%,80%);border-radius:6px;">
        <p style="font-size:12px;color:hsl(35,90%,20%);margin:0;">
          <strong>Important:</strong> Insureview is an informational tool only.
          It is not regulated by MAS as a financial advisory service.
          Nothing on this site constitutes financial advice.
        </p>
      </div>
    </div>
    <!-- Footer -->
    <div style="padding:16px 32px;border-top:1px solid #e2e8f0;">
      <p style="font-size:12px;color:#94a3b8;margin:0;">
        You received this because you requested to sign in to Insureview.<br>
        If you didn't request this link, you can safely ignore this email.
      </p>
    </div>
  </div>
</body>
</html>`;

  // In dev, just log the URL to console
  if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVER_USER) {
    console.log(`\n📧 Magic link email for ${email}:\n   ${url}\n`);
    return;
  }

  await transporter.sendMail({
    from: process.env.EMAIL_FROM,
    to: email,
    subject: "Your Insureview sign-in link",
    html,
  });
}
