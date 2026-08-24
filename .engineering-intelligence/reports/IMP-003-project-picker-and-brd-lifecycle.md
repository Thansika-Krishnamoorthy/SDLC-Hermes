# IMP-003: Project picker siblings, hide approved BRD, save per feature

## Classification
- Type: bugfix
- Risk: low
- Scope: browse root / workspace defaults, git repo listing, BRD save uniqueness, approval UI
- Depth: Standard

## Analysis
- Mode: in-progress
- Empty `BROWSE_ROOT` must resolve to the home directory, not the process cwd (this repo).
- Folder picker opens at `$HOME` so projects under `~/projects`, `~/Documents`, and similar are visible; git listing scans those trees first.
- Approve must persist the BRD into `<project>/docs/`, hide the on-screen draft, and start a new session/file for a later requirement.

## Validation Requirements
- Unit tests for empty browse root, unique BRD filenames, approve auto-save
- API tests for `/api/fs` default current path under a constrained browse root
- Existing git sibling discovery tests
