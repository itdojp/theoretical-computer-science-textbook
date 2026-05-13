# markdownlint baseline policy

This repository contains Japanese textbook manuscripts under `src/` and a synchronized GitHub Pages mirror under `docs/`. As of 2026-05-14, a full default markdownlint pass reports a large pre-existing baseline dominated by formatting preferences rather than parser-critical defects.

## Current measured baseline

`npm run lint` with the former default-style configuration reported 1,615 findings. The largest categories were:

| Rule | Count | Baseline treatment |
| --- | ---: | --- |
| MD032 blanks-around-lists | 765 | Defer; requires broad manuscript reflow. |
| MD022 blanks-around-headings | 183 | Defer; requires broad manuscript reflow. |
| MD030 list-marker-space | 148 | Defer; should be handled with list normalization. |
| MD013 line-length | 144 | Defer; Japanese prose, math, Liquid links, and tables need book-specific wrapping policy. |
| MD029 ol-prefix | 120 | Defer; requires ordered-list renumbering decisions. |
| MD004 ul-style | 92 | Defer; requires bullet-style normalization. |
| MD031 blanks-around-fences | 75 | Defer; should be handled with code-block normalization. |
| MD025 single-title | 34 | Defer; Jekyll front matter and page H1 conventions need an explicit rule decision. |

## Active lint gate

The active `.markdownlint.json` intentionally keeps the lint gate focused on high-signal syntax and reference risks:

- MD009 trailing spaces
- MD010 hard tabs
- MD011 reversed link syntax
- MD012 multiple blank lines
- MD037 spaces inside emphasis markers
- MD052 undefined reference-style links/images
- MD046 fenced code block style

This keeps `npm run lint` useful while avoiding a high-churn reflow of the manuscript. Deferred style categories should be reduced by small, chapter- or rule-scoped PRs.


## Explicitly unenforced legacy rules

The former configuration already disabled several rules. They remain outside the active gate unless a later PR gives them a book-specific policy:

- MD033 inline HTML: used by Jekyll/Liquid-facing manuscript pages.
- MD034 bare URLs: external-source notes and generated references need a link-format policy before enforcement.
- MD036 emphasis as heading: the manuscript uses bold labels for theorem/proof blocks.
- MD041 first-line H1: Jekyll front matter precedes page headings.

## Follow-up policy

When reducing the deferred baseline, prefer one of these scopes per PR:

1. one rule across a small set of files;
2. one chapter or appendix across a small set of rules;
3. generated/mechanical changes only when the diff remains reviewable.

Every manuscript edit must keep `src/` and `docs/` mirrors synchronized.
