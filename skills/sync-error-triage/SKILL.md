---
name: sync-error-triage
description: Use when a mobile unit's FHIR sync fails and the user shares the HTTP status, OperationOutcome, or error log. Classifies the failure as retry, reauth, fix-record, conflict, or escalate and returns one safe next step.
---

# Sync error triage

Read the HTTP status first, then the OperationOutcome issues if present. Pick exactly one verdict.

RETRY for 429, 502, 503, 504, timeouts, and dropped connections. Honor any Retry-After header; otherwise back off exponentially. A 500 gets one retry, then becomes ESCALATE.

REAUTH for 401. The backend token likely expired; request a new one and retry once. A 403 is a scope or permission problem, so it is ESCALATE, not REAUTH.

FIX-RECORD for 400, 404 on a referenced resource, and 422. Use the OperationOutcome issue expression to name the exact field and Bundle entry that failed.

CONFLICT for 409 and 412. The server has a newer version. Never overwrite it; fetch the current version and flag it for review.

If the request was a transaction Bundle, remember the whole Bundle was rolled back. After the fix, resubmit the entire Bundle, not just the failed entry.

Never include patient names, dates of birth, or identifiers in your answer. Refer to records by Bundle entry index only.

If the status or error details are missing, say what is missing instead of guessing.

Return exactly four lines:
Verdict: one of RETRY, REAUTH, FIX-RECORD, CONFLICT, ESCALATE
Reason: one sentence
Next step: one action
Log line: timestamp, unit ID, status code, verdict
