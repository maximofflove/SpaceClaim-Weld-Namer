# GitHub release helper — v0.15.8

Use this file as a copy/paste checklist when publishing the release.

## Repository commit

**Commit message**

```text
Release SpaceClaim Named Selection Namer v0.15.8
```

Upload the **contents** of the `SpaceClaim-Weld-Namer` folder from the GitHub-ready archive to the repository root. Do not upload the outer folder as an extra directory level.

## Release

**Tag**

```text
v0.15.8
```

**Release title**

```text
SpaceClaim Named Selection Namer v0.15.8
```

Publish as a normal **Latest release**; do not mark it as Pre-release.

**Suggested release text**

```text
Contact pair (ctkt) now has the same controlled QA / Repair workflow as Weld pair.

New in v0.15.8:
- Contact Named Selection QA / Repair Manager.
- Replace A/B, Add to A/B, Remove from A/B.
- Create Missing A/B.
- Highlight / Zoom Selected Pair.
- Highlight Problems and Highlight Conflict.
- Contact QA CSV export.
- Contact repair is Faces-only.
- Existing ctkt groups are updated through NamedSelection.Replace(...), then re-read and revalidated.
- Weld repair behavior is unchanged.
- Detailed English/Russian User Guide added.

Validation: 23/23 automated regression checks passed. The Contact QA / Repair workflow was then confirmed by the user in SpaceClaim 2021 R1 / API V19. A supplied validation capture shows `Add to B` updating `ctkt37b` to 8 Faces followed by automatic revalidation. v0.15.8 is the stable release.
```

Attach `SpaceClaim_Named_Selection_Namer_v0.15.8_RELEASE.zip` as the Release asset.
