# Sample Audit Findings for Testing

Use these inputs to demonstrate the AI Auditor during interviews or demos.

---

## ✅ High-Confidence Matches (Distance < 1.0)

### 1. Weak Password Policy
**Expected Match**: `weak_password` | Distance: 0.84

```
User accounts allow passwords like 'password123' and 'admin'. No complexity requirements enforced. Users can set their own passwords without any validation.
```

**Expected Controls**:
- ISO 27001: A.9.4.3
- SOC 2: CC6.1
- NIST CSF: PR.AC-7

---

### 2. Backup Testing Failure
**Expected Match**: `backups_not_tested` | Distance: 0.97

```
Database backups run nightly but haven't been tested in 14 months. Last restoration test failed due to corrupted backup files. Backups are stored on the same network as production systems. No offsite backup copies exist.
```

**Expected Controls**:
- ISO 27001: A.12.3.1
- SOC 2: CC9.1
- HIPAA: 164.308(a)(7)(ii)(D)

---

### 3. Shared Admin Credentials
**Expected Match**: `shared_credentials` | Distance: 0.40

```
During the access review, we found that the DevOps team is using shared admin credentials (username: sysadmin, password: Admin123) to access production servers. The password has not been changed in 18 months. Additionally, there is no multi-factor authentication enabled on these privileged accounts. SSH access logs show 47 different IP addresses using this single account over the past 3 months.
```

**Expected Controls**:
- ISO 27001: A.9.2.4
- SOC 2: CC6.1
- HIPAA: 164.308(a)(3)

---

## ✅ Good Matches (Distance 1.0-1.3)

### 4. Missing MFA
**Expected Match**: `no_mfa` | Distance: 1.12

```
VPN access requires only username and password. Multi-factor authentication is not enabled. Remote employees can access internal systems from any device without additional verification.
```

---

### 5. Unencrypted Data
**Expected Match**: `missing_encryption_transit` | Distance: 1.15

```
Customer credit card data is stored in a MySQL database without encryption. Files containing Social Security Numbers are saved to shared network drives in Excel format with no password protection.
```

---

### 6. Outdated Software
**Expected Match**: `no_patch_mgmt` | Distance: 1.19

```
Windows Server 2012 hosts are 8 months behind on security patches. Critical vulnerabilities CVE-2023-1234 remain unpatched. IT team manually checks for updates quarterly but deployments are delayed due to change management approval backlogs.
```

---

### 7. Vendor Risk
**Expected Match**: `vendor_no_assessment` | Distance: 1.28

```
Marketing team uses a third-party email platform (MailChimpPro) to send customer newsletters containing email addresses and purchase history. No vendor security assessment was performed before onboarding. The contract has no data breach notification clause or right-to-audit provision.
```

---

## 🧪 Edge Cases

### 8. Multiple Risk Patterns (Tests Priority)
**Expected Match**: `excessive_permissions` | Distance: 1.07

```
12 employees have domain admin rights but only perform standard office tasks like creating PowerPoint presentations and managing calendars. Access was granted 3 years ago when they were in different roles.
```

---

### 9. Physical Security
**Expected Match**: `unlocked_workstations` | Distance: 1.35

```
Office server room door uses a 4-digit code (1234) that has been unchanged for 2 years. The code is written on a sticky note on the door frame. No entry/exit logs are maintained. Cleaning staff have 24/7 access to the room.
```

---

### 10. Cloud Misconfiguration
**Expected Match**: `public_cloud_misconfiguration` | Distance: ~1.2

```
AWS S3 bucket containing employee PII (names, addresses, SSNs) is publicly accessible on the internet. Bucket policy allows "s3:GetObject" for Principal: "*". Files were discoverable via Google search.
```

---

## 🎯 Multi-Risk Scenarios (Advanced)

### 11. Complex Finding (Multiple Controls)
```
Third-party SaaS vendor (SalesWidget Inc) processes customer payment data but has not undergone SOC 2 audit. Contract signed in 2020 has no termination clause, no insurance requirements, and no incident notification SLA. Vendor credentials are shared among 5 sales team members. API keys are hardcoded in the CRM integration scripts stored in public GitHub repository.
```

**Expected to trigger**:
- `vendor_no_assessment`
- `shared_credentials`
- `api_keys_hardcoded`

---

### 12. Incident Response Gap
```
Security Operations Center detected ransomware on file server but notification to Legal and PR teams took 8 days. No incident response playbook exists. Forensics investigation was delayed because logs were overwritten (30-day retention). Affected customers were not notified within GDPR's 72-hour requirement.
```

**Expected to trigger**:
- `no_incident_plan`
- `incident_not_reported`
- `log_retention_short`

---

## 📊 Performance Benchmarks

### Expected Results Summary

| Scenario | Pattern | Distance | Match? |
|----------|---------|----------|--------|
| Weak Password | `weak_password` | 0.84 | ✅ Yes |
| Backup Failure | `backups_not_tested` | 0.97 | ✅ Yes |
| Shared Creds | `shared_credentials` | 0.40 | ✅ Yes |
| No MFA | `no_mfa` | 1.12 | ✅ Yes |
| Unencrypted | `missing_encryption_transit` | 1.15 | ✅ Yes |
| Patches | `no_patch_mgmt` | 1.19 | ✅ Yes |
| Vendor | `vendor_no_assessment` | 1.28 | ✅ Yes |
| Admin Rights | `excessive_permissions` | 1.07 | ✅ Yes |

**Success Rate**: 8/8 (100%)
**Average Distance**: 1.00

---

## 💡 Demo Script

### For Interviews or Presentations

1. **Start with a winner**: Use "Weak Password" (0.84 distance) to show perfect match
2. **Show the warning**: Test with something NOT in database to demonstrate fallback mode
3. **Highlight multi-framework**: Use "Backup Failure" to show all 4 tabs (ISO/SOC2/HIPAA/NIST)
4. **Export demo**: Download CSV to show deliverable format
5. **Upload policy**: (Optional) Upload a sample PDF to show RAG policy integration

---

## 🚫 What NOT to Test With

### Bad Inputs (Will Fail or Give Poor Results)

❌ **Too Generic**:
```
"Security is bad"
"We need better controls"
"Compliance issues found"
```

❌ **Non-GRC Topics**:
```
"The coffee machine is broken"
"Sales team missed Q3 targets"
"Office wifi is slow"
```

❌ **Already Remediated**:
```
"MFA was enabled last month and all users enrolled"
"Backups are tested weekly and stored offsite in AWS Glacier"
```

---

## ✅ Best Practices for Testing

1. **Be Specific**: Include technical details (server names, vulnerability IDs, user counts)
2. **Use Audit Language**: "During the review...", "We observed...", "Testing revealed..."
3. **Include Evidence**: Mention logs, interviews, documentation reviewed
4. **Focus on Gaps**: Describe what's MISSING or BROKEN, not what's working

---

**Pro Tip**: Keep these samples handy for live demos. Copy-paste directly into the app to impress recruiters! 🎯
