# SpaceClaim Named Selection Namer v0.13.1

**GitHub release — 25 September 2026**

- Three independent naming modes: weld pairs `wNa/wNb`, bolt Edge pairs `fNa/fNb` and Mechanical Face Meshing groups `fmN`.
- Bolt pairs use A blue / B red highlighting; Face Meshing groups use blue highlighting. Auto / Current / All highlighting follows the selected purpose.
- Existing weld QA and repair remain weld-only.
- Empty-document root group reading has the v0.12.1 fallback.
- The user confirmed the Bolt Pair and Face Meshing workflows and their highlights in SpaceClaim 2021 R1. Earlier weld validation is documented in `docs/VALIDATION.md`.
- README now includes four real v0.13.1 interface screenshots supplied by the user.

Installation: extract the release ZIP, open `Weld_Namer.py` in the SpaceClaim 2021 R1 Script Editor (API V19), select geometry and run the script.

---

## Historical v0.12.0 release notes

# SpaceClaim Weld Namer v0.12.0

**Stable release — 16 September 2026**

v0.12.0 turns SpaceClaim Weld Namer from a sequential naming helper into a complete weld Named Selection preparation and QA workflow for SpaceClaim 2021 R1.

## Main additions

- A/B color separation: **A blue, B red** without changing CAD colors.
- Named Selection QA table with **OK / CHECK / ERROR** screening.
- Orange global problem highlighting.
- Problem navigation, selected-pair highlight and zoom.
- CSV QA export.
- Controlled repair of selected weld groups:
  - Replace A/B;
  - Add to A/B;
  - Remove from A/B;
  - Create Missing A/B;
  - Highlight Conflict.
- Repair operations verify the resulting group contents and refresh QA.

## Validation

Validated on the real target environment:

- ANSYS SpaceClaim 2021 R1;
- Script API V19;
- IronPython 2.7;
- large Edge-based weld model;
- 104 weld groups / 346 geometry items exercised in the recorded global-highlight validation session.

The normal Create Next mutation chain remains unchanged from the validated baseline.

## Log

```text
%TEMP%\SpaceClaim_Weld_Namer_v012.log
```

## License

GNU GPL v3.0.

## Companion project

MPC184 Viewer: https://github.com/maximofflove/MPC184Viewer

## Optional support

https://boosty.to/ansys2021/donate

## 0.12.1 (group read fallback)

When the SpaceClaim scripting API raises a null-reference exception in a modeless callback, try reading Named Selection groups directly from the root part. If both methods fail, stop without creating a group and record both exceptions in the existing log. Requires verification in SpaceClaim 2021 R1.

## 0.13.0 (Bolt and Face Meshing names)

Added independent `fNa/fNb` edge groups for bolts and `fmN` face groups for Mechanical Face Meshing. The purpose selector constrains the geometry type and Check Next Name follows the selected sequence. Weld QA and highlighting remain scoped to `w` groups. SpaceClaim runtime testing is required.

## 0.13.1 (Bolt and Face Meshing highlights)

The auto-highlight option and both highlight buttons now follow the selected purpose. Bolt pairs use A=blue secondary selection and B=red temporary overlay. Face Meshing groups use blue secondary selection; Current highlights the last group created in the current window or the largest numbered `fm` group after reopening. Switching purposes clears old highlights. Weld QA remains weld-only. Requires runtime verification in SpaceClaim 2021 R1.
