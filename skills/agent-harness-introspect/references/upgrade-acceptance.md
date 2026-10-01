# Upgrade acceptance

Use this branch for requested upgrades and monthly evolution runs.

1. Inspect Git status, remote and SHA; fetch and fast-forward only. Preserve unrelated changes in place and use an isolated checkout when needed. Create the requested baseline archive before changes.
2. Run the configuration semantic gate before runtime synchronization. Measure prompt tokens using the same resolved CLI and working directory before and after; record measurement time and scope. CLI probes do not measure the active Desktop conversation or billed usage.
3. Scout first-party releases, standards and papers. For each candidate record the local gap, expected net benefit, minimal experiment, acceptance metrics, compatibility, license, rollback and adopt/defer/reject decision. Popularity is not an activation criterion.
4. Audit automation identities and contracts through non-secret metadata. Distinguish static contract checks from observed scheduler health, execution cost and last-success evidence. Preserve the live scheduler definition; repository documentation describes behavior rather than duplicating schedules or private prompts.
5. Exercise memory failure paths with synthetic fixtures: unavailable, locked or corrupt index; inaccessible source root; short Unicode query; encoding error; output budget. Read-only Markdown must survive index failure. Report bounded scans as potentially incomplete.
6. Apply targeted, backed-up changes. Use the app automation API for requested automation mutations and verify readback. Preserve runtime-specific patches; review third-party diffs before importing them.
7. Run relevant tests and one end-to-end flow. Browser changes require a real browser check and cleanup of task-owned resources. Inspect every rendered page of a visual report.
8. Publish only task-owned, secret-checked files within the user's authorization, verify remote refs, and record unresolved gates honestly. Keep local receipts and private backups outside Git.
