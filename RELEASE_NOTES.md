# SpaceClaim Named Selection Namer v0.15.8 — Contact pair repair support

**Release status: Stable** — runtime-confirmed in SpaceClaim 2021 R1 / API V19 on 2026-10-02.
## New in this release

`Contact pair (ctkt)` now opens **Contact Named Selection QA / Repair Manager**. For a selected `ctktN` pair the manager supports:

- Replace A / Replace B;
- Add to A / Add to B;
- Remove from A / Remove from B;
- Create Missing A / Create Missing B;
- Highlight / Zoom Selected Pair;
- Highlight Problems / Clear Problem Highlight;
- Highlight Conflict;
- Contact QA CSV export.

Contact operations are **Faces only**. Existing `ctkt` Named Selections are updated through the same `NamedSelection.Replace(...)` workflow used by Weld repair, then re-read and verified before the QA table is refreshed. The v0.15.7 muted-blue/sand Contact visualization is preserved.

## Documentation

- cleaned GitHub README in English and Russian;
- added detailed `docs/USER_GUIDE.md` and `docs/USER_GUIDE_RU.md` describing every main-window and Repair Manager control;
- added the latest real SpaceClaim screenshots supplied for the GitHub update, including final v0.15.8 Contact main-window and Contact QA / Repair validation captures, while retaining earlier validated Weld/Bolt/Face Meshing images.

## Validation

Automated checks outside SpaceClaim: **23/23 passed** (16 Bolt geometry/mutation-guard tests + 7 Contact repair static/routing tests).

Runtime confirmation has now been completed in **SpaceClaim 2021 R1 / API V19**. The user confirmed the Contact QA / Repair workflow works; the supplied validation capture shows **Add to B** updating `ctkt37b` to 8 Faces followed by automatic revalidation. v0.15.8 is therefore released as **stable**.
