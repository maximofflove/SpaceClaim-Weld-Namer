# SpaceClaim Weld Namer v0.10.0

**Status:** Stable  
**Target:** ANSYS SpaceClaim 2021 R1 / Script API V19 / IronPython 2.7

v0.10.0 was promoted to stable after successful testing on the real target installation.

## New in v0.10

- Auto highlight of the current weld pair after **Create Next**.
- Manual **Highlight Current Pair**.
- Manual **Highlight All Weld Groups**.
- **Clear Highlight**.
- Auto Highlight state retained after closing and reopening the tool window in the same SpaceClaim session.
- Current pair is reported by **Check Next Name**.
- Log file: `%TEMP%\SpaceClaim_Weld_Namer_v010.log`.

## Unchanged core

The previously validated mutation path remains unchanged:

```text
Selection.GetActive()
-> NamedSelection.GetGroups(root)
-> NamedSelection.Create(selection, Selection.Empty())
-> verify exactly one new group
-> NamedSelection.Rename(temporary_name, target)
```

Secondary Selection remains the visualization mechanism; CAD colors are not modified.

## Validation note

The Edges workflow and the new v0.10 pair-highlighting controls were confirmed on the real SpaceClaim 2021 R1 installation. `Faces` mode is implemented but remains unvalidated at the time of this release.

## Distribution model

SpaceClaim Weld Namer is released as free and open-source software under GNU GPL v3.0. Optional project support is available through Boosty: https://boosty.to/ansys2021/donate. Donations do not unlock additional features.

## Companion project

For downstream ANSYS Mechanical weld-connection work, see **MPC184 Viewer**: https://github.com/maximofflove/MPC184Viewer
