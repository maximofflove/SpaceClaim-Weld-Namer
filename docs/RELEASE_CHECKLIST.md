# Release Checklist

## Core creation

- [x] Root-part requirement retained.
- [x] Empty/mixed selection rejected.
- [x] Multiple Edge objects supported.
- [x] Existing weld groups not intentionally overwritten by normal Create.
- [x] Gap-aware, case-insensitive numbering retained.
- [x] `MAX_PAIR = 99999999` retained.

## Window lifecycle

- [x] UI created through host `BeginInvoke`.
- [x] Duplicate launch suppression retained.
- [x] Close/reopen behavior retained.

## Visualization

- [x] A = Secondary Selection.
- [x] B = red temporary Graphic.
- [x] Current pair / all groups / Auto Highlight use A/B colors.
- [x] Clear Highlight removes A and B visualization.
- [x] Orange QA problem overlay available.

## QA / repair

- [x] Validate All.
- [x] Problem-only filter and navigation.
- [x] Pair highlight and zoom.
- [x] CSV export.
- [x] Replace/Add/Remove A/B.
- [x] Create Missing A/B.
- [x] Conflict highlight.
- [x] Post-repair group verification.

## Packaging

- [x] Source header = v0.13.1.
- [x] Window titles = v0.13.1.
- [x] Log file = `%TEMP%\\SpaceClaim_Weld_Namer_v012.log`.
- [x] README / README_RU / CHANGELOG / RELEASE_NOTES updated.
- [x] Real validation distinguished from static checks.
- [x] GPL-3.0 license included.
- [x] Development logs and temporary reports excluded from repository root.
- [x] Screenshots from real v0.12 validation included.

## New workflows

- [x] Bolt Edge pairs and Face Meshing Face groups use independent sequences.
- [x] Auto / Current / All highlights follow selected purpose.
- [x] User confirmed both new creation modes and highlights work in SpaceClaim 2021 R1.
- [x] Weld QA / Repair is scoped to weld groups.

## GitHub release

Recommended metadata:

```text
Tag:    v0.13.1
Target: main
Title:  SpaceClaim Named Selection Namer v0.13.1
```
