# SpaceClaim Named Selection Namer

A semi-automatic Named Selection tool for welds, bolt joints and Mechanical Face Meshing in **SpaceClaim 2021 R1 / API V19 / IronPython 2.7**. Weld groups also have QA and repair controls.

**Current release: v0.13.1**

> SpaceClaim script for the Script Editor. It is not an ACT extension or DLL.

## Name sequences

| Purpose | Geometry | Sequence | Highlight |
| --- | --- | --- | --- |
| Weld Pair | Faces or Edges | `w1a`, `w1b` … `w99999999b` | A blue, B red |
| Bolt Pair | Edges | `f1a`, `f1b` … `f999999b` | A blue, B red |
| Mechanical Face Meshing | Faces | `fm1` … `fm999999999` | Blue |

Select geometry and press **Create Next**. All selected items enter one group. Naming is case insensitive, fills gaps independently for each purpose and leaves existing groups intact. **Check Next Name** shows the next name in the selected mode. Auto highlight, Highlight Current and Highlight All follow the selected purpose; **Clear Highlight** removes the temporary colors. Weld QA / Repair applies only to `w` groups.

The user confirmed Bolt Pair and Face Meshing creation and highlighting in SpaceClaim 2021 R1. See [validation scope](docs/VALIDATION.md) for details.

## Interface screenshots — v0.13.1

Real screenshots from SpaceClaim 2021 R1.

**Weld Pair** — sequential weld groups and current pair:

![Weld Pair mode in v0.13.1](docs/images/v0131_weld_pair_window.png)

**Bolt Pair** — Edge groups `fNa/fNb`:

![Bolt Pair mode in v0.13.1](docs/images/v0131_bolt_pair_window.png)

**Face Meshing** — Face groups `fmN`:

![Face Meshing mode in v0.13.1](docs/images/v0131_face_meshing_window.png)

**Weld Named Selection QA / Repair Manager** — an example screening table from the user's model. CHECK rows need review in their model context.

![Weld QA and Repair Manager in v0.13.1](docs/images/v0131_weld_qa_repair_manager.png)

## Why this tool exists

The utility was created for large detailed structural submodels containing many welded joints. In this workflow every weld is prepared as a pair of Named Selections:

```text
w1a / w1b
w2a / w2b
w3a / w3b
...
```

Manually creating, naming and checking dozens or hundreds of these pairs becomes repetitive and easy to get wrong. SpaceClaim Weld Namer keeps the engineering decision with the user — the engineer selects the real geometry — while automating the naming, bookkeeping, visualization and QA around it.

The Named Selections can then be transferred to **ANSYS Mechanical** and used with the companion **MPC184 Viewer** workflow.

## Main workflow

```text
Select weld geometry in SpaceClaim
        ↓
Create Next
        ↓
wNa / wNb Named Selections
        ↓
A side = blue, B side = red
        ↓
QA / Repair Manager
        ↓
ANSYS Mechanical
        ↓
MPC184 Viewer
```

## Weld workflow inherited from v0.12.0

### Sequential Named Selection creation

The first free name is determined automatically:

```text
w1a -> w1b -> w2a -> w2b -> ... -> w99999999b
```

- case-insensitive existing-name detection;
- gaps are filled automatically;
- several selected edges or faces can be stored in one group;
- normal creation does not overwrite existing weld groups;
- numbering is recalculated from the actual root-part groups every time.

### Independent A/B visualization

- `w...a` is shown with the proven SpaceClaim **Secondary Selection** highlight (blue on the tested installation);
- `w...b` is drawn as a temporary **red `Display.Graphic`** overlay;
- CAD/body colors are not modified;
- `Highlight Current Pair`, `Highlight All Weld Groups` and Auto Highlight use the same A/B convention;
- `Clear Highlight` clears both visualization channels.

![A/B weld pair highlight](docs/images/v012_ab_pair_highlight.png)

### Named Selection QA Manager

The QA Manager scans weld groups and presents them as pairs in a table.

Checks include:

- missing `A` or `B` side;
- empty/unresolved Named Selection;
- mixed or unsupported geometry type;
- A/B type mismatch;
- the same geometry used in both A and B;
- geometry reused by another weld group;
- duplicate group names ignoring case;
- sequence gaps;
- edge-length / face-area mismatch above the screening tolerance (default 10%).

A/B object-count difference is displayed as **information**, not automatically treated as an error, because one physical weld side may be partitioned into a different number of topological edges/faces.

Available review functions include:

- **Validate All**;
- **Show Problems Only**;
- **Highlight Problems** in orange;
- **Previous Problem / Next Problem**;
- **Highlight Selected Pair**;
- **Zoom Selected Pair**;
- **Export CSV**.

![QA / Repair Manager](docs/images/v012_qa_repair_manager.png)

> QA status is a geometry/model-preparation screening result. It is not an engineering weld acceptance assessment.

### Controlled Repair Manager

The selected weld pair can be repaired using the current SpaceClaim primary selection:

- **Replace A / Replace B**;
- **Add to A / Add to B**;
- **Remove from A / Remove from B**;
- **Create Missing A / Create Missing B**;
- **Highlight Conflict** for reused geometry.

Repair operations validate the selected geometry type, request confirmation, execute the mutation, re-read the Named Selection and verify the resulting geometry before the QA table is refreshed.

Existing Named Selections are changed with the V19 scripting command `NamedSelection.Replace(...)`; `Group.Members` is deliberately treated as read-only.

## Real SpaceClaim validation

v0.12.0 was promoted from the test build after successful use on the real target installation:

- **ANSYS SpaceClaim 2021 R1**;
- **Script API V19**;
- built-in **IronPython 2.7**;
- large Edge-based weld model;
- at least **104 weld Named Selection groups / 346 geometry items** exercised by the global highlight during the validation session;
- A/B blue/red visualization confirmed;
- QA / Repair Manager opened and operated successfully;
- repair workflow reported by the user as working successfully.

Faces support is implemented, including face-area QA and red boundary rendering, but the public validation claim for v0.12.0 remains primarily the real **Edges** workflow unless separately tested.

See [docs/VALIDATION.md](docs/VALIDATION.md).

## Requirements

- ANSYS SpaceClaim **2021 R1**
- Script API **V19**
- built-in **IronPython 2.7**
- root component / root part active when creating or repairing weld groups

Other SpaceClaim versions may work, but are not claimed as validated by this release.

## Quick start

1. Open the SpaceClaim model and activate the **root component**.
2. Open `Weld_Namer.py` in the SpaceClaim Script Editor.
3. Select **API V19**.
4. Run the complete script.
5. Choose `Edges` or `Faces`.
6. Select geometry and click **Create Next**.
7. Use **Named Selection QA / Repair Manager** to validate, navigate, highlight and repair weld pairs.

The stable log is written to:

```text
%TEMP%\SpaceClaim_Weld_Namer_v012.log
```

## Important API behavior retained from validation

The normal creation chain remains intentionally conservative:

```text
Selection.GetActive()
NamedSelection.GetGroups(root)
NamedSelection.Create(selection, Selection.Empty())
NamedSelection.Rename(temporary_name, target)
```

Important target-installation observations:

- `Part.Groups` is not available in the tested environment;
- `NamedSelection.GetGroups(root)` is used explicitly;
- parameterless `NamedSelection.GetGroups()` previously failed from the modeless callback;
- the WinForms UI is launched on the SpaceClaim UI thread through `BeginInvoke`;
- AppDomain state + `Monitor` prevent duplicate windows during repeated script runs;
- `Window.Rendering` getter can throw while the custom rendering slot is empty, therefore the stable overlay path writes the property directly and refreshes the window without reading the getter first.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Repository layout

```text
SpaceClaim-Weld-Namer/
├── Weld_Namer.py
├── README.md
├── README_RU.md
├── CHANGELOG.md
├── RELEASE_NOTES.md
├── VERSION
├── LICENSE
├── SUPPORT.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── VALIDATION.md
│   ├── RELEASE_CHECKLIST.md
│   ├── DEVELOPMENT_NOTES.md
│   └── images/
└── tools/
    ├── API_Diagnostics.py
    ├── Allow_Reopen.py
    ├── Create_Next_Once.py
    ├── Weld_Highlight_API_Diagnostics.py
    ├── Weld_Highlight_API_Diagnostics_v2.py
    └── Weld_NamedSelection_Repair_API_Diagnostics.py
```

## Companion project

**MPC184 Viewer:** https://github.com/maximofflove/MPC184Viewer

SpaceClaim Weld Namer prepares `wNa / wNb` geometry groups; MPC184 Viewer uses the downstream Mechanical model to create, validate, visualize and post-process MPC184 weld connections.

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).

## Support

The project is completely free and open source. Optional voluntary support:

**https://boosty.to/ansys2021/donate**
