# Validation Matrix

Target environment:

- SpaceClaim 2021 R1
- Script API V19
- Built-in IronPython 2.7

The project distinguishes tests performed on the **real target installation** from developer/static checks.

## v0.10.0 STABLE — confirmed on the real installation

| Test | Result |
|---|---|
| Modeless WinForms window starts on SpaceClaim UI thread | PASS |
| Close window -> Run script again -> window reopens | PASS |
| Repeated Run while queued/open does not create duplicate windows | PASS |
| `NamedSelection.GetGroups(root)` | PASS |
| Edges accepts `DesignEdgeGeneral` | PASS |
| Multiple selected edges stored in one Named Selection | PASS |
| Sequential `wNa / wNb` creation and continuation | PASS |
| Gap-aware next-name calculation | PASS |
| Existing groups are not overwritten by normal creation | PASS |
| Secondary Selection highlights exact weld geometry | PASS |
| Highlight All Weld Groups | PASS |
| Auto highlight current pair after Create | PASS |
| Create side `a` -> available part of current pair highlighted | PASS |
| Create side `b` -> both sides of current pair highlighted | PASS |
| Highlight Current Pair | PASS |
| Auto Highlight can be disabled without breaking Create | PASS |
| Close/reopen preserves Auto Highlight state | PASS |

## Earlier v0.7 color experiment

| Observation | Result |
|---|---|
| Color API accepted edge selections without exception | OBSERVED |
| Log recorded color calls | OBSERVED |
| Required per-edge visual result | FAILED |
| Decision | CAD color abandoned for weld visualization |

## Not yet confirmed on the real installation

| Test | Status |
|---|---|
| Faces mode end-to-end | TODO |
| Publish Script as Tool | TODO |
| Shortcut conflict check and hotkey assignment | TODO |

## Behavioral invariants

- Highlight failure must not delete or invalidate a successfully created Named Selection.
- `NamedSelection.Create` is executed once on the normal path; no mutation retry with alternative signatures.
- The next name is recalculated from root groups on every Create/Check operation.
- Existing matching weld groups are never intentionally overwritten by normal creation.
- Visualization uses Secondary Selection, not permanent CAD color modification.
