# Development Notes

These notes summarize API findings established during v0.10–v0.12 development on the real SpaceClaim 2021 R1 / V19 installation.

## Confirmed working production calls

```text
Selection.GetActive()
NamedSelection.GetGroups(root)
NamedSelection.Create(selection, Selection.Empty())
NamedSelection.Rename(temporary_name, target)
Selection.CreateByGroups(name)
Selection.Create(items).SetActiveSecondary()
NamedSelection.Replace(name, selection, Selection.Empty())
```

## Highlight API findings

Confirmed by reflection:

```text
Display.CurvePrimitive.Create(ITrimmedCurve)
Display.Graphic.Create(...)
Display.GraphicStyle.LineColor
Display.GraphicStyle.LineWidth
Window.Rendering (writable)
Window.RefreshRendering()
```

Real runtime behavior:

- reading `Window.Rendering` can throw a null-reference when its custom slot is empty;
- assigning a Graphic directly works;
- assigning `None` and calling `RefreshRendering()` clears the custom overlay.

## Repair API findings

Confirmed by reflection:

```text
NamedSelection.Replace(String, ISelection, ISelection, ICommandInfo)
NamedSelection.Delete(String[])
```

`SpaceClaim.Api.V19.Group.Members` is readable but not writable, so production repair does not attempt collection mutation.

## Deliberately retained constraints

- Root part must be active for creation/repair.
- `MAX_PAIR = 99999999`.
- No Ctrl+W shortcut in v0.12.0.
- QA tolerance is screening logic, not a weld-design acceptance criterion.
