---
name: phi-log-scrub
description: Use before a mobile unit's sync log or FHIR error is shared in a ticket, chat, or email. Runs a redaction script that replaces patient identifiers with placeholders while keeping status codes, timestamps, and unit IDs.
---

# PHI log scrub

Never repeat the original log in your answer. Only the scrubbed version may appear.

Save the log the user gave you to a temporary file, then run:
python3 scripts/scrub.py <temp-file>

The script replaces names, birth dates, MRNs, SSNs, phone numbers, emails, and addresses with numbered placeholders such as [NAME-1]. The same value always gets the same placeholder, so the log still makes sense.

After the script runs, read the output once more for identifiers the patterns can miss, such as a name written in free text without a "Patient:" label. Replace any you find with the next placeholder number and say what you changed.

Do not remove HTTP status codes, timestamps, unit IDs, resource types, or Bundle entry numbers. Troubleshooting depends on them.

Delete the temporary file when done.

Return the scrubbed log, then one line listing what was redacted.
