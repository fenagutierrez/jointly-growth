# Loop: Austin Team Deep-Dive Research

## Task

Each iteration, pick **one** unresearched Austin team from the master spreadsheet and run the full deep-dive research process on it.

### Step 1 — Find the next qualifying team

```
gws sheets spreadsheets values get --params '{"spreadsheetId": "1T8taDH4WPC47R2YSlPdXavFlX6kvmvZamhy1NPBIQOA", "range": "medium_teams_texas!A:W"}'
```

Filter for rows where `metroArea` (col I) = "Austin", `website` (col K) is not empty, and `profile link` (col C) is empty. Pick the first match. Record the row number, team name, and website URL.

If no rows qualify, stop and report "No qualifying Austin teams remaining."

### Step 2 — Run the deep-dive

Follow `@00.companies/teams/process-documentation/team-deep-dive-research.md` from Phase 0 through Phase 5, using the team's `website` as the Anchor URL.

### Step 3 — Report

After Phase 5 completes, output a one-paragraph summary: team name, row processed, confirmed seat count, MRR potential, any flags, and confirmation that the Google Drive upload and spreadsheet link update succeeded.
