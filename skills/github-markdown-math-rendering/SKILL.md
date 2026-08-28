---
name: github-markdown-math-rendering
description: Use when writing or editing LaTeX/KaTeX math ($...$ or $$...$$) in a Markdown file meant to be viewed on github.com (README, docs, PR/issue body) — especially when math renders fine in a local KaTeX/MathJax check or via `gh api /markdown` but still shows literal text, garbles, or throws "Extra open brace or missing close brace" on the actual github.com page.
---

# GitHub Markdown Math Rendering

## Overview

GitHub renders math in repo files (blob view) with **MathJax**, not KaTeX —
and its client-side rendering path has quirks that neither a local
KaTeX/MathJax check nor GitHub's own `/markdown` API reproduce. Formulas
that "parse fine everywhere else" can still silently fail or render garbled
only on the live github.com page. Treat local/API validation as necessary
but not sufficient.

## When to Use

- Adding `$...$` / `$$...$$` math to a README, docs page, or example that
  will be viewed as a rendered `.md` file on github.com.
- A formula renders in a KaTeX playground / mathjax-full / `gh api
  /markdown` but not on the actual repository page.
- Symptoms: inline math shown as raw `$...$` text with no rendering; a
  `\begin{aligned}` block throwing "Extra open brace or missing close
  brace"; braces, `;`, or `,` vanishing from the rendered formula; the tail
  of a formula silently missing (a `\%` swallowed as a comment marker); a
  sum/product with a `<`/`>` in the subscript rendering broken or not at all.

## The Four Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `$...$` shown as literal text, no error | GitHub only recognizes an opening `$` when preceded by start-of-line, whitespace, or `(`. Any other preceding character — including full-width/CJK punctuation like `（`, `、`, `。`, `「` — leaves it untouched. | Insert a space before the `$` (`価格は $x$` not `価格は$x$`). |
| `\{`, `\}`, `\;`, `\,`, `\%` (any `\<ASCII punctuation>`) silently lose their backslash | CommonMark's backslash-escape rule strips the backslash off any `\<ASCII punctuation>` in ordinary text *before* it reaches the math renderer. `\{`/`\}` arrive as bare `{}` (an empty group, not a literal brace); `\;`/`\,` (spacing commands) arrive as bare `;`/`,` (stray punctuation instead of a space); **`\%` arrives as a bare `%`, which MathJax/TeX treats as a comment marker — everything after it on that line is silently dropped, breaking the rest of the formula, not just the percent sign.** `\\` is unaffected — this is not a blanket problem, only single-punctuation escapes. | Use `\lbrace` / `\rbrace` instead of `\{` / `\}`. Drop `\;`/`\,` spacing (it becomes pointless anyway — a plain space or nothing works fine). Never write a literal `%` inside `$...$` math — move percentages outside math mode as plain text (`理論値25%` not `$25\%$`), or use a decimal (`0.25`) inside math instead. |
| `\begin{aligned}...\end{aligned}` throws "Extra open brace or missing close brace" only in repo files | This align environment is broken specifically in GitHub's **blob-rendered** `.md` files (it works fine in issue/PR comments), even though it parses correctly under vanilla KaTeX/MathJax locally — see mathjax/MathJax#2274. | Don't use `\begin{aligned}`/`\begin{align}` in repo markdown. Write the formula as a single line without `\\` line breaks. |
| `\sum_{i<j}` (or any bare `<`/`>` inside math) breaks only on the live github.com page | A literal `<`/`>` inside math breaks GitHub's actual client-side MathJax rendering, despite parsing fine under standalone mathjax-full/KaTeX *and* the generic `/markdown` API — this is specific to GitHub's client-side rendering path, not a general MathJax/KaTeX bug. | Use `\lt` / `\gt` instead of the literal character: `\sum_{i \lt j}`. |

## Example

Bad — breaks on github.com despite looking correct and passing local/API checks:

```
価格は$\sqrt{2}$倍になる。
目的関数: $\sum_{i<j} x_i x_j$
集合: $\{a, b\}$、区切りは\;を使う。
$$
\begin{aligned}
H &= \sum_i c_i x_i \\
  &+ \sum_{i<j} J_{ij} x_i x_j
\end{aligned}
$$
```

Good — renders correctly on the actual github.com blob view:

```
価格は $\sqrt{2}$ 倍になる。
目的関数: $\sum_{i \lt j} x_i x_j$
集合: $\lbrace a, b \rbrace$。
$$
H = \sum_i c_i x_i + \sum_{i \lt j} J_{ij} x_i x_j
$$
```

## How to Verify

Local KaTeX, mathjax-full, and `gh api /markdown` all fail to reproduce at
least one of these bugs (the `<`-in-subscript bug in particular passes all
three). The only reliable check is loading the actual rendered file on
github.com.

To debug a suspected rendering break:
1. Put each suspect formula in its own isolated fragment in one file (a
   heading + one formula per section) so failures can be attributed to a
   specific fragment.
2. Push and view the file live on github.com (not the API, not a local
   preview).
3. Bisect: the fragments that fail to render (or throw a parse error)
   pinpoint the offending construct — cross-check it against the table
   above.
4. Delete the debug file once the cause is confirmed; don't leave
   scratch/debug files committed.

## Common Mistakes

- Trusting a local KaTeX/MathJax render or `gh api /markdown` as proof the
  formula is fine on GitHub — none of them fully reproduce github.com's
  blob-view rendering path.
- Assuming a parse error like "Extra open brace or missing close brace"
  means broken LaTeX syntax, when it can instead mean an environment
  (`\begin{aligned}`) that's simply unsupported in that render context.
- Escaping braces/semicolons with `\{`, `\}`, `\;` in running Markdown text
  and assuming the backslash survives to the math renderer.
