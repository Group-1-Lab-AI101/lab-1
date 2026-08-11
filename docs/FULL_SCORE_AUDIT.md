# Full-score Readiness Audit

Audit basis: all ten pages of the official Lab 1 specification, the group task
division, the integration contract, source code, tests, API output, and desktop
and mobile GUI behavior.

## Status by scoring criterion

| Criterion | Points | Current readiness | Main evidence/risk |
| --- | ---: | --- | --- |
| Vietnamese context | 10 | Strong | 24 real HCMC landmarks and OSM roads |
| Graph, dataset, cost | 15 | Strong with limitation | 481/995 graph; hybrid profiles; landmark offsets and boundary connector must be disclosed |
| Required algorithms | 20 | Strong | Independent BFS, DFS, UCS, A*; all-pair optimality checks |
| Additional algorithms | 10 | Strong | Dijkstra and Greedy with dedicated tests |
| Multi-location | 10 | Strong | Nearest, exact, gap, end/return, unique landmark nodes |
| GUI/visualization | 10 | Strong | Map, visited/frontier/current, path and metrics, `g/h/f` trace detail |
| Explanation/alternatives | 10 | Strong | Named congestion segments, guarantee, distinct baseline metrics |
| Technical report | 10 | Strong | Final 13-page illustrated PDF contains verified group identity and references |
| Demo video | 5 | Missing | Verified 15-slide deck, walkthrough, and script exist; recording/link do not |

## Critical blockers

1. Backend and frontend are pushed, but GitHub rejects both `main` and a new
   branch push to the parent repository with HTTP 403. Its complete deliverable
   commit and updated submodule pointers currently exist only on this machine.
2. All three source links return HTTP 404 in a signed-out request because the
   repositories are private. The instructor must be granted access or the
   repositories must be made public before submission.
3. A recorded demo video and public/viewable link do not exist.
4. The final single ZIP with the exact required filenames does not exist because
   the required video URL is unavailable.

## Verified engineering evidence

- 70 automated backend tests pass.
- Frontend TypeScript and Vite production build pass.
- All 552 ordered landmark pairs are reachable.
- UCS, A*, and Dijkstra return identical optimal cost on all 552 pairs.
- A* heuristic consistency audit reports zero violations.
- The reproducible exhaustive audit is stored in
  `lab-1-backend/docs/full_audit_results.json` and can be regenerated with
  `python examples/run_full_audit.py`.
- 24 landmarks map to 24 distinct graph nodes.
- Single, Compare, and Multi GUI workflows run on desktop and mobile.
- Browser console is clean after route animation.
- The 15-slide deck has sources in speaker notes, renders correctly, and passes
  the automated overflow check.
- The final 13-page report was rendered and visually checked page by page with
  the five supplied names and student IDs; no placeholder metadata remains.
- Pushed backend commit `ec98af3` and frontend commit `4665d32` were rebuilt
  from freshly initialized parent submodules. The parent deliverables are in a
  local commit awaiting repository write access.

## Honest score outlook

The engineering implementation is competitive for nearly all 85 technical
points, but the current repository/submission state is not grade-ready. Without
accessible source links, the official video link, and the exact ZIP, the project
cannot be called a full-score submission. After those artifacts are completed
and checked in a signed-out browser, the project has a credible full-score
target; no score can be guaranteed because final marking remains the
instructor's decision.
