# Validation Matrix — v0.15.8

Target: SpaceClaim 2021 R1, Script API V19, IronPython 2.7.


## v0.15.8 build checks

The v0.15.8 package was checked outside SpaceClaim with `python -m unittest discover -s tests -v`: **23/23 tests passed**. This includes the 16 Bolt geometry/mutation-guard tests and 7 Contact repair static/routing checks.

| Check | Result |
| --- | --- |
| Contact manager routes to `ctkt` validator/highlighter | PASS (static) |
| Contact repair enforces Faces | PASS (static) |
| Contact Add/Remove uses shared Replace + verification path | PASS (static) |
| Contact missing-side creation uses `ctkt` prefix | PASS (static) |
| Weld repair routing remains present | PASS (static regression) |
| SpaceClaim 2021 R1 / API V19 runtime test of Contact QA / Repair workflow | PASS — user confirmed v0.15.8 works |
| Contact `Add to B` mutation + post-operation revalidation | PASS — captured on `ctkt37b`, updated to 8 Faces |

## v0.15.8 real target validation

On **2026-10-02**, the v0.15.8 Contact workflow was tested by the user in the target **SpaceClaim 2021 R1 / Script API V19** environment. The supplied captures confirm:

- the main Contact mode exposes the active **Contact Named Selection QA / Repair Manager** button;
- the Contact manager reads real `ctktNa/ctktNb` groups as Faces-only;
- QA records, area mismatch screening, navigation and repair controls are populated;
- **Add to B** successfully updated `ctkt37b` to **8 Faces**;
- the tool immediately re-read and revalidated `ctkt37` after the mutation.

The user reported the Contact repair feature works. Together with the shared `NamedSelection.Replace(...)` mutation path and the 23/23 regression checks, this target-host confirmation is the basis for promoting **v0.15.8 to stable**.

## v0.14.1 isolated checks

16 tests passed in `tests/test_bolt_geometry.py`: aligned and offset centres, arbitrary 3D directions, reversed normals, tolerance thresholds, coincident stations, incomplete circles, missing planar faces, multi-edge scoping, differing plate normals, first-side PENDING, creation into gaps with an existing B, audit continuation and unreadable groups. The actual `create_next` mutation path was checked to stop before NamedSelection.Create on failed angles. GUI control bounds were checked for overlap. Geometry adapters use mocks; real API V19 circle/face access and overlays remain unverified.

Run: `python3 -m unittest discover -s tests`

## v0.14.0 isolated checks

Source syntax, selected-geometry membership, unreadable-group reporting, multi-owner labels, label selection filtering, toggling names and preserving the red overlay passed isolated mocks. The stroke glyphs were rendered for visual inspection. New UI geometry was checked for control overlap. The exact target rendering and lookup have not been tested in SpaceClaim.

## User confirmed in SpaceClaim

| Workflow | Evidence |
| --- | --- |
| Bolt Pair creation from Edges (`f…a/f…b`) | User reported it works in v0.13.0 |
| Face Meshing creation from Faces (`fm…`) | User reported it works in v0.13.0 |
| Bolt Pair highlight | User reported v0.13.1 works |
| Face Meshing highlight | User reported v0.13.1 works |
| Empty-root fallback and `w1a/w1b` creation | User log dated 2026-09-24 |

The earlier real-model weld checks below belong to v0.12.0. Specific boundary cases such as the maximum `f` / `fm` number and other SpaceClaim versions were not run on the target installation. The v0.13.1 source parsed and the name routing / highlight selection were checked with isolated mocks.

The v0.13.2 Face Meshing duplicate check was validated with isolated mocks for no overlap, partial overlap, multiple matching groups, unreadable groups and no mutation when blocked. It awaits a run in SpaceClaim 2021 R1.

The v0.13.3 audit was validated with isolated mocks for duplicate faces across groups, unique faces, repeated selection within one group and unreadable groups. The audit and its blue highlight await a run in SpaceClaim 2021 R1.

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
