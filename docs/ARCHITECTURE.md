# Architecture and API Notes

## Design goal

SpaceClaim Weld Namer remains a small SpaceClaim script while the workflow is mature and validated. v0.10.0 is not an ACT extension and not a compiled Add-In.

The architecture prioritizes predictable model mutation over abstraction: the Named Selection creation path uses the API calls confirmed on the target SpaceClaim 2021 R1 / V19 installation.

## 1. Naming model

The sequence is:

```text
w1a, w1b, w2a, w2b, ...
```

Each existing weld group is mapped to an occupied sequence index. The first free index becomes the next group name.

Consequences:

- no external counter is required;
- deleting a group makes its position available again;
- gaps are filled automatically;
- case is ignored;
- unrelated Named Selections do not affect weld numbering.

## 2. Root-part group enumeration

The target installation established that enumeration should use:

```python
NamedSelection.GetGroups(root)
```

Rejected for the target environment:

- `Part.Groups` — unavailable in the tested API;
- parameterless `NamedSelection.GetGroups()` — previously caused a null-reference failure from the modeless form callback.

`GetGroups(root)` is therefore an invariant of the stable implementation.

## 3. Creation transaction

The stable mutation path is:

```text
read current selection
validate geometry type
read root groups before creation
calculate next name
NamedSelection.Create(...)
read root groups after creation
verify exactly one new group
NamedSelection.Rename(temporary_name, target)
verify final group set
```

The code does not retry model mutation with alternative API signatures. Reflection is used only for diagnostics.

## 4. Modeless window and UI thread

Creating the WinForms form directly from the script execution thread previously produced a frozen window.

The stable solution creates the form through `BeginInvoke` on the SpaceClaim host UI thread.

Repeated presses of Run are handled through application `AppDomain` state synchronized with `Monitor`.

Conceptual phases:

```text
none -> queued -> open -> closed -> queued -> open ...
```

A launch request received while `queued` or `open` is ignored. `FormClosed` clears the live form reference and changes the phase to `closed`, allowing a later Run to create a fresh window.

Faces/Edges and Auto Highlight preferences are kept in the same session state.

## 5. Visualization

### Rejected approach: CAD color

The v0.7 color experiment completed without exceptions but did not visibly mark the required individual edges on the real target model.

Permanent CAD color is therefore not used for weld visualization.

### Stable approach: Secondary Selection

Named Selection geometry is resolved and placed in SpaceClaim Secondary Selection.

Benefits:

- exact topology stored by the weld groups is highlighted;
- no helper geometry is generated;
- CAD appearance is not modified;
- highlight can be cleared independently.

Highlighting is post-processing. Creation is complete after the successful rename/verification chain; a later highlight error must not invalidate that model change.

## 6. Current-pair highlighting in v0.10

Automatic visualization is limited to the pair associated with the group just created.

Example:

```text
Create w5a -> resolve pair w5 -> highlight w5a
Create w5b -> resolve pair w5 -> highlight w5a + w5b
Create w6a -> resolve pair w6 -> highlight w6a
```

Manual **Highlight Current Pair** uses the same pair-resolution logic. **Highlight All Weld Groups** remains available for global review.

This behavior was validated on the real SpaceClaim 2021 R1 installation before v0.10.0 was promoted to stable.

## 7. Compatibility strategy

The project currently targets exactly:

- SpaceClaim 2021 R1
- Script API V19
- IronPython 2.7

Compatibility statements for other versions should be added only after real validation or clearly identified as unverified.
