# Data Retention Policy

> **Insureview -- Singapore Insurance Portfolio Analysis Platform**
> Version: 1.0.0
> Last Updated: 28 March 2026
> Issued pursuant to the Personal Data Protection Act 2012 (PDPA) of Singapore

---

## 1. Overview

This Data Retention Policy describes how long Insureview retains each category of personal data, and the processes for secure deletion. All retention periods comply with Singapore PDPA requirements.

---

## 2. Data Categories and Retention Periods

| Data Category | Retention Period | Basis |
|---|---|---|
| Raw policy PDFs | Deleted within 24 hours of parsing completion | PDPA minimisation principle |
| Structured policy data (benefits, riders, exclusions) | Until user withdraws consent or deletes account | Service necessity |
| User account (email, name) | 12 months after last login or account deletion | Account recovery |
| Consent records | 7 years after consent withdrawal | PDPA audit compliance |
| Analysis results | Deleted with account; not retained separately | Service necessity |
| Session/authentication tokens | Duration of session only; JWT expires in 24 hours | Security |
| Server logs (IP, user-agent) | 90 days | Security monitoring |
| PDPA withdrawal records | 7 years | Legal compliance |

---

## 3. PDF Document Handling

### 3.1 Default Flow
All uploaded policy PDFs are deleted within 24 hours of parsing completion. This is an automated process that runs after the parsing pipeline confirms successful extraction.

### 3.2 Secure Vault Option
Users may opt into the Secure Vault feature. If opted in:
- PDFs are retained in encrypted S3 storage
- Vault data is retained until the user deletes their account or specifically removes vault documents
- A separate Vault Agreement and additional consent is required for the Secure Vault feature

### 3.3 Orphaned PDFs
A scheduled daily job checks for PDFs that have been in S3 for more than 24 hours without a corresponding parsing session record. These are automatically deleted regardless of vault status.

### 3.4 Failed Parsing
If parsing fails, the PDF is retained in S3 for 7 days to allow retry, then deleted automatically.

---

## 4. Deletion Procedures

### 4.1 User-Initiated Deletion
Users may delete all their data at any time via the Settings page. The deletion process:
1. All S3 objects (PDFs, including vault) are permanently deleted
2. All database records are deleted in dependency order (benefits, riders, exclusions, policies, consent records, analysis results)
3. User account is anonymised (email hash set to NULL, name set to NULL, magic_link_token cleared)
4. Consent withdrawal is recorded with timestamp
5. User receives email confirmation when deletion is complete

### 4.2 Anonymisation vs. Deletion
The account record is anonymised rather than dropped entirely because:
- Consent records must be retained for 7 years under PDPA audit requirements
- Anonymised records retain the withdrawal timestamp and consent hash for audit purposes
- No personally identifiable information remains in anonymised records

### 4.3 Scheduled Deletion Jobs
- Daily at 02:00 SGT: Delete PDFs in S3 older than 24 hours with no associated parsing session
- Monthly: Identify and anonymise accounts inactive for more than 12 months
- Annually: Delete anonymised consent records older than 7 years

---

## 5. Secure Destruction

### 5.1 S3 Deletion
Objects deleted from S3 are removed using S3's permanent deletion (not versioning-recoverable paths). For the Secure Vault, S3 Intelligent-Tiering or Glacier is not used; standard storage only.

### 5.2 Database Deletion
Database records are deleted using `DELETE` SQL statements with `ON DELETE CASCADE` for dependent tables. No soft-delete mechanism is used for policy data.

### 5.3 Encryption Keys
When a user deletes their account, the encryption key material used specifically for their vault documents (if applicable) is flagged for secure destruction. The Fernet encryption key is not reused across users in normal operation.

---

## 6. Data Export (Portability)

Users may export all their structured policy data at any time via the Settings page. The export is provided as a JSON file containing:
- All policy records (without raw PDF data)
- All analysis results
- All consent records (for transparency)

Export requests are fulfilled within 24 hours.

---

## 7. Compliance

### 7.1 PDPA Compliance
This policy is designed to comply with:
- PDPA Section 25: Protection of personal data
- PDPA Section 22: Retention limitation
- PDPA Section 24: Access and correction rights

### 7.2 Audit Trail
All consent records, deletion requests, and export requests are logged with timestamps for PDPA audit purposes.

---

## 8. Contact

For questions about data retention, contact: privacy@insureview.com
