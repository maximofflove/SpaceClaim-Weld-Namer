# User Guide — SpaceClaim Named Selection Namer v0.15.8

This guide documents the visible controls and the validated workflow of the v0.15.8 stable release.

## 1. Main window

### Group purpose
Chooses the naming/audit workflow. The four modes are independent; existing `w`, `f`, `fm` and `ctkt` numbering does not interfere across purposes.

### Selection type
Defines which geometry is accepted by Create Next. Weld supports Faces or Edges. Bolt is locked to Edges. Face Meshing and Contact are locked to Faces.

### Create Next
Reads existing root-part groups, determines the first free name for the active purpose, validates the current selection and creates one Named Selection containing all accepted selected objects. It does not overwrite an existing target name. Mode-specific guards run before mutation: Face Meshing overlap prevention and Bolt geometry screening, where applicable.

### Check Next Name
Performs a read-only scan and reports the next name/current pair plus the number of groups inspected. Useful before creating anything or after manual edits to the tree.

### Auto highlight after Create
When enabled, immediately shows the newly created logical pair/group after Create Next. This is display-only.

### Show names of highlighted Named Selections
Adds temporary model-space labels next to highlighted geometry. Labels are display graphics, not model annotations and not CAD objects.

### Label size (%)
Scales the temporary labels from 10% to 500%. Because labels are model-space graphics, apparent screen size still depends on camera zoom.

### Bolt axis tolerance (degrees)
Active in Bolt mode. Sets the maximum angular deviation used by the Bolt axis screening. The default is 1 degree. This setting is a geometry-screening tolerance, not a bolt design criterion.

### Highlight Current Pair / Current Group
Highlights the logical current item inferred from the naming sequence. For pair modes it uses both A and B when present. In Face Meshing it highlights one `fmN` group.

### Highlight All ...
Highlights every group for the active purpose. Color conventions: Weld/Bolt A blue and B red; Face Meshing blue; Contact A muted blue and B sand.

### Clear Highlight
Clears pair/group graphics, temporary labels and orange QA/problem overlays. Named Selections and CAD geometry are unchanged.

### Weld Named Selection QA / Repair Manager
Available in Weld mode. Opens the detailed pair table and repair controls described in Section 2.

### Contact Named Selection QA / Repair Manager
Available in Contact mode in v0.15.8. Uses the same pair-management workflow as Weld but all contact group geometry and repair selection must be Faces.

### Check Existing Bolt Pairs
Read-only audit. Reports each pair as OK, ERROR or INCOMPLETE and highlights geometry problems. It does not edit Named Selections. Checks include complete circular rim/planar support assumptions and pair-axis deviation when both sides exist.

### Check Existing Face Meshing
Read-only audit of existing `fm` groups. Detects faces reused by more than one Face Meshing group and highlights overlaps blue. If a group cannot be read, the audit reports an incomplete check rather than silently continuing.

### Find Groups for Selected Geometry
Looks at the current SpaceClaim selection and lists all groups of the active purpose that contain those objects. This is useful when the model is visually crowded or one geometry item is intentionally shared.

### Output panel
Shows the latest action, counts, warnings, validation result or error. It is the first place to look when a button appears to have done nothing.

## 2. Weld / Contact QA and Repair Manager

### Validate All
Re-reads all matching pair groups from the active model and rebuilds the QA table.

### Show Problems Only
Filters the table to ERROR/CHECK records. It does not change the underlying validation results.

### Highlight Problems
Shows problematic pair geometry with an orange temporary overlay. Pair colors remain separate from the orange problem indication.

### Clear Problem Highlight
Removes only the orange QA overlay.

### Export CSV
Writes the current QA records to a CSV file. Weld and Contact use different default filenames. The export contains pair name, A/B group names, geometry types, counts, metric difference, status and reason.

### QA table columns
- **Weld / Contact**: logical pair number/name.
- **A / B**: actual group names found in the model.
- **Type A / Type B**: resolved geometry kind.
- **Count A / Count B**: number of objects in each side.
- **Metric diff %**: relative total edge-length or face-area difference where comparable.
- **Status**: OK, CHECK or ERROR.
- **Reason**: diagnostic explanation; count mismatch may appear as informational text.

### Previous Problem / Next Problem
Moves the table selection between problem records for rapid review.

### Highlight Selected Pair
Highlights the currently selected table row using the pair's normal A/B colors.

### Zoom Selected Pair
Temporarily selects the pair geometry for SpaceClaim zoom-to-selection, then restores the custom pair highlight.

## 3. Repair controls

Repair uses the **current SpaceClaim primary selection** as input. The selected table row determines which Named Selection will be changed.

### Replace A / Replace B
Replaces the complete contents of the selected side with the current SpaceClaim selection.

### Add to A / Add to B
Merges the current SpaceClaim selection into the chosen side, removes duplicates, replaces the Named Selection through the supported V19 command path, re-reads the result and revalidates the pair.

### Remove from A / Remove from B
Removes only selected objects that already belong to the chosen side. If none of the selected objects belongs to the group, nothing changes. If the removal would leave the group empty, the operation is blocked; use Replace instead if an empty-to-new transition is intended.

### Create Missing A / Create Missing B
Creates the absent side for a QA record using the current selection. The operation is rejected if the side already exists.

### Highlight Conflict
Highlights exact geometry involved in A/B internal reuse or reuse by other pair groups. If no reusable-geometry conflict exists, the normal pair highlight is shown instead.

### Confirmation and verification
All model-changing repair actions show a confirmation dialog. Existing groups are changed with `NamedSelection.Replace(...)`; the tool treats `Group.Members` as read-only. After mutation the target group is resolved again, its geometry is checked, the full pair table is rebuilt and the edited pair is reselected.

## 4. QA status interpretation

**ERROR** is used for structural group problems such as missing side, empty/unresolved group, invalid/mixed geometry, A/B type mismatch, same object on both sides, duplicate name ignoring case, or sequence problems.

**CHECK** is a screening warning. Examples include total edge-length / face-area mismatch above the configured 10% screening threshold or geometry reused by another pair group.

**OK** means no implemented QA finding was detected. It does not prove the engineering model is correct.

Object-count difference between A and B is informational because topological partitioning can differ across physically corresponding faces/edges.

## 5. Contact-specific rules

- names: `ctktNa` / `ctktNb`;
- Faces only for creation and repair;
- A = muted blue, B = sand;
- face-area difference is used for the metric screening;
- same-face reuse inside A/B and reuse by other contact groups is reported;
- Named Selection management does not create Mechanical Contact Region objects or assign Contact/Target behavior.

## 6. Safe operating sequence for repair

1. Open QA / Repair Manager and press **Validate All**.
2. Select the target row.
3. Use **Highlight Selected Pair** or **Zoom Selected Pair** to confirm it is the intended pair.
4. Select the exact replacement/add/remove geometry in SpaceClaim.
5. Press the required repair button.
6. Read the confirmation dialog carefully and accept only if the old/selected/result counts are expected.
7. Review the automatically revalidated row and visual highlight.
8. Export CSV if a traceable review record is needed.
