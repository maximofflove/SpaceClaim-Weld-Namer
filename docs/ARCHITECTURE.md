# Architecture and API Notes — v0.13.1

## Design principle

The project favors predictable mutations that have been confirmed on the target SpaceClaim 2021 R1 / API V19 installation. Diagnostic reflection is used to learn the API; production code avoids speculative signatures.

## 1. Naming

The sequence is:

```text
w1a, w1b, w2a, w2b, ...
```

Existing matching names are converted to occupied sequence positions and the first free slot is used. No persistent numeric counter is required.

## 2. Root-group enumeration

Stable enumeration uses:

```python
NamedSelection.GetGroups(root)
```

The target installation established:

- `Part.Groups` is unavailable;
- parameterless `NamedSelection.GetGroups()` can fail from the modeless callback;
- explicit root-part enumeration works on populated parts; in an empty document it can throw and `root.GetChildren[Group]()` supplies a read-only fallback.

## 3. Normal creation transaction

```text
read primary selection
validate Faces / Edges
read root groups before
calculate next name
NamedSelection.Create(selection, Selection.Empty())
read root groups after
verify exactly one group was added
NamedSelection.Rename(temporary_name, target)
verify rename
```

The normal creation path does not retry mutations using guessed alternate signatures.

## 4. Modeless UI lifecycle

Direct `Form.Show()` from the script execution thread previously produced a frozen form. The stable implementation schedules form creation through WinForms `BeginInvoke` on the SpaceClaim UI thread.

Window/session state is kept in `AppDomain` and synchronized with `Monitor`. Repeated script runs while the window is queued/open do not create duplicate forms.

## 5. A/B visualization

### A side

A-side geometry uses SpaceClaim Secondary Selection:

```python
Selection.Create(a_items).SetActiveSecondary()
```

### B side

The user's V19 reflection probe confirmed:

- `DesignEdge.Shape -> Modeler.Edge`;
- `Modeler.Edge` implements `ITrimmedCurve`;
- `CurvePrimitive.Create(ITrimmedCurve)`;
- `GraphicStyle.LineColor` and `LineWidth`;
- writable `Window.Rendering`.

B-side geometry is therefore rendered as a temporary red `Display.Graphic`.

For Face groups, the overlay is drawn on the boundary edges of the selected Faces so the parent body's CAD color is not changed.

### `Window.Rendering` null getter behavior

A real target test showed that the `Window.Rendering` getter can throw when the custom-rendering slot has not been initialized. Direct assignment works:

```text
window.Rendering = graphic
window.RefreshRendering()
```

The stable overlay state therefore avoids reading that getter. Red B graphics and orange QA graphics are composed in application state and written as one combined Graphic.

## 6. QA screening

The QA scan builds a case-insensitive weld-group map, resolves each group's geometry, tracks geometry usage across groups and calculates pair-level records.

For Edge pairs the comparison metric is total curve length; for Face pairs it is total area. The relative difference is only a screening value.

The code also protects against accidental very large sequence gaps: it does not generate millions of missing rows if a high-number weld group appears unexpectedly.

## 7. Controlled repair

The repair API probe confirmed:

```text
NamedSelection.Replace(name, primary, secondary, ICommandInfo)
NamedSelection.Delete(names[])
```

and that `Group.Members` is read-only.

Existing groups are therefore changed via `NamedSelection.Replace(...)`, not by mutating `Members`.

Repair sequence:

```text
read current primary selection
validate homogeneous Edges or Faces
construct desired final item list
ask for confirmation
NamedSelection.Replace(...)
re-read group via Selection.CreateByGroups(...)
compare actual and expected geometry keys
refresh QA
```

Creating a missing A/B side reuses the already validated Create + Rename model, followed by explicit geometry verification.

## 8. Compatibility

Validated target:

- SpaceClaim 2021 R1
- Script API V19
- IronPython 2.7

Compatibility with other releases should be claimed only after real testing.

## 8. Additional name sequences and highlighting

The v0.13.x purpose selector routes name allocation independently: `wNa/wNb` for welds, `fNa/fNb` for bolt edges, and `fmN` for faces. All modes use the verified single Create and Rename path. Bolt A/B highlighting reuses the same temporary blue/red visual channels as welds. `fm` groups use blue Secondary Selection without the red overlay. Weld QA and repairs scan only `w` groups.
