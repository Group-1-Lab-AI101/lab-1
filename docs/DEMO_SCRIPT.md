# Saigon Route Lab - Demo Script

Target length: 9 to 12 minutes. The algorithm walkthrough is mandatory; do not
replace it with only an application tour.

## 1. Introduction - 45 seconds

- State the problem: plan tourist routes in central Ho Chi Minh City while
  considering distance, estimated time, congestion, and risk.
- Show the network count in the results panel: 481 nodes, 995 directed edges,
  and 24 landmarks.
- Briefly identify the React/Leaflet frontend and FastAPI backend.

## 2. Group-designed algorithm example - 4 minutes

Open `ALGORITHM_WALKTHROUGH.md` or the matching presentation slides. Introduce
the directed graph with two alternatives:

- `A -> B -> G`: 2 edges, weighted cost 9.
- `A -> C -> D -> G`: 3 edges, weighted cost 3.

For every algorithm, show the node removed from the frontier, the frontier
after generation, parent updates, and the final path.

1. **BFS:** expand `A, B, C, G`; return the two-edge cost-9 route. Explain that
   BFS is optimal by edge count, not weighted traffic cost.
2. **DFS:** with `B` first in adjacency order, expand `A, B, G`; return cost 9.
   Explain that DFS has no cost optimality guarantee.
3. **UCS:** show `g` values and pop `A(0), C(1), D(2), G(3)`; return cost 3.
   State that the goal is accepted only when popped at minimum cost.
4. **A*:** show `g`, `h`, and `f=g+h` for every popped node; expand
   `A(0+2), C(1+2), D(2+1), G(3+0)`; return cost 3.
5. **Dijkstra:** show the same non-negative cost order on this one-goal case and
   explain that the project also exposes reusable single-source distances.
6. **Greedy:** show `h` only, choose `B` before `C`, and return cost 9. Explain
   why ignoring accumulated `g` can make the route non-optimal.

End this section with a guarantee table: BFS by edge count; UCS, A*, and
Dijkstra by weighted cost under their stated assumptions; DFS and Greedy not
guaranteed.

## 3. Single route search - 1.5 minutes

1. Select `Nha tho Duc Ba` as start and `Thao Cam Vien Sai Gon` as destination.
2. Choose Dijkstra, balanced cost, and normal traffic.
3. Click **Find route**.
4. Point out the red route, blue visited nodes, amber frontier, current node,
   and dashed landmark-access links.
5. Use the play, pause, next, and slider controls to show the search trace.
6. Read distance, time, weighted cost, runtime, path-node count, expanded and
   generated counts, named congested segments, and the alternative comparison.

Explain that Dijkstra is optimal because every edge cost is non-negative.

## 4. Algorithm comparison - 1.5 minutes

1. Open **Compare** and run all algorithms with the same start, goal, criterion,
   and traffic profile.
2. Compare cost, distance, time, expanded nodes, and runtime.
3. Select different table rows so their routes appear on the same map.
4. Explain the expected contrast:
   - BFS optimizes edge count, not traffic cost.
   - DFS returns the first depth-first route.
   - UCS and Dijkstra minimize the weighted cost.
   - A* uses cost plus an admissible Haversine estimate.
   - Greedy uses only the estimate and is not guaranteed optimal.

Avoid claiming one algorithm is always fastest from a single run.

## 5. Multi-landmark route - 1.5 minutes

1. Open **Multi**.
2. Keep the reproducible four stops: Ben Thanh Market, Nguyen Hue Walking
   Street, Bach Dang Wharf, and Fine Arts Museum; start at Notre Dame Cathedral.
3. Run nearest neighbor and read its actual visiting order and cost `13.57`.
4. Show Exact Brute Force cost `11.22` and the displayed `20.88%` gap.
5. Explain that nearest neighbor is approximate, while exact brute force checks
   all orders for small waypoint sets and is optimal for the pairwise problem.
6. Briefly show fixed-end and return-to-start controls.

## 6. Traffic and objective scenarios - 1 minute

- Switch between balanced, fastest, shortest, low congestion, and low risk.
- Use Ben Thanh Market to Independence Palace and compare normal with rainy.
- Point out that the rainy scenario changes the selected road sequence, while
  rush hour raises time/cost even where the route remains the same.
- Explain that these settings change edge costs while every algorithm receives
  the same graph and scenario during a comparison.

## 7. Engineering evidence - 30 seconds

- Open `http://127.0.0.1:8000/docs` and show the REST/WebSocket-facing API.
- State that 70 backend tests pass and the frontend production build succeeds.
- Mention the main limitations: simulated traffic and one transparent boundary
  connector between separately clipped OSM extracts.

## 8. Closing - 20 seconds

Summarize the result: six comparable search algorithms, a real OSM-derived
traffic graph, multi-location optimization, live animation, and an end-to-end
tested web application.
