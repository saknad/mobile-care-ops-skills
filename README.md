# mobile-care-ops-skills

Agent skills for running the data side of mobile health units: syncing patient records from vans that work offline, handling sync failures, and keeping patient data out of logs and tickets.

## Skills

| Skill | What it does |
|---|---|
| `sync-error-triage` | Classifies a failed FHIR sync as retry, reauth, fix-record, conflict, or escalate, and returns one safe next step. |
| `phi-log-scrub` | Redacts patient identifiers from a sync log with a script before it is shared, keeping what troubleshooting needs. |

## Install

```bash
npx skills add https://github.com/<your-username>/mobile-care-ops-skills
```

Update installed copies with `npx skills update`.

## Planned

- `offline-queue-check`: pre-departure check that the van's record queue is backed up before leaving coverage.
- `clinic-handoff-summary`: end-of-day visit summary for the receiving clinic, with no patient identifiers.
