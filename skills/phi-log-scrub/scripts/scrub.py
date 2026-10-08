#!/usr/bin/env python3
"""Redact patient identifiers from a sync log before it is shared.

Usage:
  python3 scrub.py <input-file> [output-file]

Reads plain-text or FHIR JSON logs. Replaces patient identifiers with
numbered placeholders (the same value always gets the same placeholder)
and keeps what troubleshooting needs: status codes, timestamps, unit IDs,
resource types, and Bundle entry numbers. Prints a redaction summary.
"""
import re
import sys
from collections import defaultdict

placeholders = {}
counts = defaultdict(int)


def token(kind, value):
    key = (kind, value.strip().lower())
    if key not in placeholders:
        counts[kind] += 1
        placeholders[key] = f"[{kind}-{counts[kind]}]"
    return placeholders[key]


def sub_field(text, fields, kind):
    """Redact the value of JSON fields like "family": "Smith"."""
    pattern = r'("(?:' + "|".join(fields) + r')"\s*:\s*)("([^"]*)"|\[[^\]]*\])'

    def repl(m):
        raw = m.group(2)
        if raw.startswith("["):
            items = re.findall(r'"([^"]*)"', raw)
            return m.group(1) + "[" + ", ".join(f'"{token(kind, i)}"' for i in items) + "]"
        return m.group(1) + f'"{token(kind, m.group(3))}"'

    return re.sub(pattern, repl, text)


def scrub(text):
    # FHIR JSON fields
    text = sub_field(text, ["family", "given"], "NAME")
    text = sub_field(text, ["birthDate"], "DOB")
    text = sub_field(text, ["line", "postalCode"], "ADDRESS")
    text = re.sub(r'("system"\s*:\s*"[^"]*(?:mrn|ssn|patient-id)[^"]*"\s*,\s*"value"\s*:\s*")([^"]+)(")',
                  lambda m: m.group(1) + token("MRN", m.group(2)) + m.group(3), text, flags=re.I)
    # Labeled plain-text fields: "Patient: Jane Doe", "DOB 01/02/1980", "MRN 12345"
    # Label is case-insensitive; the name itself must be Capitalized words separated by one space or ", "
    text = re.sub(r'\b((?i:patient(?: name)?|name))(\s*[:=]\s*)([A-Z][a-z]+(?:(?:, | )[A-Z][a-z]+)+)',
                  lambda m: m.group(1) + m.group(2) + token("NAME", m.group(3)), text)
    text = re.sub(r'\b(dob|date of birth|birth ?date)(\s*[:=]?\s*)(\d{1,4}[-/]\d{1,2}[-/]\d{1,4})',
                  lambda m: m.group(1) + m.group(2) + token("DOB", m.group(3)), text, flags=re.I)
    text = re.sub(r'\b(mrn|medical record(?: number)?)(\s*[:=#]?\s*)([A-Z0-9-]{4,})',
                  lambda m: m.group(1) + m.group(2) + token("MRN", m.group(3)), text, flags=re.I)
    # Patterns that are identifiers wherever they appear
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', lambda m: token("SSN", m.group()), text)
    text = re.sub(r'(?<!\d)(?:\+1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)',
                  lambda m: token("PHONE", m.group()), text)
    text = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', lambda m: token("EMAIL", m.group()), text)
    return text


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 scrub.py <input-file> [output-file]")
    with open(sys.argv[1], encoding="utf-8") as f:
        result = scrub(f.read())
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(result)
    else:
        print(result)
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "nothing found"
    print(f"\nRedacted -> {summary}", file=sys.stderr)


if __name__ == "__main__":
    main()
