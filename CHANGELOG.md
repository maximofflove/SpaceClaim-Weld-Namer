# Changelog

## v0.10.0 — Stable — 2026-09-11

Promoted to stable after successful testing on the real SpaceClaim 2021 R1 installation.

Added:

- **Auto highlight current pair after Create**.
- **Highlight Current Pair**.
- **Highlight All Weld Groups** wording for the global highlight command.
- Current-pair calculation based on the first free sequential weld name.
- Persistence of Auto Highlight state within the SpaceClaim session.
- Current-pair information in **Check Next Name**.
- Diagnostic log `%TEMP%\SpaceClaim_Weld_Namer_v010.log`.

Validated on the real target installation:

- current-pair highlight after creating side `a`;
- complete pair highlight after creating side `b`;
- manual **Highlight Current Pair**;
- **Highlight All Weld Groups**;
- Auto Highlight behavior;
- close/reopen with retained Auto Highlight state;
- existing v0.9 Edges/reopen/Secondary Selection workflow.

The proven Named Selection create/rename chain was retained unchanged.

## v0.9 — Stable

- Promoted Secondary Selection highlighting to the stable baseline.
- Edges/reopen/highlight confirmed on real SpaceClaim 2021 R1.
- Exact weld geometry can be highlighted without modifying CAD color.

## v0.8 — Highlight Test

- Replaced ineffective per-edge CAD color visualization with Secondary Selection.
- Added weld-group highlight and clear-highlight controls.

## v0.7 — Color Test

- Experimental color-based visualization.
- API calls completed without exception but did not provide the required per-edge visual result on the target model.
- Color approach abandoned for weld visualization.

## v0.6 — Reopen Fix

- Fixed stale window lock after closing the form.
- Window can be reopened by running the script again.
- Duplicate launch requests while queued/open are suppressed.
- Faces/Edges selection mode retained in the SpaceClaim session.

## v0.5 — Validated Creation Baseline

- Confirmed creation of `w1a` and `w1b` from selected edges.
- Established the creation chain retained by later versions:

```text
Selection.GetActive()
NamedSelection.GetGroups(root)
NamedSelection.Create(selection, Selection.Empty())
NamedSelection.Rename(temporary_name, target)
```
