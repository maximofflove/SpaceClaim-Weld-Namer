# Changelog

## v0.13.1 — 2026-09-25

- Bolt pairs `fNa/fNb` can be highlighted: A via blue Secondary Selection and B via a red temporary overlay.
- Face Meshing groups `fmN` can be highlighted blue individually or all at once.
- Auto Highlight follows the selected purpose; switching purpose clears the previous highlight.
- User confirmed Bolt Pair, Mechanical Face Meshing and their highlights work in SpaceClaim 2021 R1.

## v0.13.0 — 2026-09-25

- Added separate name sequences for Bolt Pair (Edges, `f1a/f1b` to `f999999a/f999999b`) and Mechanical Face Meshing (Faces, `fm1` to `fm999999999`).
- Weld naming, visualization and QA remain available.

## v0.12.1 — 2026-09-24

- Added root-part group enumeration fallback for an empty document, where the V19 scripting `GetGroups(root)` raised a null reference.
- The user's log confirmed the fallback and subsequent creation of `w1a/w1b`.


## v0.12.0 — Stable — 2026-09-16

Promoted to stable after successful validation on the real SpaceClaim 2021 R1 / API V19 installation.

Added since v0.10.0:

- independent A/B visualization:
  - A via Secondary Selection;
  - B via red temporary `Display.Graphic`;
- combined overlay state and reliable clear behavior;
- **Named Selection QA Manager**;
- validation of missing/empty groups, geometry types, reuse/conflicts, sequence gaps and A/B metric mismatch;
- orange **Highlight Problems**;
- **Show Problems Only**;
- **Previous / Next Problem** navigation;
- **Highlight Selected Pair** and **Zoom Selected Pair**;
- QA CSV export;
- controlled **Repair Manager**:
  - Replace A / B;
  - Add to A / B;
  - Remove from A / B;
  - Create Missing A / B;
  - Highlight Conflict;
- post-repair geometry verification and automatic revalidation.

Confirmed V19 API behavior used by this release:

- `Display.CurvePrimitive.Create(ITrimmedCurve)`;
- `GraphicStyle.LineColor` / `LineWidth`;
- writable `Window.Rendering` plus `RefreshRendering()`;
- `NamedSelection.Replace(name, primary, secondary, ...)` for existing group contents;
- `Group.Members` is read-only.

Real target validation included a large Edge-based model; a global highlight processed 104 weld groups / 346 geometry items during the recorded session.

## v0.11 — QA Manager Test

- introduced tabular weld-pair QA;
- orange problem highlighting;
- problem navigation and CSV export;
- retained A-blue / B-red visualization.

## v0.10.0 — Stable — 2026-09-11

- Auto highlight current pair after Create;
- Highlight Current Pair;
- Highlight All Weld Groups;
- current-pair calculation based on the first free sequential name;
- modeless window reopen/duplicate suppression retained;
- Secondary Selection visualization validated.

## v0.9 — Stable

- promoted Secondary Selection highlighting to the stable baseline.

## v0.8 — Highlight Test

- replaced ineffective per-edge CAD color visualization with Secondary Selection.

## v0.7 — Color Test

- experimental color-based visualization; abandoned because it did not provide the required per-edge visual result.

## v0.6 — Reopen Fix

- fixed stale window lock after close and duplicate launch behavior.

## v0.5 — Validated Creation Baseline

Established the creation chain retained by later versions:

```text
Selection.GetActive()
NamedSelection.GetGroups(root)
NamedSelection.Create(selection, Selection.Empty())
NamedSelection.Rename(temporary_name, target)
```
