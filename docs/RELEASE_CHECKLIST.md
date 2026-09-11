# Release Checklist

Use this checklist before creating a stable GitHub Release.

## Model behavior

- [ ] Root part active requirement produces a clear error when violated.
- [ ] Empty selection rejected.
- [ ] Mixed selection rejected.
- [ ] Edge mode accepts the required SpaceClaim edge types.
- [ ] Face mode tested if the release claims Face validation.
- [ ] Multiple selected items create exactly one Named Selection.
- [ ] Existing groups are not overwritten.
- [ ] Gap-aware numbering verified.
- [ ] Case-insensitive existing names verified.

## Window lifecycle

- [ ] First Run opens one window.
- [ ] Repeated Run while open does not create a duplicate.
- [ ] Close with X.
- [ ] Run again reopens the window.
- [ ] Selection mode persists if claimed.
- [ ] Auto Highlight state persists if claimed.

## Highlighting

- [ ] Secondary Selection highlights only weld geometry.
- [ ] Clear Highlight removes Secondary Selection.
- [ ] Highlight Current Pair shows only the intended pair.
- [ ] Create side `a` with Auto ON highlights the available part of that pair.
- [ ] Create side `b` with Auto ON highlights both sides of that pair.
- [ ] Auto OFF does not prevent successful Create.
- [ ] Highlight All Weld Groups remains functional.
- [ ] Create remains successful if highlighting fails.

## Diagnostics

- [ ] Log file created in `%TEMP%`.
- [ ] Creation and rename events logged.
- [ ] Errors include useful diagnostics.
- [ ] Log name/version matches the release version.

## Packaging

- [ ] Version in window title updated.
- [ ] Version in source header updated.
- [ ] README updated.
- [ ] CHANGELOG updated.
- [ ] Validation matrix distinguishes real tests from static tests.
- [ ] No logs, temporary files, `__pycache__`, or editor files included.
- [ ] ZIP extracts cleanly.

## GitHub publication

- [ ] Repository description added.
- [ ] Topics/tags added (`ansys`, `spaceclaim`, `ironpython`, `fea`, `welding`, `automation`, `named-selection`).
- [ ] License decision made before describing the project as open source.
- [ ] Stable tag created only from a real-validated build.
