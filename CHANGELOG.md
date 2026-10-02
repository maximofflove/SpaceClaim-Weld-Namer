# v0.15.8 — Stable — Contact pair repair support

- Enabled QA / Repair Manager for `Contact pair (ctkt)`.
- Added `Replace A/B`, `Add to A/B`, `Remove from A/B`, and `Create Missing A/B` for `ctktNa/ctktNb`.
- Contact repair is Face-only and reuses the verified `NamedSelection.Replace(...)` workflow.
- Added contact-pair QA records, face-area screening, duplicate/reuse checks, contact-aware highlighting/zoom, conflict highlight and Contact CSV export.
- Weld repair behavior remains unchanged.
- Added detailed English/Russian User Guide documentation for all visible controls.
- Regression checks: 23/23 passed outside SpaceClaim.
- Runtime validation completed in SpaceClaim 2021 R1 / API V19; the user confirmed Contact QA / Repair works. The captured validation session shows `Add to B` updating `ctkt37b` to 8 Faces followed by automatic revalidation.
- Promoted to stable after target-host confirmation.

# v0.15.7 — Colors by group purpose

Weld pairs w#a/w#b: A uses native blue highlight, B uses red graphics.
Face Meshing fm#: native blue highlight.
Contact pairs ctkt#a/ctkt#b: muted blue RGB 110/150/177 and sand RGB 190/166/120, using the existing v0.15.6 fill.
Bolt pairs also use their original blue/red colors.
Label size control retained. Legends updated.

Validated syntax and verified the contact and Face Meshing rendering functions are unchanged from v0.15.6. SpaceClaim runtime is not available in this environment.

# v0.15.6 — Contact A/B display consistency

Contact pairs now render BOTH sides using the same temporary face mesh graphics, replacing native secondary selection for contact A. A: muted blue RGB 110/150/177. B: sand RGB 190/166/120. Both use depth testing and two-sided fill. B is added before A in the composite. Clear Highlight removes both via the existing overlay lifecycle. Other pair modes are unchanged.

The update addresses mixed native-selection/custom-overlay rendering. Exact coincident faces can still compete for depth; physically obscured faces may remain hidden. Visual confirmation in SpaceClaim is required. Label size retained.

# v0.15.5 — Blue A / purple B

Side B overlay color changed to purple RGB (160, 80, 220). Side A retains native blue secondary selection. UI color legends updated. Existing face fill and label sizing are retained. Internal legacy overlay keys are preserved for compatibility.

# v0.15.4 — V19 face fill from confirmed API signatures

User diagnostics confirmed DesignFaceGeneral occurrence wrappers, Master.Shape as Modeler.Face, Body.GetTessellation(faces, options), FaceTessellation.Vertices/Facets and MeshPrimitive.CreateFacets.
The implementation now tessellates only the selected master face, converts PositionNormalTextured vertices via PositionNormal and transforms the tessellation back to the occurrence coordinates. Backface culling is disabled for two-sided red fill. Face borders are not substituted for fill. Label sizing is retained.
CAD geometry, appearance and Named Selections are not edited by highlighting.
Validation: syntax and existing regression tests outside SpaceClaim. Visual/runtime confirmation in SpaceClaim is still required.

# v0.15.3 — Fix FacetSense import failure

The supplied SpaceClaim log confirms ImportError: Cannot import name FacetSense from Modeler.
The fill code now resolves the enum and tessellation options directly from the installed public GetTessellation method signature. It no longer imports FacetSense/TessellationOptions from a guessed namespace.
Also uses clr.GetPythonType for the typed facet list. Full underlying fill errors are displayed in the UI and logged.
Red face fill and label size controls are retained. No outline fallback for faces.
Validation: Python syntax and existing geometry tests. SpaceClaim V19 execution and visual fill remain to be verified in the host.

# v0.15.2 — Red face fill (host test required)

Side B face selections now use red filled mesh graphics from trimmed CAD face tessellation, instead of perimeter curves. Applies to contact and weld face groups. Edge groups retain red lines. The fill does not change CAD appearance or Named Selection contents. Label size control is retained.

SpaceClaim V19 runtime is not available in the build environment. Verify face fill, holes, both viewing sides and Clear Highlight in SpaceClaim. If the V19 tessellation/display API rejects the call, the operation reports a highlight failure and writes details to the existing log; it does not substitute outlines or modify model colors.

# v0.15.1 — Adjustable label size

Label size (%) controls geometry label height: 10–500%, default 100% (previous size).
Changes redraw visible labels immediately. The value persists when closing and reopening the tool within the same SpaceClaim session.
Labels are model-space line graphics, not screen-space fonts; their apparent size still changes with camera zoom.
Contact side B intentionally uses a red boundary overlay; side A uses SpaceClaim secondary selection shading. Named Selection contents remain faces.
No face recoloring or CAD geometry changes are made by these display controls.
Syntax and existing geometry tests checked outside SpaceClaim; host UI/runtime verification remains required.

# v0.15.0 — Contact Named Selections

Added Purpose: Contact pair (ctkt).
Select one or more faces, then Create Next: ctkt1a, ctkt1b, ctkt2a, ctkt2b, ... ctkt9999999a, ctkt9999999b.
Numbering is case-insensitive, independent of w/f/fm, fills gaps and never overwrites existing groups.
A uses blue selection highlighting; B uses the existing red overlay. Current/all highlighting, Find Groups and optional labels support ctkt.
This creates Named Selections only; assign Contact/Target and contact properties in Mechanical separately.
Contact geometric QA is not implemented; its manager button is disabled. Faces may participate in multiple contact groups.
Based on v0.14.1. SpaceClaim runtime verification is required (SpaceClaim is unavailable in the build environment).

# Changelog

## v0.14.1 — 2026-09-30 (test)

- Added pre-creation Bolt Pair axis screening using complete circle centres and adjacent planar plate normals; default deviation tolerance is 1 degree, configurable in the window.
- First-side creation is PENDING until the counterpart is available; invalid completed pairs are blocked before mutation.
- Added an audit of existing Bolt pairs with OK / ERROR / INCOMPLETE, angle details and orange problem highlight.
- Added 16 isolated geometry and mutation-guard tests. SpaceClaim 2021 R1 runtime verification is pending.

## v0.14.0 — 2026-09-30 (test)

- Added a checkbox for temporary names beside highlighted Named Selection geometry in weld, bolt and Face Meshing modes.
- Added selected-geometry membership lookup; shared faces list all matching groups, while unreadable groups are explicitly reported.
- Labels use the existing temporary curve-graphic mechanism and are cleared with highlights; no annotation objects are created.
- Isolated checks passed; target SpaceClaim 2021 R1 testing is pending.

## v0.13.3 — 2026-09-25

- Added Check Existing Face Meshing in `fm` mode: read-only audit of all existing `fm` groups, reporting duplicate faces and their group names.
- Highlight shared faces blue for visual inspection; fail with an incomplete-check message if any `fm` group cannot be read.
- SpaceClaim runtime validation of the audit is pending.

## v0.13.2 — 2026-09-25

- Prevent overlapping faces across `fm` Named Selections during Create Next, including partial overlaps in multi-face selections.
- Report the conflicting group names and face counts before mutation; stop if any existing `fm` group cannot be inspected.
- SpaceClaim runtime validation of this safeguard is pending.

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
