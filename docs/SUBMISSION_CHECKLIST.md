# Full-score Submission Checklist

The official submission must be one `[GroupID].zip` containing all five named
deliverables below.

## Required files

- [ ] `1 - SC.txt` contains source-code links, but the repositories must still be
  made accessible to the instructor.
- [x] `1 - Report.pdf` contains the complete technical report.
- [x] `1 - Slide.pptx` is ready.
- [ ] `[GroupID - Video].txt` contains a viewable demo-video link.
- [x] `1 - Data.txt` describes/includes data.

## Identity and contribution checks

- [x] Confirm official Group ID as `1`.
- [x] Create `docs/group_metadata.json` from the example and fill all five
  verified full names and student IDs.
- [x] Confirm full names and contribution statements.
- [x] Add the actual completion level for each requirement.

## Source-code delivery

- [x] Commit backend changes and push them to the backend repository.
- [x] Commit frontend changes and push them to the frontend repository.
- [x] Update parent Git submodule pointers to those commits.
- [ ] Push the committed report/source-link/data documents in the parent
  repository; GitHub currently rejects the push with HTTP 403.
- [x] Clone the submitted links as submodules and run tests/build from scratch.
- [x] Do not include `node_modules`, `.venv`, `dist`, caches, or secrets.
- [ ] Make all three source links accessible to the instructor; a signed-out
  request currently returns HTTP 404 because the repositories are private.

## Report

- [x] Export the report source to `1 - Report.pdf`.
- [x] Build and visually verify the 13-page Unicode PDF export pipeline using
  both draft data and long Vietnamese QA names.
- [x] Add verified Single, Compare, and Multi screenshots to the report source.
- [x] Verify all 13 pages, diagrams, tables, page numbers, captions, and OSM attribution.
- [x] Check that every benchmark claim matches `benchmark_results.json`.
- [x] Make the final exporter reject missing or sample identity values.

## Slides and video

- [x] Generate and visually verify the 20-slide presentation deck.
- [x] Run the presentation overflow test and verify all speaker-note source blocks.
- [x] Explain all six algorithms using the group-designed example.
- [x] Show expansion order and frontier/open list for every algorithm.
- [x] Show `g` for UCS/Dijkstra and `g/h/f` for A*.
- [x] Show `h` for Greedy and explain why its result may be non-optimal.
- [x] Cover Single, Compare, and Multi modes in the slide deck.
- [x] Cover at least two traffic conditions and explain a route change.
- [x] Compare Nearest Neighbor with Exact Brute Force.
- [ ] Demonstrate and verify the same workflows in the actual video.
- [ ] Confirm the video link works in a signed-out browser.

The prepared slide deck and demo script contain the required material; the
remaining demo items must be verified against the actual video.

## Final verification

- [x] Backend: `python -m unittest discover -s tests -v` (72 tests passed).
- [x] Exhaustive audit: `python examples/run_full_audit.py` (552/552 pairs
  reachable, zero optimal-cost mismatches, zero heuristic violations).
- [x] Frontend: `pnpm build`.
- [x] Verify desktop and mobile layouts with a clean browser console.
- [x] Dry-run `scripts/build_submission.ps1` and verify its exact five-file ZIP
  manifest on Windows PowerShell 5.1.
- [ ] Run `scripts/build_submission.ps1` with the official Group ID, final PDF,
  and public video URL.
- [ ] Open every file and link inside the final ZIP.
- [ ] Keep one local and one cloud backup before submission.
