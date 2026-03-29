# Privacy Policy

> **Insureview -- Singapore Insurance Portfolio Analysis Platform**
> Version: 1.0.0
> Last Updated: 28 March 2026
> This Privacy Policy is issued pursuant to the Personal Data Protection Act 2012 (PDPA) of Singapore.

---

## 1. Who We Are

Insureview ("we", "our", or "us") operates a web platform that allows Singapore residents to upload their personal insurance policy documents for analysis. We process these documents to extract structured information about coverage, benefits, exclusions, and riders.

We are not a licensed financial adviser. We provide an informational analysis service only.

---

## 2. What Personal Data We Collect

We collect the following categories of personal data:

### 2.1 Account Information
- Email address (for authentication via magic link)
- Full name (optional, provided by you)

### 2.2 Insurance Policy Documents
- Uploaded PDF copies of insurance policy documents
- These documents may contain: your name, policy numbers, NRIC or FIN numbers (if present in policy documents), benefit amounts, coverage details, and beneficiary information

### 2.3 Derived Data
- Structured policy data extracted from uploaded PDFs (benefits, exclusions, riders, coverage amounts)
- Plain English summaries generated from your policies
- Portfolio analysis results (gaps, overlaps, conflicts)

### 2.4 Technical Data
- IP address
- Browser user agent
- Timestamps of all actions
- Consent records with versioned text hashes

---

## 3. How We Use Your Personal Data

We use your personal data for the following purposes only:

1. **Policy Analysis**: To parse your uploaded insurance PDFs and provide coverage gap, overlap, and conflict analysis
2. **Account Management**: To authenticate you and manage your session
3. **PDPA Compliance Records**: To maintain immutable consent records as required by Singapore law
4. **Service Improvement**: Aggregate, anonymised statistics on parsing accuracy (no individual policy data)

We do NOT:
- Sell your personal data to any party
- Share your policy documents with insurers or third parties
- Use your data for marketing or advertising
- Use your data to provide financial advice

---

## 4. Disclosure of Personal Data

We do not disclose your personal data to any third parties, except:

1. **Anthropic (Claude API)**: Your policy PDFs are processed by Anthropic's Claude Opus 4 model. We have a Data Processing Agreement with Anthropic covering the processing of personal data in policy documents. See: anthropic.com/privacy

2. **OpenAI (GPT-4o fallback)**: In limited cases, your policy text may be processed by OpenAI's GPT-4o as a fallback. OpenAI is used as a sub-processor under a Data Processing Agreement.

3. **AWS / S3**: Your PDFs are temporarily stored in encrypted S3-compatible storage during the parsing process.

4. **Legal Requirements**: We may disclose your data if required by law, court order, or Singapore government authority.

---

## 5. How We Protect Your Data

### 5.1 PDF Deletion
Your original policy PDFs are deleted immediately after parsing is complete, unless you explicitly opt into the Secure Vault feature. Only the structured, extracted policy data is retained.

### 5.2 Encryption
Sensitive fields within structured policy data (such as policy numbers) are encrypted at rest using Fernet symmetric encryption.

### 5.3 Access Controls
Access to your data is restricted to you. Our systems use row-level isolation per user account. No Insureview staff can access your individual policy data.

### 5.4 Consent Immutability
Consent records are stored with a SHA-256 hash of the exact consent text agreed to, creating an immutable audit trail.

---

## 6. PDPA Rights You Have

Under the PDPA, you have the following rights:

### 6.1 Access
You may request a copy of all your personal data held by us at any time. To exercise this right, contact us at privacy@insureview.com or use the Settings page in your account.

### 6.2 Correction
You may request correction of inaccurate personal data.

### 6.3 Withdrawal of Consent
You may withdraw consent for data collection and processing at any time. Withdrawal triggers the data deletion process described in Section 7.

### 6.4 Data Portability
You may export all your structured policy data as a JSON file at any time via the Settings page.

### 6.5 Data Deletion
You may request complete deletion of all your personal data at any time. See Section 7.

---

## 7. Data Retention and Deletion

### 7.1 Policy PDFs
Raw PDFs are deleted within 24 hours of parsing completion (immediately after if not opted into Secure Vault).

### 7.2 Structured Policy Data
Retained until you withdraw consent or request deletion.

### 7.3 Account Data
Retained for 12 months after your last login, or until deletion is requested, whichever is earlier.

### 7.4 Consent Records
Retained for 7 years after withdrawal of consent, as required for PDPA audit purposes.

### 7.5 Data Deletion Process
Upon valid deletion request:
1. All raw PDFs are deleted from S3
2. All structured policy data is deleted from PostgreSQL (including benefits, riders, exclusions)
3. All analysis results are deleted
4. Your account is anonymised (email hash zeroed, name removed)
5. Consent records are retained in anonymised form for the statutory period

---

## 8. International Data Transfers

Your policy documents may be processed by Anthropic (US) and OpenAI (US) as described in Section 4. These transfers occur under Standard Contractual Clauses or equivalent mechanisms provided by those providers.

---

## 9. Cookies

We use minimal cookies:
- `next-auth.session-token`: Essential authentication cookie, expires when you sign out
- No analytics cookies
- No advertising cookies

---

## 10. Changes to This Policy

If we update this Privacy Policy:
- We will notify you by email if you have an active account
- Updated policy will be available at insureview.com/privacy
- If changes require re-consent, you will be prompted to agree before continuing to use the service

---

## 11. Contact Us

For any questions about this Privacy Policy or to exercise your PDPA rights:

**Data Protection Officer**
Insureview
Email: privacy@insureview.com

If you are not satisfied with our response, you may contact the Personal Data Protection Commission (PDPC) of Singapore: pdpc.gov.sg

---

## 12. Governing Law

This Privacy Policy is governed by and construed in accordance with the laws of the Republic of Singapore.
