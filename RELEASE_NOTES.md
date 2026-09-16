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
