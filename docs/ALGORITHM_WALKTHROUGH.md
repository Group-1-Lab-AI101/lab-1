# Group-designed Algorithm Walkthrough

Use this example in the presentation and video. It was designed for this
project and is also represented by automated test fixtures.

## Example graph

```text
             cost 8          cost 1
        A ----------> B ------------> G
        |
        | cost 1
        v
        C ----------> D ------------> G
             cost 1          cost 1
```

Adjacency order at `A` is `B` then `C`. Heuristic values to `G` are:

| Node | A | B | C | D | G |
| --- | ---: | ---: | ---: | ---: | ---: |
| `h(n)` | 2 | 0 | 2 | 1 | 0 |

Two competing routes exist:

- `A -> B -> G`: 2 edges, total cost 9.
- `A -> C -> D -> G`: 3 edges, total cost 3.

## BFS

| Step | Pop | Frontier after generation | Note |
| ---: | --- | --- | --- |
| 1 | A | B, C | Discover both depth-1 nodes |
| 2 | B | C, G | G first receives parent B |
| 3 | C | G, D | G is already discovered |
| 4 | G | D | Stop |

Result: `A -> B -> G`, cost 9. BFS is optimal by edge count, not traffic cost.

## DFS

With adjacency order `B` then `C`, the stack explores `B` first.

| Step | Pop | Stack | Note |
| ---: | --- | --- | --- |
| 1 | A | C, B | B is next |
| 2 | B | C, G | Continue deepest branch |
| 3 | G | C | Stop |

Result: `A -> B -> G`, cost 9. DFS has no route-quality guarantee.

## Uniform Cost Search

| Step | Pop with `g` | Priority frontier | Action |
| ---: | --- | --- | --- |
| 1 | A, 0 | C:1, B:8 | Relax B and C |
| 2 | C, 1 | D:2, B:8 | Relax D |
| 3 | D, 2 | G:3, B:8 | Relax G |
| 4 | G, 3 | B:8 | Stop when best-cost goal is popped |

Result: `A -> C -> D -> G`, cost 3, optimal.

## A* Search

A* uses `f(n) = g(n) + h(n)`.

| Step | Pop | `g` | `h` | `f` | Resulting frontier |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | A | 0 | 2 | 2 | C `(1+2=3)`, B `(8+0=8)` |
| 2 | C | 1 | 2 | 3 | D `(2+1=3)`, B `(8)` |
| 3 | D | 2 | 1 | 3 | G `(3+0=3)`, B `(8)` |
| 4 | G | 3 | 0 | 3 | Stop |

Result: `A -> C -> D -> G`, cost 3. The admissible heuristic preserves
optimality and guides expansion.

## Dijkstra

For one destination, Dijkstra expands the same cost order as UCS in this graph:
`A(0), C(1), D(2), G(3)`. The project distinguishes its role by exposing a
single-source helper that reuses one run for many pairwise multi-location paths.

Result: `A -> C -> D -> G`, cost 3, optimal.

## Greedy Best-First Search

Greedy ranks only by `h(n)`.

| Step | Pop | Heuristic frontier | Action |
| ---: | --- | --- | --- |
| 1 | A | B:0, C:2 | Choose B because its heuristic is smallest |
| 2 | B | G:0, C:2 | Generate G |
| 3 | G | C:2 | Stop |

Result: `A -> B -> G`, cost 9. Greedy finds a route quickly but misses the
cost-3 route because it ignores accumulated cost when ordering the frontier.

## Video checklist

For each algorithm, show the initial state, goal, expansion order, frontier,
parent updates, and final path. For UCS/Dijkstra/A*, read the displayed cost
values. For A*/Greedy, read the heuristic values. End by comparing the two
possible routes and the guarantee of each algorithm.
