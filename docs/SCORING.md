# Content Scoring Model

This document defines the logic for the Content Score (0-100), ensuring it behaves logically and predictably.

## Core Principles

1.  **Monotonicity**: Adding relevant content (terms, useful length) should never decrease the score (unless over-optimized).
2.  **Stability**: Deleting relevant content should never increase the score.
3.  **Smoothness**: No abrupt jumps (e.g., from 1.0 to 0.0) when crossing thresholds.

## Score Breakdown (Total: 100)

| Component | Weight | Description |
| :--- | :--- | :--- |
| **Term Coverage** | **60** | Usage of recommended keywords (NLP terms). |
| **Structure** | **20** | Word count, paragraphs, images. |
| **Headings** | **20** | Hierarchy (H1, H2, H3) and terms in headings. |

---

## 1. Term Coverage (60 points)

For each term, we calculate a `term_score` (0.0 to 1.0). The final component score is the average of all `term_scores` multiplied by 60.

### Formula per Term

Let $C$ be the current count, $Min$ be recommended minimum, $Max$ be recommended maximum.

1.  **Under-optimized** ($C < Min$):
    $$ Score = \frac{C}{Min} $$
    *(Linear growth from 0 to 1.0)*

2.  **Optimal** ($Min \le C \le Max$):
    $$ Score = 1.0 $$
    *(Perfect score)*

3.  **Slightly Over-optimized** ($Max < C \le Max \times 1.5$):
    $$ Score = 1.0 - 0.5 \times \frac{C - Max}{Max \times 0.5} $$
    *(Linear decay from 1.0 to 0.5)*

4.  **Heavily Over-optimized** ($C > Max \times 1.5$):
    $$ Score = 0.5 \times \frac{Max \times 1.5}{C} $$
    *(Hyperbolic decay towards 0, never abrupt 0)*

**Why this fixes the bug:**
Previously, exceeding the limit caused a jump to 0.0. Now, it decays smoothly. Deleting a term when heavily over-optimized will increase the score (correct behavior), but deleting a term when optimal or under-optimized will decrease or maintain the score.

---

## 2. Structure (20 points)

### Word Count (10 points)
*   $C < Min$: $\frac{C}{Min} \times 10$
*   $Min \le C \le Max$: $10$
*   $C > Max$: $10$ (No penalty for extra length, unless extreme - TBD)

### Images (5 points)
*   $C < Min$: $\frac{C}{Min} \times 5$
*   $Min \le C \le Max$: $5$
*   $C > Max$: $5$ (No penalty)

### Paragraphs (5 points)
*   Based on density (approx 1 paragraph per 100 words).
*   Too few paragraphs (wall of text) = penalty.
*   Too many = no penalty.

---

## 3. Headings (20 points)

*   **H1 Presence** (5 points): 5 if H1 exists, 0 otherwise.
*   **H2/H3 Count** (10 points):
    *   $C < Min$: $\frac{C}{Min} \times 10$
    *   $Min \le C \le Max$: $10$
    *   $C > Max$: $10$
*   **Terms in Headings** (5 points):
    *   Bonus for using keywords in H1/H2/H3.

---

## Implementation Notes

*   **Normalization**: Ensure terms list is not empty. If empty, score is 0.
*   **Caching**: Frontend should update immediately on input (debounced), backend should be stateless regarding score calculation (always recalculate based on full text).
