# Validation Matrix — v0.13.1

Target: SpaceClaim 2021 R1, Script API V19, IronPython 2.7.

## User confirmed in SpaceClaim

| Workflow | Evidence |
| --- | --- |
| Bolt Pair creation from Edges (`f…a/f…b`) | User reported it works in v0.13.0 |
| Face Meshing creation from Faces (`fm…`) | User reported it works in v0.13.0 |
| Bolt Pair highlight | User reported v0.13.1 works |
| Face Meshing highlight | User reported v0.13.1 works |
| Empty-root fallback and `w1a/w1b` creation | User log dated 2026-09-24 |

The earlier real-model weld checks below belong to v0.12.0. Specific boundary cases such as the maximum `f` / `fm` number and other SpaceClaim versions were not run on the target installation. The v0.13.1 source parsed and the name routing / highlight selection were checked with isolated mocks.

# Historical weld validation — v0.12.0

Target environment:

- ANSYS SpaceClaim 2021 R1
- Script API V19
- built-in IronPython 2.7

This document separates **real SpaceClaim validation** from developer/static checks.

## Real target installation — confirmed

| Function | Status |
|---|---|
| Modeless WinForms launched through SpaceClaim UI thread | PASS |
| Window close -> script Run -> reopen | PASS |
| Duplicate-window suppression | PASS |
| `NamedSelection.GetGroups(root)` | PASS |
| Sequential `wNa / wNb` creation | PASS |
| Gap-aware and case-insensitive numbering | PASS |
| Multiple selected Edge objects in one Named Selection | PASS |
| Normal Create does not intentionally overwrite existing group | PASS |
| A-side Secondary Selection visualization | PASS |
| B-side red `Display.Graphic` visualization | PASS |
| Highlight Current Pair | PASS |
| Highlight All Weld Groups | PASS |
| Clear Highlight clears A/B visualization | PASS |
| QA / Repair Manager opens and scans weld groups | PASS |
| QA table and selected-pair navigation | PASS |
| Orange QA problem visualization | PASS |
| Repair workflow on the tested Edge-based model | PASS — user reported successful operation |
| Global A/B highlight on 104 groups / 346 geometry items | PASS — observed in validation session |

## API diagnostics confirmed on the target installation

The reflection probes confirmed these relevant V19 capabilities before implementation:

- `CurvePrimitive.Create(ITrimmedCurve)`;
- `Graphic.Create(...)` and `GraphicStyle.LineColor` / `LineWidth`;
- writable `Window.Rendering` and `Window.RefreshRendering()`;
- `NamedSelection.Replace(String, ISelection, ISelection, ICommandInfo)`;
- `NamedSelection.Delete(String[])`;
- `Group.Members` readable but not writable.

A real test also established that reading `Window.Rendering` while the custom-rendering slot is empty can raise a null-reference exception, while direct assignment plus `RefreshRendering()` works. The stable code therefore avoids that getter.

## Developer/static checks

- Python source parses successfully with CPython's parser for syntax compatible with the file.
- Stable package contains no development logs or temporary files.
- `MAX_PAIR` remains `99999999`.
- normal `create_next()` logic retains the established create/rename path.
- README, version, changelog and UI titles are synchronized to v0.12.0.

## Not claimed as real-validated in v0.12.0

| Function | Status |
|---|---|
| Full Faces workflow including repair | Implemented, not independently confirmed in the recorded target test |
| SpaceClaim versions other than 2021 R1 | Not validated |
| Script publication as a toolbar Tool | Not validated |
| Keyboard shortcut / Ctrl+W | Not implemented |

## QA interpretation

The QA Manager is a **model-preparation screening tool**. A `CHECK` or `ERROR` flag identifies suspicious Named Selection structure or geometry relationships. It is not an engineering acceptance criterion for weld strength or weld quality.

Object-count mismatch is informational because topological partitioning may differ between otherwise corresponding weld sides. The 10% length/area tolerance is a configurable screening threshold, not a code requirement.
